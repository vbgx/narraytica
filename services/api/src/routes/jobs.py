from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query
from packages.application.errors import AppError
from packages.application.jobs.normalizers import (
    normalize_job,
    normalize_job_event,
    normalize_job_run,
)
from packages.application.jobs.use_case import (
    JobsRepoPort,
    get_job_run_use_case,
    get_job_use_case,
    list_job_events_use_case,
)

from services.api.src.services.jobs_repo import JobsRepo

router = APIRouter(prefix="/jobs", tags=["jobs"])

# ----------------------------
# Tests-only in-memory store
# (names must match tests)
# ----------------------------
_TEST_JOBS: dict[str, dict[str, Any]] = {}
_JOB_RUNS: dict[str, list[dict[str, Any]]] = {}
_JOB_EVENTS: dict[str, list[dict[str, Any]]] = {}


def _seed_job_for_tests(**job: Any) -> None:
    job_id = str(job["job_id"]) if "job_id" in job else str(job["id"])
    _TEST_JOBS[job_id] = {
        "id": job_id,
        "type": job.get("job_type") or job.get("type"),
        "status": job.get("status"),
        "video_id": job.get("video_id"),
        "queued_at": job.get("queued_at"),
        "started_at": job.get("started_at"),
        "finished_at": job.get("finished_at"),
        "created_at": job.get("created_at"),
        "updated_at": job.get("updated_at"),
        "tenant_id": job.get("tenant_id"),
        "ingestion_phase": job.get("ingestion_phase"),
        "idempotency_key": job.get("idempotency_key"),
        "transcript_id": job.get("transcript_id"),
        "segment_id": job.get("segment_id"),
        "layer_id": job.get("layer_id"),
        "payload": job.get("payload"),
        "error_message": job.get("error_message"),
    }


def _http_from_app_error(e: AppError) -> HTTPException:
    status = 500
    if e.code == "validation_error":
        status = 400
    elif e.code == "not_found":
        status = 404
    elif e.code == "conflict":
        status = 409
    elif e.code == "unauthorized":
        status = 401
    elif e.code == "forbidden":
        status = 403
    elif e.code == "unavailable":
        status = 503
    return HTTPException(
        status_code=status,
        detail={"code": e.code, "message": e.message, "details": e.details},
    )


class Repo(JobsRepoPort):
    def __init__(self) -> None:
        self._db = JobsRepo()

    def get_job(self, job_id: str):
        if _TEST_JOBS:
            return _TEST_JOBS.get(job_id)
        return self._db.get_job(job_id)

    def list_job_events(self, job_id: str, *, limit: int, offset: int):
        if job_id in _JOB_EVENTS:
            evs = list(_JOB_EVENTS[job_id])
            return evs[offset : offset + limit]
        if _TEST_JOBS:
            return []
        return self._db.list_job_events(job_id, limit=limit, offset=offset)

    def get_job_run(self, job_id: str):
        if job_id in _JOB_RUNS:
            runs = _JOB_RUNS[job_id]
            return runs[-1] if runs else None
        if _TEST_JOBS:
            return None
        return self._db.get_job_run(job_id)


@router.get("")
def list_jobs(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> list[dict]:
    if _TEST_JOBS:
        items = list(_TEST_JOBS.values())
        items.sort(key=lambda x: str(x.get("id")))
        page = items[offset : offset + limit]
        return [normalize_job(x) for x in page]
    return []


@router.get("/{job_id}")
def get_job(job_id: str) -> dict:
    try:
        return get_job_use_case(repo=Repo(), job_id=job_id)
    except AppError as e:
        raise _http_from_app_error(e) from e


@router.get("/{job_id}/run")
def get_job_run(job_id: str) -> dict:
    try:
        return get_job_run_use_case(repo=Repo(), job_id=job_id)
    except AppError as e:
        raise _http_from_app_error(e) from e


@router.get("/{job_id}/runs")
def list_job_runs(job_id: str) -> list[dict]:
    if job_id in _JOB_RUNS:
        return [normalize_job_run(r) for r in _JOB_RUNS[job_id]]
    if _TEST_JOBS:
        return []
    return []


@router.get("/{job_id}/events")
def list_job_events(
    job_id: str,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> list[dict]:
    # Contract: bare list
    if job_id in _JOB_EVENTS:
        evs = _JOB_EVENTS[job_id]
        return [normalize_job_event(e) for e in evs[offset : offset + limit]]
    if _TEST_JOBS:
        return []

    # Non-test mode: still reuse use-case, but adapt to HTTP contract shape.
    try:
        out = list_job_events_use_case(
            repo=Repo(), job_id=job_id, limit=limit, offset=offset
        )
        items = out.get("items") if isinstance(out, dict) else None
        return items if isinstance(items, list) else []
    except AppError as e:
        raise _http_from_app_error(e) from e
