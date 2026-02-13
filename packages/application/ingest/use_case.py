from __future__ import annotations

from typing import Any, Protocol

from ..errors import AppError
from .dtos import IngestRequestDTO


class IngestPort(Protocol):
    def create_ingest_job(self, payload: dict[str, Any]) -> dict[str, Any]: ...


def ingest_use_case(*, port: IngestPort, req: IngestRequestDTO) -> dict[str, Any]:
    # Contract-level validation (application, not FastAPI)
    if not req.source.kind or not isinstance(req.source.kind, str):
        raise AppError(code="validation_error", message="source.kind is required")

    if req.source.kind == "external_url":
        if not req.source.url or not isinstance(req.source.url, str):
            raise AppError(
                code="validation_error",
                message="source.url is required for external_url",
            )

    payload = req.to_payload()

    try:
        out = port.create_ingest_job(payload)
    except AppError:
        raise
    except Exception as e:
        raise AppError(
            code="unavailable", message="ingest backend unavailable", details=str(e)
        ) from e

    return out
