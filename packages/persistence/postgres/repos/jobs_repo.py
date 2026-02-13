from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import psycopg
from packages.persistence.postgres.errors import (
    Conflict,
    NotFound,
    RetryableDbError,
)
from packages.persistence.postgres.mappers.jobs import (
    job_event_row_to_contract,
    job_row_to_contract,
    job_run_row_to_contract,
)
from packages.persistence.postgres.tx import transaction
from psycopg.rows import dict_row

JsonObj = dict[str, Any]


class JobsRepo:
    """
    Postgres implementation for Jobs / JobRuns / JobEvents.

    Returns dicts aligned with contracts.
    """

    def __init__(self, conn: psycopg.Connection):
        self._conn = conn

    def create_job(self, job: JsonObj) -> JsonObj:
        try:
            with transaction(self._conn):
                cur = self._conn.cursor(row_factory=dict_row)
                cur.execute(
                    """
                    INSERT INTO jobs (
                        id, kind, status,
                        created_at, updated_at, payload
                    )
                    VALUES (
                        %(id)s, %(kind)s, %(status)s,
                        %(created_at)s, %(updated_at)s, %(payload)s
                    )
                    RETURNING
                        id, kind, status,
                        created_at, updated_at, payload
                    """,
                    job,
                )
                row = cur.fetchone()
                assert row is not None
                return job_row_to_contract(row)
        except psycopg.errors.UniqueViolation as e:
            raise Conflict(str(e)) from e
        except psycopg.Error as e:
            raise RetryableDbError(str(e)) from e

    def get_job(self, job_id: str) -> JsonObj:
        cur = self._conn.cursor(row_factory=dict_row)
        cur.execute(
            """
            SELECT
                id, kind, status,
                created_at, updated_at, payload
            FROM jobs
            WHERE id = %s
            """,
            (job_id,),
        )
        row = cur.fetchone()
        if not row:
            raise NotFound(f"job not found: {job_id}")
        return job_row_to_contract(row)

    def create_job_run(self, job_run: JsonObj) -> JsonObj:
        try:
            with transaction(self._conn):
                cur = self._conn.cursor(row_factory=dict_row)
                cur.execute(
                    """
                    INSERT INTO job_runs (
                        id, job_id, attempt, status,
                        started_at, finished_at, meta
                    )
                    VALUES (
                        %(id)s, %(job_id)s, %(attempt)s, %(status)s,
                        %(started_at)s, %(finished_at)s, %(meta)s
                    )
                    RETURNING
                        id, job_id, attempt, status,
                        started_at, finished_at, meta
                    """,
                    job_run,
                )
                row = cur.fetchone()
                assert row is not None
                return job_run_row_to_contract(row)
        except psycopg.errors.ForeignKeyViolation as e:
            raise NotFound(str(e)) from e
        except psycopg.errors.UniqueViolation as e:
            raise Conflict(str(e)) from e
        except psycopg.Error as e:
            raise RetryableDbError(str(e)) from e

    def append_job_event(self, job_id: str, event: JsonObj) -> JsonObj:
        try:
            with transaction(self._conn):
                _ = self.get_job(job_id)

                cur = self._conn.cursor(row_factory=dict_row)
                cur.execute(
                    """
                    INSERT INTO job_events (
                        id, job_id, kind,
                        occurred_at, payload
                    )
                    VALUES (
                        %(id)s, %(job_id)s, %(kind)s,
                        %(occurred_at)s, %(payload)s
                    )
                    RETURNING
                        id, job_id, kind,
                        occurred_at, payload
                    """,
                    {**event, "job_id": job_id},
                )
                row = cur.fetchone()
                assert row is not None
                return job_event_row_to_contract(row)
        except NotFound:
            raise
        except psycopg.errors.UniqueViolation as e:
            raise Conflict(str(e)) from e
        except psycopg.Error as e:
            raise RetryableDbError(str(e)) from e

    def list_job_runs(self, job_id: str) -> Sequence[JsonObj]:
        _ = self.get_job(job_id)
        cur = self._conn.cursor(row_factory=dict_row)
        cur.execute(
            """
            SELECT
                id, job_id, attempt, status,
                started_at, finished_at, meta
            FROM job_runs
            WHERE job_id = %s
            ORDER BY attempt ASC
            """,
            (job_id,),
        )
        return [job_run_row_to_contract(r) for r in cur.fetchall()]

    def list_job_events(self, job_id: str) -> Sequence[JsonObj]:
        _ = self.get_job(job_id)
        cur = self._conn.cursor(row_factory=dict_row)
        cur.execute(
            """
            SELECT
                id, job_id, kind,
                occurred_at, payload
            FROM job_events
            WHERE job_id = %s
            ORDER BY occurred_at ASC, id ASC
            """,
            (job_id,),
        )
        return [job_event_row_to_contract(r) for r in cur.fetchall()]
