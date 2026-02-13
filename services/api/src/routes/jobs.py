from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query
from packages.application.errors import AppError
from packages.application.jobs.ports import JobsRepoPort
from packages.application.jobs.use_case import (
    get_job_use_case,
    list_job_events_use_case,
    list_job_runs_use_case,
    list_jobs_use_case,
)

router = APIRouter(prefix="/jobs", tags=["jobs"])

# --- TEST STORAGE (do not remove; relied upon by tests) ---
_JOBS: dict[str, dict[str, Any]] = {}
_JOB_RUNS: dict[str, list[dict[str, Any]]] = {}
_JOB_EVENTS: dict[str, list[dict[str, Any]]] = {}


def _seed_job_for_tests(**job: Any) -> None:
    """
    Test helper expected by services/api/tests/jobs/*

    Tests pass job_id/job_type, while the contract uses id/type.
    Accept both and store a row-shaped dict.
    """
    job_id = job.get("id") or job.get("job_id")
    if not job_id:
        raise ValueError("missing job id (expected 'id' or 'job_id')")

    # normalize legacy keys -> contract-ish keys
    if "id" not in job:
        job["id"] = str(job_id)
    if "type" not in job and "job_type" in job:
        job["type"] = job["job_type"]

    _JOBS[str(job["id"])] = job


def _http_from_app_error(e: AppError) -> HTTPException:
    mapping = {
        "validation_error": 400,
        "not_found": 404,
        "conflict": 409,
        "unauthorized": 401,
        "forbidden": 403,
        "unavailable": 503,
    }
    return HTTPException(
        status_code=mapping.get(e.code, 500),
        detail={"code": e.code, "message": e.message, "details": e.details},
    )


class Repo(JobsRepoPort):
    def get_job(self, job_id: str):
        return _JOBS.get(job_id)

    def list_jobs(self, *, limit: int, offset: int):
        return list(_JOBS.values())[offset : offset + limit]

    def list_job_runs(self, job_id: str):
        return _JOB_RUNS.get(job_id, [])

    def list_job_events(self, job_id: str, *, limit: int, offset: int):
        return _JOB_EVENTS.get(job_id, [])[offset : offset + limit]


@router.get("")
def list_jobs(limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0)):
    try:
        return list_jobs_use_case(repo=Repo(), limit=limit, offset=offset)
    except AppError as e:
        raise _http_from_app_error(e) from e


@router.get("/{job_id}")
def get_job(job_id: str):
    try:
        return get_job_use_case(repo=Repo(), job_id=job_id)
    except AppError as e:
        raise _http_from_app_error(e) from e


@router.get("/{job_id}/runs")
def get_runs(job_id: str):
    try:
        return list_job_runs_use_case(repo=Repo(), job_id=job_id)
    except AppError as e:
        raise _http_from_app_error(e) from e


@router.get("/{job_id}/events")
def get_events(
    job_id: str,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    try:
        return list_job_events_use_case(
            repo=Repo(),
            job_id=job_id,
            limit=limit,
            offset=offset,
        )
    except AppError as e:
        raise _http_from_app_error(e) from e
