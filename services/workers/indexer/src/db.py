from __future__ import annotations

import os

import psycopg


def update_job_status(job_id: str, status: str, error: str | None = None) -> None:
    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        raise RuntimeError("DATABASE_URL is required to update job status")

    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            if error is None:
                cur.execute(
                    "update jobs set status=%s, updated_at=now() where id=%s",
                    (status, job_id),
                )
            else:
                cur.execute(
                    "update jobs set status=%s, error=%s, updated_at=now() where id=%s",
                    (status, error, job_id),
                )
        conn.commit()
