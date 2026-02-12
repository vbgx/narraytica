from __future__ import annotations

import json
from typing import Any

from .postgres import get_db_conn


def persist_video_metadata(
    *,
    video_id: str | None = None,
    source_type: str | None = None,
    source_uri: str | None = None,
    duration_ms: int | None = None,
    storage_bucket: str | None = None,
    storage_key: str | None = None,
    metadata: dict[str, Any] | None = None,
    # Backward/compat inputs (if worker passes richer structures)
    source: dict[str, Any] | None = None,
    artifacts: dict[str, Any] | None = None,
) -> str:
    """
    Upsert into public.videos using the CURRENT schema:

      id, source_type, source_uri, duration_ms, storage_bucket, storage_key, metadata

    - We upsert on UNIQUE(source_type, source_uri)
    - We return the canonical video id (existing or inserted)
    - We keep metadata as jsonb NOT NULL
    """

    # Derive source_type/source_uri from worker-style payload if needed.
    if not source_type or not source_uri:
        if isinstance(source, dict):
            kind = source.get("kind")
            if kind:
                source_type = source_type or str(kind)
            # upload
            if kind == "upload" and source.get("upload_ref"):
                source_uri = source_uri or str(source["upload_ref"])
            # youtube
            if kind == "youtube" and source.get("url"):
                source_uri = source_uri or str(source["url"])

    # Derive canonical storage pointers from artifacts if needed.
    if isinstance(artifacts, dict) and (not storage_bucket or not storage_key):
        v = artifacts.get("video")
        if isinstance(v, dict):
            storage_bucket = storage_bucket or v.get("bucket")
            storage_key = storage_key or v.get("object_key") or v.get("key")

    if not source_type or not source_uri:
        raise ValueError("persist_video_metadata: missing source_type/source_uri")

    # If duration is provided as seconds in metadata, normalize.
    md = dict(metadata or {})
    if duration_ms is None:
        if "duration_ms" in md and md["duration_ms"] is not None:
            try:
                duration_ms = int(md["duration_ms"])
            except Exception:
                duration_ms = None
        elif "duration_seconds" in md and md["duration_seconds"] is not None:
            try:
                duration_ms = int(float(md["duration_seconds"]) * 1000)
            except Exception:
                duration_ms = None

    # Choose a stable id if provided; otherwise derive one from source tuple.
    # (We keep it simple: use provided video_id; else use source-derived string.)
    vid = video_id or f"{source_type}:{source_uri}"

    sql = """
    INSERT INTO public.videos (
      id,
      source_type,
      source_uri,
      duration_ms,
      storage_bucket,
      storage_key,
      metadata,
      created_at,
      updated_at
    )
    VALUES (
      %(id)s,
      %(source_type)s,
      %(source_uri)s,
      %(duration_ms)s,
      %(storage_bucket)s,
      %(storage_key)s,
      %(metadata)s::jsonb,
      now(),
      now()
    )
    ON CONFLICT (source_type, source_uri)
    DO UPDATE SET
      duration_ms = EXCLUDED.duration_ms,
      storage_bucket = EXCLUDED.storage_bucket,
      storage_key = EXCLUDED.storage_key,
      metadata = EXCLUDED.metadata,
      updated_at = now()
    RETURNING id;
    """

    params = {
        "id": vid,
        "source_type": str(source_type),
        "source_uri": str(source_uri),
        "duration_ms": duration_ms,
        "storage_bucket": storage_bucket,
        "storage_key": storage_key,
        "metadata": json.dumps(md, ensure_ascii=False),
    }

    with get_db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            out = cur.fetchone()
        conn.commit()

    if not out or not out[0]:
        raise RuntimeError("persist_video_metadata: upsert returned no id")
    return str(out[0])
