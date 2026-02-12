from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

JobStatus = Literal["queued", "running", "succeeded", "failed", "canceled"]
JobType = Literal["ingest", "transcribe", "transcription", "diarize", "enrich", "index"]
IngestionPhase = Literal["downloading", "processing", "storing"]


def _iso(ts: Any) -> str | None:
    if ts is None:
        return None
    if isinstance(ts, str):
        return ts
    if isinstance(ts, datetime):
        return ts.isoformat()
    return str(ts)


def _require_str(x: Any, field: str) -> str:
    if x is None:
        raise ValueError(f"missing required field: {field}")
    s = str(x)
    if not s:
        raise ValueError(f"empty required field: {field}")
    return s


def _drop_none(d: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in d.items() if v is not None}


def normalize_job(raw: dict[str, Any]) -> dict[str, Any]:
    """
    Normalize any DB-shaped job row/dict into contract shape (job.schema.json).

    Important: optional fields must be omitted (not null).
    Required: id, type, status, video_id, queued_at, created_at, updated_at
    """
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
