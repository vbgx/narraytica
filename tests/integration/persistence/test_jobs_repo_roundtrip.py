from __future__ import annotations

import os
from datetime import UTC, datetime

import psycopg
import pytest
from packages.persistence.postgres.repos.jobs_repo import JobsRepo


def _dsn() -> str:
    dsn = os.environ.get("POSTGRES_DSN")
    if not dsn:
        pytest.skip("POSTGRES_DSN not set (integration test skipped)")
    return dsn


def test_jobs_repo_roundtrip():
    with psycopg.connect(_dsn()) as conn:
        repo = JobsRepo(conn)

        now = datetime.now(UTC)

        job = {
            "id": "job_test_1",
            "kind": "ingest",
            "status": "queued",
            "created_at": now,
            "updated_at": now,
            "payload": {"source": "test"},
        }
        created = repo.create_job(job)
        assert created["id"] == job["id"]

        run = {
            "id": "run_test_1",
            "job_id": job["id"],
            "attempt": 1,
            "status": "running",
            "started_at": now,
            "finished_at": None,
            "meta": {},
        }
        created_run = repo.create_job_run(run)
        assert created_run["job_id"] == job["id"]

        event = {
            "id": "evt_test_1",
            "kind": "started",
            "occurred_at": now,
            "payload": {"ok": True},
        }
        created_evt = repo.append_job_event(job["id"], event)
        assert created_evt["job_id"] == job["id"]

        assert len(repo.list_job_runs(job["id"])) >= 1
        assert len(repo.list_job_events(job["id"])) >= 1
