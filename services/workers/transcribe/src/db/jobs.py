from __future__ import annotations

import json
import logging
import uuid
from typing import Any

from .postgres import get_db_conn

logger = logging.getLogger("transcribe-worker.db.jobs")


def _uuid() -> str:
    return str(uuid.uuid4())


def claim_next_transcription_job() -> dict[str, Any] | None:
    """
    Claim the next queued transcription job (FIFO-ish) with SKIP LOCKED.

    Claim strategy:
      - select one queued job
      - lock it FOR UPDATE SKIP LOCKED
      - transition to running + started_at
      - insert a job_runs row (attempt=1 at v0)
    """
    sql_select = """
    SELECT id, video_id, type, status, payload
    FROM public.jobs
    WHERE status = 'queued'
      AND type IN ('transcription', 'transcribe')
    ORDER BY queued_at ASC, created_at ASC
    FOR UPDATE SKIP LOCKED
    LIMIT 1;
    """

    sql_mark_running = """
    UPDATE public.jobs
    SET status = 'running',
        started_at = COALESCE(started_at, now()),
        updated_at = now()
    WHERE id = %(job_id)s;
    """

    sql_insert_run = """
    INSERT INTO public.job_runs (
        id,
        job_id,
        attempt,
        status,
        started_at,
        created_at,
        updated_at
    )
    VALUES (%(id)s, %(job_id)s, 1, 'running', now(), now(), now())
    ON CONFLICT (job_id, attempt) DO UPDATE SET
      status = EXCLUDED.status,
      started_at = COALESCE(public.job_runs.started_at, EXCLUDED.started_at),
      updated_at = now();
    """

    with get_db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("BEGIN;")
            cur.execute(sql_select)
            row = cur.fetchone()
            if not row:
                cur.execute("COMMIT;")
                return None

            job_id, video_id, job_type, status, payload = row

            cur.execute(sql_mark_running, {"job_id": job_id})
            cur.execute(sql_insert_run, {"id": _uuid(), "job_id": job_id})

            cur.execute("COMMIT;")

    job = {
        "id": job_id,
        "video_id": video_id,
        "type": job_type,
        "status": status,
        "payload": (
            payload if isinstance(payload, dict) else json.loads(payload or "{}")
        ),
    }
    logger.info("job_claimed", extra={"job_id": job_id, "video_id": video_id})
    return job


def mark_job_succeeded(*, job_id: str) -> None:
    sql = """
    UPDATE public.jobs
    SET status = 'succeeded',
        finished_at = now(),
        updated_at = now()
    WHERE id = %(job_id)s;
    """
    sql_run = """
    UPDATE public.job_runs
    SET status = 'succeeded',
        finished_at = now(),
        updated_at = now()
    WHERE job_id = %(job_id)s AND attempt = 1;
    """
    with get_db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, {"job_id": job_id})
            cur.execute(sql_run, {"job_id": job_id})
        conn.commit()


def mark_job_failed(*, job_id: str, error_message: str) -> None:
    sql = """
    UPDATE public.jobs
    SET status = 'failed',
        finished_at = now(),
        updated_at = now()
    WHERE id = %(job_id)s;
    """
    sql_run = """
    UPDATE public.job_runs
    SET status = 'failed',
        error_message = %(error_message)s,
        finished_at = now(),
        updated_at = now()
    WHERE job_id = %(job_id)s AND attempt = 1;
    """
    with get_db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, {"job_id": job_id, "error_message": error_message})
            cur.execute(sql_run, {"job_id": job_id, "error_message": error_message})
        conn.commit()
