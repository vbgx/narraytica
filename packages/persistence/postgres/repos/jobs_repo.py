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
    Postgres implementation for jobs / job_runs / job_events.

    Aligned with packages/db/migrations/0009_jobs.sql.
    """

    def __init__(self, conn: psycopg.Connection):
        self._conn = conn

    def create_job(self, job: JsonObj) -> JsonObj:
        """
        Required keys (schema-aligned):
        - id, video_id, type, status
        Optional:
        - payload, idempotency_key, tenant_id,
          transcript_id, segment_id, layer_id,
          queued_at, started_at, finished_at
        """
        try:
            with transaction(self._conn):
                cur = self._conn.cursor(row_factory=dict_row)
                cur.execute(
                    """
                    INSERT INTO jobs (
                        id, video_id, type, status,
                        payload,
                        idempotency_key,
                        tenant_id,
                        transcript_id, segment_id, layer_id,
                        queued_at, started_at, finished_at
                    )
                    VALUES (
                        %(id)s, %(video_id)s, %(type)s, %(status)s,
                        COALESCE(%(payload)s, '{}'::jsonb),
                        %(idempotency_key)s,
                        %(tenant_id)s,
                        %(transcript_id)s, %(segment_id)s, %(layer_id)s,
                        COALESCE(%(queued_at)s, now()),
                        %(started_at)s, %(finished_at)s
                    )
                    RETURNING
                        id, video_id, type, status,
                        payload,
                        idempotency_key,
                        tenant_id,
                        transcript_id, segment_id, layer_id,
                        queued_at, started_at, finished_at,
                        created_at, updated_at
                    """,
                    job,
                )
                row = cur.fetchone()
                assert row is not None
                return job_row_to_contract(row)
        except psycopg.errors.UniqueViolation as e:
            raise Conflict(str(e)) from e
        except psycopg.errors.ForeignKeyViolation as e:
            raise NotFound(str(e)) from e
        except psycopg.Error as e:
            raise RetryableDbError(str(e)) from e

    def get_job(self, job_id: str) -> JsonObj:
        cur = self._conn.cursor(row_factory=dict_row)
        cur.execute(
            """
            SELECT
                id, video_id, type, status,
                payload,
                idempotency_key,
                tenant_id,
                transcript_id, segment_id, layer_id,
                queued_at, started_at, finished_at,
                created_at, updated_at
            FROM jobs
            WHERE id = %s
            """,
            (job_id,),
        )
        row = cur.fetchone()
        if not row:
            raise NotFound(f"job not found: {job_id}")
        return job_row_to_contract(row)

    def get_job_by_idempotency_key(self, idempotency_key: str) -> JsonObj:
        cur = self._conn.cursor(row_factory=dict_row)
        cur.execute(
            """
            SELECT
                id, video_id, type, status,
                payload,
                idempotency_key,
                tenant_id,
                transcript_id, segment_id, layer_id,
                queued_at, started_at, finished_at,
                created_at, updated_at
            FROM jobs
            WHERE idempotency_key = %s
            LIMIT 1
            """,
            (idempotency_key,),
        )
        row = cur.fetchone()
        if not row:
            raise NotFound(f"job not found for idempotency_key: {idempotency_key}")
        return job_row_to_contract(row)

    def create_job_run(self, job_run: JsonObj) -> JsonObj:
        try:
            with transaction(self._conn):
                cur = self._conn.cursor(row_factory=dict_row)
                cur.execute(
                    """
                    INSERT INTO job_runs (
                        id, job_id, attempt, status,
                        started_at, finished_at,
                        error_code, error_message, error_details, error_correlation_id,
                        metadata
                    )
                    VALUES (
                        %(id)s, %(job_id)s, %(attempt)s, %(status)s,
                        %(started_at)s, %(finished_at)s,
                        %(error_code)s, %(error_message)s,
                        %(error_details)s, %(error_correlation_id)s,
                        COALESCE(%(metadata)s, '{}'::jsonb)
                    )
                    RETURNING
                        id, job_id, attempt, status,
                        started_at, finished_at,
                        error_code, error_message, error_details, error_correlation_id,
                        metadata,
                        created_at, updated_at
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
                        id, job_id, run_id,
                        event_type, payload
                    )
                    VALUES (
                        %(id)s, %(job_id)s, %(run_id)s,
                        %(event_type)s, COALESCE(%(payload)s, '{}'::jsonb)
                    )
                    RETURNING
                        id, job_id, run_id,
                        event_type, payload,
                        created_at
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
                started_at, finished_at,
                error_code, error_message, error_details, error_correlation_id,
                metadata,
                created_at, updated_at
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
                id, job_id, run_id,
                event_type, payload,
                created_at
            FROM job_events
            WHERE job_id = %s
            ORDER BY created_at ASC, id ASC
            """,
            (job_id,),
        )
        return [job_event_row_to_contract(r) for r in cur.fetchall()]
