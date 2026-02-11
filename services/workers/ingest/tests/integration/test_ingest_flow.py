import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any

import psycopg
import pytest


def _ensure_sys_path(repo_root: str) -> None:
    """
    We load the worker via file path, but its internal imports expect top-level
    modules like:

      - domain.*
      - media.*
      - metadata.*
      - db.*
      - upload.*
      - youtube.*
      - telemetry.*
      - packages.*

    Therefore we add BOTH:
      - repo root (for packages.*)
      - ingest src (for domain/media/metadata/db/upload/youtube/telemetry)
    """
    ingest_src = Path(repo_root) / "services" / "workers" / "ingest" / "src"

    for p in (str(ingest_src), repo_root):
        if p not in sys.path:
            sys.path.insert(0, p)


def load_worker(repo_root: str):
    worker_path = (
        Path(repo_root) / "services" / "workers" / "ingest" / "src" / "worker.py"
    )
    spec = importlib.util.spec_from_file_location(
        "narralytica_ingest_worker", worker_path
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot_load_worker: {worker_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.IngestWorker


def db_fetch_one(database_url: str, sql: str, params: dict[str, Any]):
    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchone()


@pytest.mark.integration
def test_ingestion_upload_end_to_end(storage, database_url, test_ids, temp_mp4):
    repo_root = os.getcwd()
    _ensure_sys_path(repo_root)

    IngestWorker = load_worker(repo_root)

    uploads_bucket = os.getenv("UPLOADS_BUCKET", "uploads")
    video_id = test_ids["video_id"]
    job_id = test_ids["job_id"]

    upload_key = f"tmp/uploads/{video_id}.mp4"
    canonical_video_bucket = "raw-videos"
    canonical_video_key = f"videos/{video_id}/source.mp4"
    audio_bucket = "audio-tracks"
    audio_key = f"videos/{video_id}/audio.wav"

    with open(temp_mp4, "rb") as f:
        storage.upload_bytes(uploads_bucket, upload_key, f.read(), "video/mp4")

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

    IngestWorker().run(job)

    vstat = storage.stat_object(canonical_video_bucket, canonical_video_key)
    astat = storage.stat_object(audio_bucket, audio_key)
    assert vstat.get("size_bytes", 0) > 0
    assert astat.get("size_bytes", 0) > 0

    row = db_fetch_one(
        database_url,
        """
        SELECT source_platform, duration_seconds, container_format,
               raw_video_bucket, raw_video_object_key,
               audio_bucket, audio_object_key, metadata_json
        FROM public.videos
        WHERE id = %(id)s
        """,
        {"id": video_id},
    )
    assert row is not None

    source_platform, duration_seconds, container_format, rvb, rvk, ab, ak, meta = row
    assert source_platform in ("upload", "youtube", "unknown")
    assert rvb == canonical_video_bucket
    assert rvk == canonical_video_key
    assert ab == audio_bucket
    assert ak == audio_key
    assert duration_seconds is None or duration_seconds > 0
    assert container_format is None or isinstance(container_format, str)

    if isinstance(meta, str):
        meta = json.loads(meta)
    assert isinstance(meta, dict)


@pytest.mark.integration
def test_ingestion_idempotent_upsert(storage, database_url, test_ids, temp_mp4):
    repo_root = os.getcwd()
    _ensure_sys_path(repo_root)

    IngestWorker = load_worker(repo_root)

    uploads_bucket = os.getenv("UPLOADS_BUCKET", "uploads")
    video_id = test_ids["video_id"]
    job_id = test_ids["job_id"]

    upload_key = f"tmp/uploads/{video_id}.mp4"
    canonical_video_bucket = "raw-videos"
    canonical_video_key = f"videos/{video_id}/source.mp4"
    audio_bucket = "audio-tracks"
    audio_key = f"videos/{video_id}/audio.wav"

    with open(temp_mp4, "rb") as f:
        storage.upload_bytes(uploads_bucket, upload_key, f.read(), "video/mp4")

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

    w = IngestWorker()
    w.run(job)

    before = db_fetch_one(
        database_url,
        "SELECT updated_at FROM public.videos WHERE id=%(id)s",
        {"id": video_id},
    )[0]

    w.run(job)

    after = db_fetch_one(
        database_url,
        "SELECT updated_at FROM public.videos WHERE id=%(id)s",
        {"id": video_id},
    )[0]

    assert str(after) != str(before)

    count = db_fetch_one(
        database_url,
        "SELECT COUNT(*) FROM public.videos WHERE id=%(id)s",
        {"id": video_id},
    )[0]
    assert count == 1
