from __future__ import annotations

import json
import os
from typing import Any

from packages.persistence.postgres.db import connection
from packages.persistence.postgres.repos.jobs_repo import JobsRepo
from packages.persistence.postgres.repos.transcripts_repo import TranscriptsRepo


def get_db_conn():
    """
    Compatibility DB entrypoint for transcribe worker.

    Tests set DATABASE_URL.
    In other runtimes we allow POSTGRES_DSN.
    """
    dsn = os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_DSN")
    if not dsn:
        raise RuntimeError("DATABASE_URL (or POSTGRES_DSN) is required")
    return connection(dsn)


def claim_next_transcription_job() -> dict[str, Any] | None:
    with get_db_conn() as conn:
        return JobsRepo(conn).claim_next_transcription_job()


def mark_job_succeeded(*, job_id: str) -> None:
    with get_db_conn() as conn:
        JobsRepo(conn).mark_job_succeeded(job_id=job_id)


def mark_job_failed(*, job_id: str, error_message: str) -> None:
    with get_db_conn() as conn:
        JobsRepo(conn).mark_job_failed(job_id=job_id, error_message=error_message)


def insert_transcript(
    *,
    transcript_id: str,
    video_id: str,
    provider: str | None = None,
    language: str | None = None,
    duration_seconds: float | None = None,
    status: str = "completed",
    metadata: dict[str, Any] | None = None,
    tenant_id: str | None = None,
    artifact_bucket: str | None = None,
    artifact_key: str | None = None,
    artifact_format: str | None = None,
    artifact_bytes: int | None = None,
    artifact_sha256: str | None = None,
    storage_ref: dict[str, Any] | None = None,
    version: int = 1,
    is_latest: bool = True,
) -> None:
    transcript = {
        "id": transcript_id,
        "tenant_id": tenant_id,
        "video_id": video_id,
        "provider": provider,
        "language": language,
        "duration_seconds": duration_seconds,
        "status": status,
        "artifact_bucket": artifact_bucket,
        "artifact_key": artifact_key,
        "artifact_format": artifact_format,
        "artifact_bytes": artifact_bytes,
        "artifact_sha256": artifact_sha256,
        "version": version,
        "is_latest": is_latest,
        "metadata": json.dumps(metadata or {}, ensure_ascii=False),
        "storage_ref": json.dumps(storage_ref or {}, ensure_ascii=False),
    }

    with get_db_conn() as conn:
        TranscriptsRepo(conn).upsert_transcript_by_artifact(transcript=transcript)
