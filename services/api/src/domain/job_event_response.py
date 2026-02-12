from __future__ import annotations

from datetime import datetime
from typing import Any


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
        raise ValueError(f"missing required field: {field}")
    return x


def _drop_none(d: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in d.items() if v is not None}


def normalize_job_event(raw: dict[str, Any]) -> dict[str, Any]:
    """
    Normalize into job_event.schema.json shape.

    Important: optional fields must be omitted (not null).
    Required: id, job_id, event_type, payload, created_at
    """
    out: dict[str, Any] = {
        "id": str(_require(raw.get("id"), "id")),
        "job_id": str(_require(raw.get("job_id"), "job_id")),
        "run_id": str(raw["run_id"]) if raw.get("run_id") is not None else None,
        "event_type": str(_require(raw.get("event_type"), "event_type")),
        "payload": _require(raw.get("payload"), "payload"),
        "created_at": str(_require(_iso(raw.get("created_at")), "created_at")),
    }
    return _drop_none(out)
