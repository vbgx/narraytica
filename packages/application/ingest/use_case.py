from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any, Protocol

from packages.application.errors import AppError


class JobsRepoPort(Protocol):
    def get_job_by_external_id(self, external_id: str) -> dict[str, Any] | None: ...
    def create_job(self, payload: dict[str, Any]) -> dict[str, Any]: ...


class ObsPort(Protocol):
    def emit(self, event_type: str, payload: dict[str, Any]) -> None: ...


def _validate_source(source: dict[str, Any]) -> None:
    if not isinstance(source, dict):
        raise AppError(code="validation_error", message="invalid source")

    kind = source.get("kind")

    if not kind:
        raise AppError(code="validation_error", message="source.kind is required")

    if kind == "external_url":
        if not source.get("url"):
            raise AppError(
                code="validation_error",
                message="source.url is required for external_url",
            )


def request_ingest(
    *,
    input_dto: dict[str, Any],
    jobs_repo: JobsRepoPort,
    obs: ObsPort | None = None,
) -> dict[str, Any]:

    external_id = input_dto.get("external_id")
    source = input_dto.get("source")

    if not source:
        raise AppError(code="validation_error", message="source is required")

    _validate_source(source)

    # Idempotence
    if external_id:
        existing = jobs_repo.get_job_by_external_id(external_id)
        if existing:
            return existing

    job_id = f"job_{uuid.uuid4().hex[:12]}"
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")

    job_payload = {
        "id": job_id,
        "external_id": external_id,
        "type": "ingest",
        "status": "queued",
        "video_id": None,
        "payload": input_dto,
        "queued_at": now,
        "created_at": now,
        "updated_at": now,
    }

    created = jobs_repo.create_job(job_payload)

    if obs:
        obs.emit("ingest.requested", {"job_id": job_id})

    return created
