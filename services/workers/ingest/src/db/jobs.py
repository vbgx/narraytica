from __future__ import annotations

import json
import logging
import uuid

from psycopg.errors import UniqueViolation

from .postgres import get_db_conn

logger = logging.getLogger("ingest-worker.db.jobs")


def _uuid() -> str:
    return str(uuid.uuid4())


def create_or_get_transcription_job(
    *,
    video_id: str,
    audio_bucket: str,
    audio_key: str,
    audio_size_bytes: int | None,
) -> tuple[str, str]:
    """
    Create transcription job when audio is available.

    Idempotency:
      idempotency_key = f"transcription:{video_id}:{audio_bucket}:{audio_key}"

    Returns:
      (job_id, idempotency_key)
    """
    if not video_id:
        raise ValueError("video_id_required")
    if not audio_bucket or not audio_key:
        raise ValueError("audio_storage_ref_required")

    idempotency_key = f"transcription:{video_id}:{audio_bucket}:{audio_key}"
    job_id = _uuid()

    payload = {
        "audio_storage_ref": {
            "provider": "minio",
            "bucket": audio_bucket,
            "key": audio_key,
            "content_type": "audio/wav",
            "size_bytes": audio_size_bytes,
        }
    }

    sql_insert = """
    INSERT INTO public.jobs (
      id, video_id, type, status, payload, idempotency_key,
      queued_at, created_at, updated_at
    )
    VALUES (
      %(id)s, %(video_id)s, %(type)s, %(status)s, %(payload)s::jsonb,
      %(idempotency_key)s,
      now(), now(), now()
    );
    """

    sql_select = """
    SELECT id
    FROM public.jobs
    WHERE idempotency_key = %(idempotency_key)s
    LIMIT 1;
    """

    params = {
        "id": job_id,
        "video_id": video_id,
        "type": "transcription",
        "status": "queued",
        "payload": json.dumps(payload, ensure_ascii=False),
        "idempotency_key": idempotency_key,
    }

    logger.info(
        "transcription_job_insert_attempt",
        extra={"video_id": video_id, "idempotency_key": idempotency_key},
    )

    with get_db_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute(sql_insert, params)
            conn.commit()
            logger.info(
                "transcription_job_inserted",
                extra={
                    "video_id": video_id,
                    "job_id": job_id,
                    "idempotency_key": idempotency_key,
                },
            )
            return job_id, idempotency_key

        except UniqueViolation:
            conn.rollback()
            with conn.cursor() as cur:
                cur.execute(sql_select, {"idempotency_key": idempotency_key})
                row = cur.fetchone()
                if not row:
                    raise
                existing_id = row[0]
                logger.info(
                    "transcription_job_already_exists",
                    extra={
                        "video_id": video_id,
                        "job_id": existing_id,
                        "idempotency_key": idempotency_key,
                    },
                )
                return existing_id, idempotency_key
