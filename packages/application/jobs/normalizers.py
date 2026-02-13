from __future__ import annotations

from datetime import datetime
from typing import Any

from ..errors import AppError


def _iso(ts: Any) -> str | None:
    if ts is None:
        return None
    if isinstance(ts, str):
        return ts
    if isinstance(ts, datetime):
        return ts.isoformat()
    return str(ts)


def _require(x: Any, field: str) -> Any:
    if x is None:
        raise AppError(
            code="internal_error", message=f"missing required field: {field}"
        )
    return x


def _require_str(x: Any, field: str) -> str:
    if x is None:
        raise AppError(
            code="internal_error", message=f"missing required field: {field}"
        )
    s = str(x)
    if not s:
        raise AppError(code="internal_error", message=f"empty required field: {field}")
    return s


def _drop_none(d: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in d.items() if v is not None}


def normalize_job(raw: Any) -> dict[str, Any]:
    """
    Normalize any DB-shaped job row/dict into contract shape (job.schema.json).

    Important: optional fields must be omitted (not null).
    Required: id, type, status, video_id, queued_at, created_at, updated_at
    """
    if not isinstance(raw, dict):
        raise AppError(
            code="internal_error",
            message="invalid job shape",
            details=type(raw).__name__,
        )

    job_id = _require_str(raw.get("id"), "id")
    job_type = _require_str(raw.get("type"), "type")
    status = _require_str(raw.get("status"), "status")
    video_id = _require_str(raw.get("video_id"), "video_id")

    queued_at = _require_str(_iso(raw.get("queued_at")), "queued_at")
    created_at = _require_str(_iso(raw.get("created_at")), "created_at")
    updated_at = _require_str(_iso(raw.get("updated_at")), "updated_at")

    out: dict[str, Any] = {
        "id": job_id,
        "tenant_id": raw.get("tenant_id"),
        "type": job_type,
        "status": status,
        "ingestion_phase": raw.get("ingestion_phase"),
        "idempotency_key": raw.get("idempotency_key"),
        "video_id": video_id,
        "transcript_id": raw.get("transcript_id"),
        "segment_id": raw.get("segment_id"),
        "layer_id": raw.get("layer_id"),
        "payload": raw.get("payload"),
        "error_message": raw.get("error_message"),
        "queued_at": queued_at,
        "started_at": _iso(raw.get("started_at")),
        "finished_at": _iso(raw.get("finished_at")),
        "created_at": created_at,
        "updated_at": updated_at,
    }

    # Status/timestamps stability rules:
    # - running: ensure started_at exists
    # - terminal: ensure finished_at exists
    if out["status"] == "running" and out.get("started_at") is None:
        out["started_at"] = out["updated_at"]
    if (
        out["status"] in ("succeeded", "failed", "canceled")
        and out.get("finished_at") is None
    ):
        out["finished_at"] = out["updated_at"]

    return _drop_none(out)


def normalize_job_event(raw: Any) -> dict[str, Any]:
    """
    Normalize into job_event.schema.json shape.

    Important: optional fields must be omitted (not null).
    Required: id, job_id, event_type, payload, created_at
    """
    if not isinstance(raw, dict):
        raise AppError(
            code="internal_error",
            message="invalid job event shape",
            details=type(raw).__name__,
        )

    out: dict[str, Any] = {
        "id": str(_require(raw.get("id"), "id")),
        "job_id": str(_require(raw.get("job_id"), "job_id")),
        "run_id": str(raw["run_id"]) if raw.get("run_id") is not None else None,
        "event_type": str(_require(raw.get("event_type"), "event_type")),
        "payload": _require(raw.get("payload"), "payload"),
        "created_at": str(_require(_iso(raw.get("created_at")), "created_at")),
    }
    return _drop_none(out)


def normalize_job_run(raw: Any) -> dict[str, Any]:
    """
    Normalize into job_run.schema.json shape.

    Important: optional fields must be omitted (not null).
    Required: id, job_id, attempt, status, created_at, updated_at
    """
    if not isinstance(raw, dict):
        raise AppError(
            code="internal_error",
            message="invalid job run shape",
            details=type(raw).__name__,
        )

    created_at = _require(_iso(raw.get("created_at")), "created_at")
    updated_at = _require(_iso(raw.get("updated_at")), "updated_at")

    out: dict[str, Any] = {
        "id": str(_require(raw.get("id"), "id")),
        "job_id": str(_require(raw.get("job_id"), "job_id")),
        "attempt": int(_require(raw.get("attempt"), "attempt")),
        "status": str(_require(raw.get("status"), "status")),
        "started_at": _iso(raw.get("started_at")),
        "finished_at": _iso(raw.get("finished_at")),
        "error": raw.get("error"),
        "metadata": raw.get("metadata"),
        "created_at": str(created_at),
        "updated_at": str(updated_at),
    }

    # stability: terminal => finished_at
    if (
        out["status"] in ("succeeded", "failed", "canceled")
        and out.get("finished_at") is None
    ):
        out["finished_at"] = out["updated_at"]

    return _drop_none(out)
