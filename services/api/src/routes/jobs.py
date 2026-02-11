from __future__ import annotations

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("")
def list_jobs() -> list[dict]:
    # Returns Job[] (canonical)
    return []


@router.get("/{job_id}")
def get_job(job_id: str) -> dict:
    raise HTTPException(
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
