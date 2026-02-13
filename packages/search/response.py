from __future__ import annotations

from typing import Any

from .types import SearchItem, SearchResult


def to_dict(result: SearchResult) -> dict[str, Any]:
    """
    Canonical mapping SearchResult -> dict matching search.schema.json.

    IMPORTANT:
    - Do NOT emit additional properties.
    - Keep deterministic ordering handled elsewhere (ranking).
    """
    return {
        "items": [item_to_dict(it) for it in result.items],
        "page": {
            "limit": int(result.page.limit),
            "offset": int(result.page.offset),
            "total": result.page.total
            if result.page.total is None
            else int(result.page.total),
        },
    }


def item_to_dict(it: SearchItem) -> dict[str, Any]:
    seg = it.segment
    out: dict[str, Any] = {
        "segment": {
            "id": str(seg.id),
            "video_id": str(seg.video_id),
            "transcript_id": seg.transcript_id,
            "speaker_id": seg.speaker_id,
            "segment_index": seg.segment_index,
            "start_ms": int(seg.start_ms),
            "end_ms": int(seg.end_ms),
            "text": str(seg.text),
            "language": seg.language,
            "source": seg.source,
            "created_at": seg.created_at,
            "updated_at": seg.updated_at,
        },
        "video": None
        if it.video is None
        else {
            "id": str(it.video.id),
            "title": it.video.title,
            "source": it.video.source,
            "published_at": it.video.published_at,
        },
        "speaker": None
        if it.speaker is None
        else {
            "id": str(it.speaker.id),
            "name": it.speaker.name,
        },
        "highlights": None
        if it.highlights is None
        else [{"field": h.field, "text": h.text} for h in it.highlights],
        "score": {
            "combined": float(it.score.combined),
            "lexical": it.score.lexical,
            "vector": it.score.vector,
            "lexical_rank": it.score.lexical_rank,
            "vector_rank": it.score.vector_rank,
        },
    }

    # Contract: additionalProperties false everywhere → strip Nones *inside dicts*
    # but keep keys that are allowed to be null (schema uses anyOf/null).
    out["segment"] = {k: v for k, v in out["segment"].items() if v is not None}
    out["score"] = {k: v for k, v in out["score"].items() if v is not None}

    return out
