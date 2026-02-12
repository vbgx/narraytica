from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator

JOB_SCHEMA = json.loads(Path("packages/contracts/schemas/job.schema.json").read_text())
JOB_RUN_SCHEMA = json.loads(
    Path("packages/contracts/schemas/job_run.schema.json").read_text()
)
JOB_EVENT_SCHEMA = json.loads(
    Path("packages/contracts/schemas/job_event.schema.json").read_text()
)

v_job = Draft202012Validator(JOB_SCHEMA)
v_run = Draft202012Validator(JOB_RUN_SCHEMA)
v_event = Draft202012Validator(JOB_EVENT_SCHEMA)


def _assert_valid(validator: Draft202012Validator, data: Any) -> None:
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
    assert not errors, "\n".join([f"{list(e.path)}: {e.message}" for e in errors])


@pytest.fixture()
def client() -> TestClient:
    # Minimal app: mount ONLY jobs router under /api/v1
    import services.api.src.routes.jobs as jobs_mod

    app = FastAPI()
    v1 = APIRouter(prefix="/api/v1")
    v1.include_router(jobs_mod.router)
    app.include_router(v1)

    return TestClient(app, raise_server_exceptions=True)


def test_jobs_list_and_get_match_job_contract(client: TestClient) -> None:
    import services.api.src.routes.jobs as jobs_mod

    jobs_mod._seed_job_for_tests(
        job_id="job_01",
        job_type="ingest",
        status="queued",
        video_id="vid_01",
        queued_at="2026-01-01T00:00:00Z",
        created_at="2026-01-01T00:00:00Z",
        updated_at="2026-01-01T00:00:00Z",
    )

    r = client.get("/api/v1/jobs")
    assert r.status_code == 200, r.text
    data = r.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    for job in data:
        _assert_valid(v_job, job)

    r2 = client.get("/api/v1/jobs/job_01")
    assert r2.status_code == 200, r2.text
    _assert_valid(v_job, r2.json())


def test_job_runs_and_events_match_contracts(client: TestClient) -> None:
    import services.api.src.routes.jobs as jobs_mod

    jobs_mod._seed_job_for_tests(
        job_id="job_02",
        job_type="transcribe",
        status="running",
        video_id="vid_02",
        queued_at="2026-01-01T00:00:00Z",
        created_at="2026-01-01T00:00:00Z",
        updated_at="2026-01-01T00:00:01Z",
        started_at="2026-01-01T00:00:01Z",
    )

    jobs_mod._JOB_RUNS["job_02"] = [
        {
            "id": "run_01",
            "job_id": "job_02",
            "attempt": 1,
            "status": "running",
            "started_at": "2026-01-01T00:00:01Z",
            "created_at": "2026-01-01T00:00:01Z",
            "updated_at": "2026-01-01T00:00:02Z",
        }
    ]
    jobs_mod._JOB_EVENTS["job_02"] = [
        {
            "id": "evt_01",
            "job_id": "job_02",
            "run_id": "run_01",
            "event_type": "progress",
            "payload": {"pct": 50},
            "created_at": "2026-01-01T00:00:02Z",
        }
    ]

    r_runs = client.get("/api/v1/jobs/job_02/runs")
    assert r_runs.status_code == 200, r_runs.text
    runs = r_runs.json()
    assert isinstance(runs, list)
    for run in runs:
        _assert_valid(v_run, run)

    r_ev = client.get("/api/v1/jobs/job_02/events")
    assert r_ev.status_code == 200, r_ev.text
    events = r_ev.json()
    assert isinstance(events, list)
    for ev in events:
        _assert_valid(v_event, ev)


def test_job_404_shape(client: TestClient) -> None:
    r = client.get("/api/v1/jobs/nope")
    assert r.status_code == 404
    body = r.json()
    assert "detail" in body
