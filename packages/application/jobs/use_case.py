from __future__ import annotations

from typing import Any, Protocol

from ..errors import AppError
from .normalizers import normalize_job, normalize_job_event, normalize_job_run


class JobsRepoPort(Protocol):
    """
    Application port. Implemented by API infra.
    """

    def get_job(self, job_id: str) -> Any: ...
    def list_jobs(self, *, limit: int, offset: int) -> list[Any]: ...
    def list_job_events(self, job_id: str, *, limit: int, offset: int) -> list[Any]: ...
    def get_job_run(self, job_id: str) -> Any: ...


def list_jobs_use_case(*, repo: JobsRepoPort, limit: int, offset: int) -> dict:
    if limit < 1 or offset < 0:
        raise AppError(code="validation_error", message="invalid pagination")

    raws = repo.list_jobs(limit=limit, offset=offset)
    items = [normalize_job(x) for x in raws]
    return {"items": items, "page": {"limit": limit, "offset": offset, "total": None}}


def get_job_use_case(*, repo: JobsRepoPort, job_id: str) -> dict:
    if not job_id or not isinstance(job_id, str):
        raise AppError(code="validation_error", message="job_id is required")

    raw = repo.get_job(job_id)
    if raw is None:
        raise AppError(
            code="not_found", message="job not found", details={"job_id": job_id}
        )

    return normalize_job(raw)


def get_job_run_use_case(*, repo: JobsRepoPort, job_id: str) -> dict:
    if not job_id or not isinstance(job_id, str):
        raise AppError(code="validation_error", message="job_id is required")

    raw = repo.get_job_run(job_id)
    if raw is None:
        raise AppError(
            code="not_found", message="job run not found", details={"job_id": job_id}
        )

    return normalize_job_run(raw)


def list_job_events_use_case(
    *, repo: JobsRepoPort, job_id: str, limit: int, offset: int
) -> dict:
    if not job_id or not isinstance(job_id, str):
        raise AppError(code="validation_error", message="job_id is required")
    if limit < 1 or offset < 0:
        raise AppError(code="validation_error", message="invalid pagination")

    raws = repo.list_job_events(job_id, limit=limit, offset=offset)
    items = [normalize_job_event(x) for x in raws]

    return {"items": items, "page": {"limit": limit, "offset": offset, "total": None}}
