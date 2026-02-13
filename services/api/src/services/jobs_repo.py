from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any

from sqlalchemy import text

from .db import get_db


def _acquire_conn() -> Any:
    """
    get_db() is a FastAPI dependency provider in this repo (often yields a conn).
    - In request context, FastAPI drives the generator.
    - In tests / direct calls, we may get a generator object.

    This helper returns a usable conn.
    """
    db = get_db()
    if hasattr(db, "execute"):
        return db
    if isinstance(db, Iterator):
        return next(db)
    raise RuntimeError(f"get_db() returned unsupported object: {type(db).__name__}")


@dataclass(frozen=True)
class JobsRepo:
    """
    Infra adapter: DB-backed repository for jobs.
    Returns dicts (DB rows mapped to dict).
    """

    def get_job(self, job_id: str) -> dict[str, Any] | None:
        conn = _acquire_conn()
        row = (
            conn.execute(
                text(
                    """
                    SELECT *
                    FROM jobs
                    WHERE id = :job_id
                    LIMIT 1
                    """
                ),
                {"job_id": job_id},
            )
            .mappings()
            .first()
        )
        return dict(row) if row else None

    def list_jobs(self, *, limit: int, offset: int) -> list[dict[str, Any]]:
        conn = _acquire_conn()
        rows = (
            conn.execute(
                text(
                    """
                    SELECT *
                    FROM jobs
                    ORDER BY created_at DESC
                    LIMIT :limit OFFSET :offset
                    """
                ),
                {"limit": int(limit), "offset": int(offset)},
            )
            .mappings()
            .all()
        )
        return [dict(r) for r in rows]

    def get_job_run(self, job_id: str) -> dict[str, Any] | None:
        conn = _acquire_conn()
        row = (
            conn.execute(
                text(
                    """
                    SELECT *
                    FROM job_runs
                    WHERE job_id = :job_id
                    ORDER BY started_at DESC NULLS LAST
                    LIMIT 1
                    """
                ),
                {"job_id": job_id},
            )
            .mappings()
            .first()
        )
        return dict(row) if row else None

    def list_job_events(
        self, job_id: str, *, limit: int, offset: int
    ) -> list[dict[str, Any]]:
        conn = _acquire_conn()
        rows = (
            conn.execute(
                text(
                    """
                    SELECT *
                    FROM job_events
                    WHERE job_id = :job_id
                    ORDER BY created_at ASC
                    LIMIT :limit OFFSET :offset
                    """
                ),
                {"job_id": job_id, "limit": int(limit), "offset": int(offset)},
            )
            .mappings()
            .all()
        )
        return [dict(r) for r in rows]
