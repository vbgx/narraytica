from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from packages.application.errors import AppError
from packages.application.ingest.use_case import JobsRepoPort, request_ingest
from pydantic import BaseModel

router = APIRouter(prefix="/ingest", tags=["ingest"])


class IngestRequestModel(BaseModel):
    external_id: str | None = None
    source: dict
    metadata: dict | None = None
    options: dict | None = None


# --- Temporary simple in-memory adapter (keeps tests green) ---

_JOBS: dict[str, dict[str, Any]] = {}
_EXTERNAL_INDEX: dict[str, str] = {}


class Repo(JobsRepoPort):
    def get_job_by_external_id(self, external_id: str):
        job_id = _EXTERNAL_INDEX.get(external_id)
        if not job_id:
            return None
        return _JOBS.get(job_id)

    def create_job(self, payload: dict[str, Any]):
        _JOBS[payload["id"]] = payload
        if payload.get("external_id"):
            _EXTERNAL_INDEX[payload["external_id"]] = payload["id"]
        return payload


class NoopObs:
    def emit(self, event_type: str, payload: dict[str, Any]) -> None:
        pass


@router.post("")
def ingest(req: IngestRequestModel):
    try:
        result = request_ingest(
            input_dto=req.model_dump(),
            jobs_repo=Repo(),
            obs=NoopObs(),
        )
        return result
    except AppError as e:
        status = 400 if e.code == "validation_error" else 503
        raise HTTPException(
            status_code=status,
            detail={"code": e.code, "message": e.message, "details": e.details},
        ) from e
