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


def normalize_job_run(raw: dict[str, Any]) -> dict[str, Any]:
    """
    Normalize into job_run.schema.json shape.

    Important: optional fields must be omitted (not null).
    Required: id, job_id, attempt, status, created_at, updated_at
    """
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
