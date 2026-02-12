from __future__ import annotations

import json
from typing import Any

from .postgres import get_db_conn


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
    """
    Insert a transcript row (idempotent).

    Uniqueness / reruns:
      - DB has a UNIQUE index on (video_id, artifact_key, version)
        with a predicate: WHERE artifact_key IS NOT NULL
      - Therefore our UPSERT MUST match that exact constraint, including the WHERE.

    V0 worker writes:
      - metadata (text/segments/asr/audio_ref, etc.)
      - optional artifact_* pointers (object storage)
      - storage_ref (canonical reference to artifact in object storage)
    """
    sql = """
    INSERT INTO public.transcripts (
      id,
      tenant_id,
      video_id,
      provider,
      language,
      duration_seconds,
      status,
      artifact_bucket,
      artifact_key,
      artifact_format,
      artifact_bytes,
      artifact_sha256,
      version,
      is_latest,
      metadata,
      storage_ref,
      created_at,
      updated_at
    )
    VALUES (
      %(id)s,
      %(tenant_id)s,
      %(video_id)s,
      %(provider)s,
      %(language)s,
      %(duration_seconds)s,
      %(status)s,
      %(artifact_bucket)s,
      %(artifact_key)s,
      %(artifact_format)s,
      %(artifact_bytes)s,
      %(artifact_sha256)s,
      %(version)s,
      %(is_latest)s,
      %(metadata)s::jsonb,
      %(storage_ref)s::jsonb,
      now(),
      now()
    )
    ON CONFLICT (video_id, artifact_key, version)
    WHERE artifact_key IS NOT NULL
    DO UPDATE SET
      tenant_id = EXCLUDED.tenant_id,
      provider = EXCLUDED.provider,
      language = EXCLUDED.language,
      duration_seconds = EXCLUDED.duration_seconds,
      status = EXCLUDED.status,
      artifact_bucket = EXCLUDED.artifact_bucket,
      artifact_key = EXCLUDED.artifact_key,
      artifact_format = EXCLUDED.artifact_format,
      artifact_bytes = EXCLUDED.artifact_bytes,
      artifact_sha256 = EXCLUDED.artifact_sha256,
      is_latest = EXCLUDED.is_latest,
      metadata = EXCLUDED.metadata,
      storage_ref = EXCLUDED.storage_ref,
      updated_at = now();
    """

    params = {
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
        with conn.cursor() as cur:
            cur.execute(sql, params)
        conn.commit()
