from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, HTTPException

from ..domain.job_event_response import normalize_job_event
from ..domain.job_response import normalize_job
from ..domain.job_run_response import normalize_job_run

router = APIRouter(prefix="/jobs", tags=["jobs"])


# -----------------------------------------------------------------------------
# In-memory store (v0 scaffolding)
# Replace with a repository/service when DB layer is wired.
# -----------------------------------------------------------------------------

_JOBS: dict[str, dict[str, Any]] = {}
_JOB_RUNS: dict[str, list[dict[str, Any]]] = {}
_JOB_EVENTS: dict[str, list[dict[str, Any]]] = {}


def _not_found(job_id: str) -> HTTPException:
    return HTTPException(
        status_code=404,
        detail={
            "error": {
                "code": "resource_not_found",
                "message": "Job not found",
                "details": {"job_id": job_id},
                "correlation_id": None,
            }
        },
    )


def _get_job_or_404(job_id: str) -> dict[str, Any]:
    raw = _JOBS.get(job_id)
    if not raw:
        raise _not_found(job_id)
    return raw


# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------


@router.get("")
def list_jobs() -> list[dict[str, Any]]:
    """
    Returns Job[] (contract: job.schema.json)
    """
    out: list[dict[str, Any]] = []
    for raw in _JOBS.values():
        out.append(normalize_job(raw))
    # deterministic ordering
    out.sort(key=lambda j: (j["created_at"], j["id"]))
    return out


@router.get("/{job_id}")
def get_job(job_id: str) -> dict[str, Any]:
    """
    Returns Job (contract: job.schema.json)
    """
    raw = _get_job_or_404(job_id)
    return normalize_job(raw)


@router.get("/{job_id}/runs")
def list_job_runs(job_id: str) -> list[dict[str, Any]]:
    """
    Returns JobRun[] (contract: job_run.schema.json)
    """
    _ = _get_job_or_404(job_id)
    runs = _JOB_RUNS.get(job_id, [])
    out = [normalize_job_run(r) for r in runs]
    out.sort(key=lambda r: (r["attempt"], r["created_at"], r["id"]))
    return out


@router.get("/{job_id}/events")
def list_job_events(job_id: str) -> list[dict[str, Any]]:
    """
    Returns JobEvent[] (contract: job_event.schema.json)
    """
    _ = _get_job_or_404(job_id)
    events = _JOB_EVENTS.get(job_id, [])
    out = [normalize_job_event(e) for e in events]
    out.sort(key=lambda e: (e["created_at"], e["id"]))
    return out


# -----------------------------------------------------------------------------
# Test-only helpers (seed endpoints are NOT exposed; tests can monkeypatch dicts)
# -----------------------------------------------------------------------------


def _seed_job_for_tests(
    *,
    job_id: str,
    job_type: Literal[
        "ingest", "transcribe", "transcription", "diarize", "enrich", "index"
    ],
    status: Literal["queued", "running", "succeeded", "failed", "canceled"],
    video_id: str,
    queued_at: str,
    created_at: str,
    updated_at: str,
    started_at: str | None = None,
    finished_at: str | None = None,
) -> None:
    _JOBS[job_id] = {
        "id": job_id,
        "type": job_type,
        "status": status,
        "video_id": video_id,
        "queued_at": queued_at,
        "started_at": started_at,
        "finished_at": finished_at,
        "created_at": created_at,
        "updated_at": updated_at,
    }
