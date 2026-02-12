from __future__ import annotations

import os
import sys
import wave
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

import psycopg
import pytest

# Ensure transcribe/src is importable (worker runtime uses "from worker import ...").
HERE = Path(__file__).resolve()
TRANSCRIBE_SRC = HERE.parents[2] / "src"  # .../services/workers/transcribe/src
if str(TRANSCRIBE_SRC) not in sys.path:
    sys.path.insert(0, str(TRANSCRIBE_SRC))

import asr.runner as asr_runner  # noqa: E402
import worker as transcribe_worker  # noqa: E402
from packages.shared.storage.s3_client import S3ObjectStorageClient  # noqa: E402


@dataclass(frozen=True)
class _Seg:
    start_s: float
    end_s: float
    text: str


@dataclass(frozen=True)
class _Res:
    text: str
    language: str | None
    segments: list[_Seg]
    raw: dict


class FakeAsrProvider:
    name = "fake"

    def transcribe(self, *, audio_path: str) -> _Res:
        _ = audio_path
        segments = [
            _Seg(start_s=0.0, end_s=0.6, text="Bonjour"),
            _Seg(start_s=0.6, end_s=1.2, text="le monde"),
        ]
        return _Res(
            text="Bonjour le monde",
            language=None,  # Force worker language fallback path.
            segments=segments,
            raw={"provider": "fake", "note": "deterministic test provider"},
        )


@pytest.mark.integration
def test_transcribe_flow_end_to_end(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://narralytica:narralytica@127.0.0.1:15432/narralytica",
    )
    os.environ["DATABASE_URL"] = database_url

    # Avoid subprocess path in asr.runner for faster_whisper.
    os.environ["TRANSCRIBE_ATTEMPT_TIMEOUT_S"] = "0"
    os.environ["TRANSCRIBE_JOB_TIMEOUT_S"] = "60"

    endpoint = os.getenv("S3_ENDPOINT", "http://127.0.0.1:19000")
    access_key = os.getenv("S3_ACCESS_KEY", "minioadmin")
    secret_key = os.getenv("S3_SECRET_KEY", "minioadmin")

    storage = S3ObjectStorageClient(
        endpoint_url=endpoint,
        access_key=access_key,
        secret_key=secret_key,
    )

    audio_bucket = os.getenv("AUDIO_BUCKET", "audio-tracks")
    transcripts_bucket = os.getenv("TRANSCRIPTS_BUCKET", "transcripts")

    video_id = f"video_it_{uuid4().hex[:12]}"
    job_id = f"job_it_{uuid4().hex[:12]}"

    # --- make tiny wav ---
    wav_path = tmp_path / "audio.wav"
    framerate = 16000
    duration_s = 1.3
    nframes = int(framerate * duration_s)

    with wave.open(str(wav_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(framerate)
        wf.writeframes(b"\x00\x00" * nframes)

    audio_key = f"videos/{video_id}/audio.wav"
    storage.upload_bytes(
        audio_bucket,
        audio_key,
        wav_path.read_bytes(),
        "audio/wav",
    )

    payload = {
        # Must match audio_fetch.resolve_audio_ref():
        # - audio_storage_ref
        # - or artifacts.audio
        "audio_storage_ref": {"bucket": audio_bucket, "key": audio_key},
    }

    # --- seed DB minimal video row (FK required by transcripts.video_id) ---
    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO public.videos (id, source_type, source_uri, metadata)
                VALUES (%(id)s, %(source_type)s, %(source_uri)s, '{}'::jsonb)
                ON CONFLICT (id) DO NOTHING
                """,
                {
                    "id": video_id,
                    "source_type": "test",
                    "source_uri": f"test://{video_id}",
                },
            )
        conn.commit()

    # --- force deterministic provider everywhere it is used ---
    monkeypatch.setattr(transcribe_worker, "get_provider", lambda: FakeAsrProvider())
    monkeypatch.setattr(asr_runner, "get_provider", lambda: FakeAsrProvider())

    # --- run worker on this job ---
    transcribe_worker._run_asr(  # noqa: SLF001
        {"id": job_id, "video_id": video_id, "payload": payload}
    )

    # --- artifact exists ---
    artifact_key = f"transcripts/{video_id}/{job_id}/transcript.v1.json"
    stat = storage.stat_object(transcripts_bucket, artifact_key)
    assert stat.get("size_bytes", 0) > 0

    # --- transcript row exists + is coherent ---
    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                  video_id,
                  provider,
                  language,
                  status,
                  artifact_bucket,
                  artifact_key,
                  duration_seconds,
                  storage_ref,
                  metadata
                FROM public.transcripts
                WHERE video_id = %(video_id)s AND artifact_key = %(artifact_key)s
                """,
                {"video_id": video_id, "artifact_key": artifact_key},
            )
            row = cur.fetchone()

    assert row is not None
    (
        db_video_id,
        db_provider,
        db_language,
        db_status,
        db_artifact_bucket,
        db_artifact_key,
        db_duration_seconds,
        db_storage_ref,
        db_metadata,
    ) = row

    assert db_video_id == video_id
    assert db_status == "completed"
    assert db_artifact_bucket == transcripts_bucket
    assert db_artifact_key == artifact_key
    assert db_provider in ("fake", "faster_whisper")

    assert isinstance(db_language, str)
    assert db_language

    assert isinstance(db_duration_seconds, float | int)
    assert float(db_duration_seconds) > 0.0

    assert db_storage_ref is None or isinstance(db_storage_ref, dict)
    assert isinstance(db_metadata, dict)

    assert "segments" in db_metadata
    assert isinstance(db_metadata["segments"], list)
    assert db_metadata["segments"]
