from __future__ import annotations

from typing import Any, Protocol

from packages.application.errors import AppError
from packages.application.jobs.normalizers import (
    normalize_job,
    normalize_job_event,
    normalize_job_run,
)


class JobsRepoPort(Protocol):
    def get_job(self, job_id: str) -> dict[str, Any] | None: ...
    def list_jobs(self, *, limit: int, offset: int) -> list[dict[str, Any]]: ...
    def list_job_events(
        self, job_id: str, *, limit: int, offset: int
    ) -> list[dict[str, Any]]: ...
    def get_job_run(self, job_id: str) -> dict[str, Any] | None: ...


def get_job_use_case(*, repo: JobsRepoPort, job_id: str) -> dict[str, Any]:
    raw = repo.get_job(job_id)
    if raw is None:
        raise AppError(code="not_found", message="job not found")

    try:
        return normalize_job(raw)
    except Exception as e:
        raise AppError(
            code="internal_error",
            message="invalid job shape",
            details=str(e),
        ) from e


def list_jobs_use_case(
    *, repo: JobsRepoPort, limit: int, offset: int
) -> list[dict[str, Any]]:
    rows = repo.list_jobs(limit=limit, offset=offset)
    out: list[dict[str, Any]] = []
    for r in rows:
        try:
            out.append(normalize_job(r))
        except Exception:
            continue
    return out


def list_job_events_use_case(
    *, repo: JobsRepoPort, job_id: str, limit: int, offset: int
) -> list[dict[str, Any]]:
    rows = repo.list_job_events(job_id, limit=limit, offset=offset)
    out: list[dict[str, Any]] = []
    for r in rows:
        try:
            out.append(normalize_job_event(r))
        except Exception:
            continue
    return out


def get_job_run_use_case(*, repo: JobsRepoPort, job_id: str) -> dict[str, Any]:
    raw = repo.get_job_run(job_id)
    if raw is None:
        raise AppError(code="not_found", message="job run not found")

    try:
        return normalize_job_run(raw)
    except Exception as e:
        raise AppError(
            code="internal_error",
            message="invalid job run shape",
            details=str(e),
        ) from e
