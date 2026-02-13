from __future__ import annotations

import os
import uuid
from typing import Any

from packages.persistence.postgres.db import connection
from packages.persistence.postgres.errors import Conflict
from packages.persistence.postgres.repos.jobs_repo import JobsRepo
from packages.persistence.postgres.repos.videos_repo import VideosRepo

JsonObj = dict[str, Any]


def get_db_conn():
    """
    Drop-in replacement for services/workers/ingest/src/db/postgres.py:get_db_conn.

    Integration tests set POSTGRES_DSN (or equivalent). We keep that contract.
    """
    dsn = os.environ.get("POSTGRES_DSN")
    if not dsn:
        raise RuntimeError("POSTGRES_DSN is required")
    return connection(dsn)


def persist_video_metadata(
    *,
    video_id: str | None = None,
    source_type: str | None = None,
    source_uri: str | None = None,
    duration_ms: int | None = None,
    storage_bucket: str | None = None,
    storage_key: str | None = None,
    metadata: dict[str, Any] | None = None,
    source: dict[str, Any] | None = None,
    artifacts: dict[str, Any] | None = None,
) -> str:
    if not source_type or not source_uri:
        if isinstance(source, dict):
            kind = source.get("kind")
            if kind:
                source_type = source_type or str(kind)
            if kind == "upload" and source.get("upload_ref"):
                source_uri = source_uri or str(source["upload_ref"])
            if kind == "youtube" and source.get("url"):
                source_uri = source_uri or str(source["url"])

    if isinstance(artifacts, dict) and (not storage_bucket or not storage_key):
        v = artifacts.get("video")
        if isinstance(v, dict):
            storage_bucket = storage_bucket or v.get("bucket")
            storage_key = storage_key or v.get("object_key") or v.get("key")

    if not source_type or not source_uri:
        raise ValueError("persist_video_metadata: missing source_type/source_uri")

    md = dict(metadata or {})
    if duration_ms is None:
        if md.get("duration_ms") is not None:
            try:
                duration_ms = int(md["duration_ms"])
            except Exception:
                duration_ms = None
        elif md.get("duration_seconds") is not None:
            try:
                duration_ms = int(float(md["duration_seconds"]) * 1000)
            except Exception:
                duration_ms = None

    vid = video_id or f"{source_type}:{source_uri}"

    payload: JsonObj = {
        "id": vid,
        "tenant_id": None,
        "org_id": None,
        "user_id": None,
        "source_type": str(source_type),
        "source_uri": str(source_uri),
        "title": md.get("title"),
        "channel": md.get("channel"),
        "duration_ms": duration_ms,
        "language": md.get("language"),
        "published_at": None,
        "storage_bucket": storage_bucket,
        "storage_key": storage_key,
        "metadata": md,
    }

    with get_db_conn() as conn:
        out = VideosRepo(conn).upsert_video(payload)
    return str(out["id"])


def create_or_get_transcription_job(
    *,
    video_id: str,
    audio_bucket: str,
    audio_key: str,
    audio_size_bytes: int | None,
) -> tuple[str, str]:
    if not video_id:
        raise ValueError("video_id_required")
    if not audio_bucket or not audio_key:
        raise ValueError("audio_storage_ref_required")

    idempotency_key = f"transcription:{video_id}:{audio_bucket}:{audio_key}"

    payload: JsonObj = {
        "audio_storage_ref": {
            "provider": "minio",
            "bucket": audio_bucket,
            "key": audio_key,
            "content_type": "audio/wav",
            "size_bytes": audio_size_bytes,
        }
    }

    with get_db_conn() as conn:
        repo = JobsRepo(conn)
        try:
            created = repo.create_job(
                {
                    "id": str(uuid.uuid4()),
                    "video_id": video_id,
                    "type": "transcription",
                    "status": "queued",
                    "payload": payload,
                    "idempotency_key": idempotency_key,
                    "tenant_id": None,
                    "transcript_id": None,
                    "segment_id": None,
                    "layer_id": None,
                    "queued_at": None,
                    "started_at": None,
                    "finished_at": None,
                }
            )
            return str(created["id"]), idempotency_key
        except Conflict:
            existing = repo.get_job_by_idempotency_key(idempotency_key)
            return str(existing["id"]), idempotency_key
