from __future__ import annotations

import os
import tempfile
import wave
from collections.abc import Iterator
from uuid import uuid4

import psycopg
import pytest
from packages.shared.storage.s3_client import S3ObjectStorageClient


@pytest.fixture(scope="session")
def database_url() -> str:
    # align with other integration tests
    return os.getenv(
        "DATABASE_URL",
        "postgresql://narralytica:narralytica@127.0.0.1:15432/narralytica",
    )


@pytest.fixture(scope="session")
def storage() -> S3ObjectStorageClient:
    endpoint = os.getenv("S3_ENDPOINT", "http://127.0.0.1:19000")
    access_key = os.getenv("S3_ACCESS_KEY", "minioadmin")
    secret_key = os.getenv("S3_SECRET_KEY", "minioadmin")
    return S3ObjectStorageClient(
        endpoint_url=endpoint,
        access_key=access_key,
        secret_key=secret_key,
    )


@pytest.fixture()
def ids() -> dict[str, str]:
    video_id = f"video_it_{uuid4().hex[:12]}"
    job_id = f"job_it_{uuid4().hex[:12]}"
    return {"video_id": video_id, "job_id": job_id}


@pytest.fixture()
def temp_wav_path() -> Iterator[str]:
    # Generate a tiny deterministic WAV (mono, 16-bit, 16kHz)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        path = f.name

    framerate = 16000
    duration_s = 1.3
    nframes = int(framerate * duration_s)

    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(framerate)
        # Write silence
        wf.writeframes(b"\x00\x00" * nframes)

    try:
        yield path
    finally:
        try:
            os.remove(path)
        except OSError:
            pass


def _exec(database_url: str, sql: str, params: dict) -> None:
    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
        conn.commit()


@pytest.fixture()
def seed_video_row(database_url: str, ids: dict[str, str]) -> None:
    # Minimal row for FK constraint transcripts.video_id → videos.id
    # Adjust columns only if your videos table differs.
    _exec(
        database_url,
        """
        INSERT INTO public.videos (id, created_at, updated_at)
        VALUES (%(id)s, now(), now())
        ON CONFLICT (id) DO NOTHING
        """,
        {"id": ids["video_id"]},
    )
