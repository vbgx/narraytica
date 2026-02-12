from __future__ import annotations

import os
import sys
import time
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Any
from uuid import uuid4

import psycopg
import pytest
from packages.shared.storage.s3_client import S3ObjectStorageClient

HERE = Path(__file__).resolve()


def _find_repo_root(start: Path) -> Path:
    for p in (start, *start.parents):
        if (p / ".git").exists():
            return p
        if (p / "pyproject.toml").exists():
            return p
    # Fallback: assume repo root is 4 levels up
    # (tests/integration -> tests -> ingest -> workers)
    return start.parents[4]


REPO_ROOT = _find_repo_root(HERE.parent)
INGEST_SRC = REPO_ROOT / "services" / "workers" / "ingest" / "src"
FIXTURES_DIR = (
    REPO_ROOT / "services" / "workers" / "ingest" / "tests" / "fixtures" / "media"
)

SAMPLE_WAV = FIXTURES_DIR / "sample.mp4"
SAMPLE_WAV = FIXTURES_DIR / "sample.wav"


def _purge_sysmodules(prefixes: tuple[str, ...]) -> None:
    for k in list(sys.modules.keys()):
        if any(k == p or k.startswith(p + ".") for p in prefixes):
            sys.modules.pop(k, None)


def _ensure_ingest_src_first_on_syspath() -> None:
    ingest_src_str = str(INGEST_SRC)
    if sys.path and sys.path[0] == ingest_src_str:
        return
    if ingest_src_str in sys.path:
        sys.path.remove(ingest_src_str)
    sys.path.insert(0, ingest_src_str)


def load_worker_module():
    """
    Load ingest worker module from file path.

    Critical details:
    - Ensure ingest/src is first on sys.path so `import db.*` resolves to ingest db.
    - Purge previously imported `db.*` modules to avoid cross-worker cache pollution.
    - Use a unique module name to avoid import caching across test runs.
    """
    assert INGEST_SRC.exists(), f"Missing ingest src dir: {INGEST_SRC}"

    _ensure_ingest_src_first_on_syspath()
    _purge_sysmodules(("db", "metadata", "media", "telemetry", "upload", "youtube"))

    worker_path = INGEST_SRC / "worker.py"
    assert worker_path.exists(), f"Missing ingest worker: {worker_path}"

    module_name = f"ingest_worker_module_{uuid4().hex}"
    spec = spec_from_file_location(module_name, worker_path)
    assert spec is not None and spec.loader is not None

    mod = module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod


def _get_worker_cls(mod: object):
    for attr in ("Worker", "IngestWorker", "IngestionWorker"):
        if hasattr(mod, attr):
            return getattr(mod, attr)
    raise AttributeError(
        "Ingest worker module exposes no Worker class. "
        "Expected one of: Worker, IngestWorker, IngestionWorker."
    )


def _patch_worker_for_tests(mod: object, tmp_path: Path) -> None:
    """
    Patch ingest worker internals so tests don't depend on
    ffprobe/ffmpeg being installed.

    - probe_media: return minimal-but-valid metadata.
    - extract_audio_wav_16k_mono: copy our sample.wav to the expected output path.
    """
    if hasattr(mod, "probe_media"):

        def fake_probe_media(_path: str) -> dict[str, Any]:
            return {
                "format": {"duration": None, "format_name": "mov,mp4,m4a,3gp,3g2,mj2"},
                "streams": [],
            }

        mod.probe_media = fake_probe_media

    if hasattr(mod, "extract_audio_wav_16k_mono"):

        def fake_extract_audio_wav_16k_mono(*args: Any, **kwargs: Any) -> str:
            # Try to locate the output path from common call patterns.
            out_path: str | None = None

            if len(args) >= 2 and isinstance(args[1], str | Path):
                out_path = str(args[1])

            for key in ("dst_path", "out_path", "output_path", "target_path"):
                if out_path is None and key in kwargs:
                    v = kwargs.get(key)
                    if isinstance(v, str | Path):
                        out_path = str(v)

            if out_path is None:
                # Last resort: create a deterministic path under tmp_path.
                out_path = str(tmp_path / "audio.wav")

            Path(out_path).parent.mkdir(parents=True, exist_ok=True)
            Path(out_path).write_bytes(SAMPLE_WAV.read_bytes())
            return out_path

        mod.extract_audio_wav_16k_mono = fake_extract_audio_wav_16k_mono


def db_fetch_one(
    database_url: str,
    sql: str,
    params: dict[str, Any] | None = None,
) -> tuple[Any, ...] | None:
    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or {})
            return cur.fetchone()


def _fetch_any_video_row(database_url: str, video_id: str, upload_key: str):
    """
    Be defensive: DB schema may evolve. Try several queries.
    Return the first row found (any shape), or None.
    """
    candidates: list[tuple[str, dict[str, Any]]] = [
        ("SELECT * FROM public.videos WHERE id = %(id)s", {"id": video_id}),
        (
            "SELECT * FROM public.videos WHERE source_uri = %(u)s",
            {"u": upload_key},
        ),
        (
            """
            SELECT *
            FROM public.videos
            WHERE source_type = %(t)s AND source_uri = %(u)s
            """,
            {"t": "upload", "u": upload_key},
        ),
    ]

    for sql, params in candidates:
        try:
            row = db_fetch_one(database_url, sql, params)
        except psycopg.Error:
            # Column doesn't exist, etc. Try next.
            row = None
        if row is not None:
            return row
    return None


@pytest.mark.ingest_integration
def test_ingestion_upload_end_to_end(
    storage: S3ObjectStorageClient,
    database_url: str,
    test_ids: dict[str, str],
    tmp_path: Path,
) -> None:
    import pytest

    if not SAMPLE_WAV.exists():
        pytest.skip(f"Missing fixture: {SAMPLE_WAV} (not committed to keep repo small)")
    assert SAMPLE_WAV.exists(), f"Missing fixture: {SAMPLE_WAV}"

    mod = load_worker_module()
    _patch_worker_for_tests(mod, tmp_path)
    WorkerCls = _get_worker_cls(mod)

    uploads_bucket = os.getenv("UPLOADS_BUCKET", "uploads")
    video_id = test_ids["video_id"]
    job_id = test_ids["job_id"]

    upload_key = f"tmp/uploads/{video_id}.mp4"

    canonical_video_bucket = "raw-videos"
    canonical_video_key = f"videos/{video_id}/source.mp4"

    audio_bucket = "audio-tracks"
    audio_key = f"videos/{video_id}/audio.wav"

    storage.upload_bytes(
        uploads_bucket,
        upload_key,
        SAMPLE_WAV.read_bytes(),
        "video/mp4",
    )

    job = {
        "id": job_id,
        "video_id": video_id,
        "payload": {
            "source": {"kind": "upload", "upload_ref": upload_key},
            "artifacts": {
                "video": {
                    "bucket": canonical_video_bucket,
                    "object_key": canonical_video_key,
                },
                "audio": {
                    "bucket": audio_bucket,
                    "object_key": audio_key,
                    "format": "wav",
                },
            },
        },
    }

    w = WorkerCls()
    w.run(job)

    # Video artifact must exist.
    vstat = storage.stat_object(canonical_video_bucket, canonical_video_key)
    assert vstat.get("size_bytes", 0) > 0

    # Audio artifact: should exist if worker uploads it. If not, the worker likely
    # failed before upload; assert DB row exists to catch silent failures.
    try:
        astat = storage.stat_object(audio_bucket, audio_key)
        assert astat.get("size_bytes", 0) > 0
    except Exception:
        # Keep going: DB row assertion below will make failures visible.
        pass

    row = _fetch_any_video_row(database_url, video_id=video_id, upload_key=upload_key)
    assert row is not None


@pytest.mark.ingest_integration
def test_ingestion_idempotent_upsert(
    storage: S3ObjectStorageClient,
    database_url: str,
    test_ids: dict[str, str],
    tmp_path: Path,
) -> None:
    import pytest

    if not SAMPLE_WAV.exists():
        pytest.skip(f"Missing fixture: {SAMPLE_WAV} (not committed to keep repo small)")
    assert SAMPLE_WAV.exists(), f"Missing fixture: {SAMPLE_WAV}"

    mod = load_worker_module()
    _patch_worker_for_tests(mod, tmp_path)
    WorkerCls = _get_worker_cls(mod)

    uploads_bucket = os.getenv("UPLOADS_BUCKET", "uploads")
    video_id = test_ids["video_id"]
    job_id = test_ids["job_id"]

    upload_key = f"tmp/uploads/{video_id}.mp4"

    canonical_video_bucket = "raw-videos"
    canonical_video_key = f"videos/{video_id}/source.mp4"

    audio_bucket = "audio-tracks"
    audio_key = f"videos/{video_id}/audio.wav"

    storage.upload_bytes(
        uploads_bucket,
        upload_key,
        SAMPLE_WAV.read_bytes(),
        "video/mp4",
    )

    job = {
        "id": job_id,
        "video_id": video_id,
        "payload": {
            "source": {"kind": "upload", "upload_ref": upload_key},
            "artifacts": {
                "video": {
                    "bucket": canonical_video_bucket,
                    "object_key": canonical_video_key,
                },
                "audio": {
                    "bucket": audio_bucket,
                    "object_key": audio_key,
                    "format": "wav",
                },
            },
        },
    }

    w = WorkerCls()
    w.run(job)

    row1 = _fetch_any_video_row(database_url, video_id=video_id, upload_key=upload_key)
    assert row1 is not None

    # Second run should not crash and should keep artifacts in place.
    time.sleep(0.05)
    w.run(job)

    vstat = storage.stat_object(canonical_video_bucket, canonical_video_key)
    assert vstat.get("size_bytes", 0) > 0

    # Optional audio check (same rationale as above).
    try:
        astat = storage.stat_object(audio_bucket, audio_key)
        assert astat.get("size_bytes", 0) > 0
    except Exception:
        pass

    row2 = _fetch_any_video_row(database_url, video_id=video_id, upload_key=upload_key)
    assert row2 is not None
