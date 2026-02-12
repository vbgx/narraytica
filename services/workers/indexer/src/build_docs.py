from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any

_ws_re = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    t = (text or "").strip()
    t = _ws_re.sub(" ", t)
    return t


def iso(dt_value: Any) -> str | None:
    if dt_value is None:
        return None
    if isinstance(dt_value, str):
        s = dt_value.strip()
        return s or None
    if isinstance(dt_value, datetime):
        return dt_value.isoformat()
    return None


def epoch_ms_from_iso(dt: str | None) -> int | None:
    if not dt:
        return None
    d = datetime.fromisoformat(dt.replace("Z", "+00:00"))
    return int(d.timestamp() * 1000)


@dataclass(frozen=True)
class SegmentDoc:
    segment_id: str
    doc: dict
    qdrant_payload: dict


def build_segment_doc(
    *,
    video_id: str,
    transcript_id: str | None,
    tenant_id: str | None,
    segment: dict,
    transcript_meta: dict | None,
    layers_by_segment_id: dict[str, dict] | None,
) -> SegmentDoc:
    start_ms = int(segment.get("start_ms"))
    end_ms = int(segment.get("end_ms"))
    if start_ms < 0 or end_ms <= start_ms:
        raise ValueError(f"invalid segment timing: start_ms={start_ms} end_ms={end_ms}")

    text = normalize_text(str(segment.get("text") or ""))
    if not text:
        raise ValueError("segment text is empty after normalization")

    fallback_id = f"{video_id}:{start_ms}:{end_ms}"
    segment_id = str(segment.get("id") or segment.get("segment_id") or fallback_id)

    language = None
    source = None
    if transcript_meta:
        language = transcript_meta.get("language")
        source = transcript_meta.get("provider") or transcript_meta.get("source")

    speaker_id = (
        segment.get("speaker_id")
        or (
            segment.get("speaker", {}).get("id")
            if isinstance(segment.get("speaker"), dict)
            else None
        )
        or segment.get("speaker_id")
    )

    created_at = iso(segment.get("created_at"))
    updated_at = iso(segment.get("updated_at"))
    created_at_ms = epoch_ms_from_iso(created_at)

    metadata: dict[str, Any] = {}
    if isinstance(segment.get("metadata"), dict):
        metadata.update(segment["metadata"])

    if transcript_meta and isinstance(transcript_meta.get("metadata"), dict):
        metadata.setdefault("transcript", {})
        if isinstance(metadata["transcript"], dict):
            metadata["transcript"].update(transcript_meta["metadata"])

    if layers_by_segment_id:
        layer = layers_by_segment_id.get(segment_id)
        if isinstance(layer, dict):
            metadata.setdefault("layers", {})
            if isinstance(metadata["layers"], dict):
                metadata["layers"].update(layer)

    doc = {
        "id": segment_id,
        "tenant_id": tenant_id,
        "video_id": video_id,
        "transcript_id": transcript_id,
        "speaker_id": speaker_id,
        "segment_index": segment.get("segment_index"),
        "start_ms": start_ms,
        "end_ms": end_ms,
        "language": language,
        "source": source,
        "created_at": created_at,
        "updated_at": updated_at,
        "text": text,
        "metadata": metadata,
    }

    qdrant_payload = {
        "segment_id": segment_id,
        "video_id": video_id,
        "transcript_id": transcript_id,
        "tenant_id": tenant_id,
        "speaker_id": speaker_id,
        "language": language,
        "source": source,
        "segment_index": segment.get("segment_index"),
        "start_ms": start_ms,
        "end_ms": end_ms,
        "created_at": created_at,
        "updated_at": updated_at,
        "created_at_ms": created_at_ms,
    }

    return SegmentDoc(segment_id=segment_id, doc=doc, qdrant_payload=qdrant_payload)
