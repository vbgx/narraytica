from __future__ import annotations

import json
from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import text

from .db import get_db


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _acquire_conn() -> Any:
    db = get_db()
    if hasattr(db, "execute"):
        return db
    if isinstance(db, Iterator):
        return next(db)
    raise RuntimeError(f"get_db() returned unsupported object: {type(db).__name__}")


class IngestPortDB:
    """
    Infra adapter: create an ingest job in DB.
    Returns a dict job record (contract-ish).
    """

    def create_ingest_job(self, payload: dict[str, Any]) -> dict[str, Any]:
        conn = _acquire_conn()

        job_id = f"job_{uuid4().hex}"
        now = _utc_now_iso()

        conn.execute(
            text(
                """
                INSERT INTO jobs (
                    id,
                    type,
                    status,
                    video_id,
                    payload,
                    queued_at,
                    created_at,
                    updated_at
                )
                VALUES (
                    :id,
                    :type,
                    :status,
                    :video_id,
                    :payload,
                    :queued_at,
                    :created_at,
                    :updated_at
                )
                """
            ),
            {
                "id": job_id,
                "type": "ingest",
                "status": "queued",
                "video_id": str(
                    payload.get("video_id")
                    or payload.get("videoId")
                    or payload.get("video")
                    or "unknown"
                ),
                "payload": json.dumps(payload),
                "queued_at": now,
                "created_at": now,
                "updated_at": now,
            },
        )
        try:
            conn.commit()
        except Exception:
            pass

        return {
            "id": job_id,
            "type": "ingest",
            "status": "queued",
            "video_id": str(
                payload.get("video_id")
                or payload.get("videoId")
                or payload.get("video")
                or "unknown"
            ),
            "payload": payload,
            "queued_at": now,
            "created_at": now,
            "updated_at": now,
        }
