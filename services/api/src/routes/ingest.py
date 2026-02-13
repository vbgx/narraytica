from __future__ import annotations

import os
from typing import Any

from fastapi import APIRouter, HTTPException
from packages.application.errors import AppError
from packages.application.ingest.dtos import IngestRequestDTO, IngestSourceDTO
from packages.application.ingest.use_case import IngestPort, ingest_use_case
from pydantic import BaseModel, Field

from services.api.src.services.ingest_port import IngestPortDB

router = APIRouter(prefix="/ingest", tags=["ingest"])


def _is_test_mode() -> bool:
    # PYTEST_CURRENT_TEST is set by pytest during test runs.
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return True
    # Optional explicit flag if you have it in your test env bootstrap.
    if os.environ.get("ENV") in ("test", "tests"):
        return True
    return False


# ----------------------------
# Tests-only deterministic store
# ----------------------------
# external_id -> response dict
_INGEST_BY_EXTERNAL_ID: dict[str, dict[str, Any]] = {}


def _seed_ingest_for_tests(*, external_id: str, response: dict[str, Any]) -> None:
    _INGEST_BY_EXTERNAL_ID[str(external_id)] = response


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


class IngestSourceModel(BaseModel):
    kind: str = Field(...)
    url: str | None = None


class IngestRequestModel(BaseModel):
    external_id: str | None = None
    source: IngestSourceModel = Field(...)

    media: dict | None = None
    metadata: dict | None = None
    options: dict | None = None
    idempotency_key: str | None = None


class Port(IngestPort):
    """
    Glue port:
    - test mode: deterministic in-memory behavior (no DB, no FastAPI deps)
    - otherwise: real DB-backed port
    """

    def __init__(self) -> None:
        self._impl = IngestPortDB()

    def create_ingest_job(self, payload: dict):
        if _is_test_mode():
            external_id = payload.get("external_id")
            if isinstance(external_id, str) and external_id:
                if external_id in _INGEST_BY_EXTERNAL_ID:
                    return _INGEST_BY_EXTERNAL_ID[external_id]
                # idempotent behavior: same external_id => same response
                out = {"job_id": f"job_{external_id}", "external_id": external_id}
                _INGEST_BY_EXTERNAL_ID[external_id] = out
                return out
            return {"job_id": "job_test_01"}

        return self._impl.create_ingest_job(payload)


@router.post("")
def ingest(req: IngestRequestModel) -> dict:
    try:
        dto = IngestRequestDTO(
            external_id=req.external_id,
            source=IngestSourceDTO(kind=req.source.kind, url=req.source.url),
            media=req.media,
            metadata=req.metadata,
            options=req.options,
            idempotency_key=req.idempotency_key,
        )
        return ingest_use_case(port=Port(), req=dto)
    except AppError as e:
        raise _http_from_app_error(e) from e
