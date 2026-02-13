from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from .hybrid_merge import merge_results
from .ports import SearchInfraPort

SearchMode = Literal["lexical", "semantic", "hybrid"]


@dataclass(frozen=True)
class SearchConfig:
    max_limit: int = 100


def parse_mode(
    *,
    mode: SearchMode | None,
    semantic_legacy: bool | None,
    query_text: str,
) -> SearchMode:
    if mode:
        return mode
    if semantic_legacy is True:
        return "hybrid"
    if semantic_legacy is False:
        return "lexical"
    return "hybrid" if query_text else "lexical"


def search_use_case(
    *,
    infra: SearchInfraPort,
    build_lexical_query: Any,
    query: dict[str, Any],
    config: SearchConfig | None = None,
) -> dict[str, Any]:
    if config is None:
        config = SearchConfig()

    query_text = str(query.get("query") or "").strip()
    limit = int(query.get("limit") or 20)
    offset = int(query.get("offset") or 0)

    if limit < 1 or limit > config.max_limit:
        raise ValueError("limit out of range")
    if offset < 0:
        raise ValueError("offset out of range")

    filters = query.get("filters") or None
    mode = parse_mode(
        mode=query.get("mode"),
        semantic_legacy=query.get("semantic"),
        query_text=query_text,
    )

    fetch_n = min(config.max_limit, limit + offset)

    lexical_body = build_lexical_query(
        query=query_text or None,
        filters=filters,
        limit=fetch_n,
        offset=0,
    )

    lexical_hits, sources, lexical_scores, highlights = infra.opensearch_search(
        lexical_body
    )

    vector_hits = []
    vector_scores = {}

    if mode in ("semantic", "hybrid"):
        if not query_text:
            raise ValueError("semantic search requires a query")
        v = infra.vector_search(query_text=query_text, filters=filters, top_k=fetch_n)
        vector_hits = [{"segment_id": x.segment_id, "score": x.score} for x in v]
        for x in v:
            vector_scores[str(x.segment_id)] = float(x.score)

    if mode == "semantic":
        merged = merge_results(lexical=[], vector=vector_hits)
    elif mode == "lexical":
        merged = merge_results(lexical=lexical_hits, vector=[])
    else:
        merged = merge_results(lexical=lexical_hits, vector=vector_hits)

    page = merged[offset : offset + limit]
    page_ids = [x.segment_id for x in page]

    missing_ids = [sid for sid in page_ids if sid not in sources]
    if missing_ids:
        sources.update(infra.opensearch_mget(missing_ids))

    items = []
    for x in page:
        src = sources.get(x.segment_id) or {}

        video_id = src.get("video_id") or src.get("videoId") or src.get("video")
        start_ms = (
            src.get("start_ms")
            or src.get("startMs")
            or src.get("start")
            or src.get("start_time_ms")
        )
        end_ms = (
            src.get("end_ms")
            or src.get("endMs")
            or src.get("end")
            or src.get("end_time_ms")
        )
        text = src.get("text") or src.get("content") or ""

        if not video_id or start_ms is None or end_ms is None:
            raise RuntimeError(
                f"segment source missing required fields for {x.segment_id}"
            )

        segment = {
            "id": str(x.segment_id),
            "video_id": str(video_id),
            "transcript_id": src.get("transcript_id") or src.get("transcriptId"),
            "speaker_id": src.get("speaker_id") or src.get("speakerId"),
            "segment_index": src.get("segment_index") or src.get("index"),
            "start_ms": int(start_ms),
            "end_ms": int(end_ms),
            "text": str(text),
            "language": src.get("language"),
            "source": src.get("source"),
            "created_at": src.get("created_at"),
            "updated_at": src.get("updated_at"),
        }

        items.append(
            {
                "segment": segment,
                "video": None,
                "speaker": None,
                "highlights": highlights.get(x.segment_id),
                "score": {
                    "combined": float(x.score),
                    "lexical": lexical_scores.get(x.segment_id),
                    "vector": vector_scores.get(x.segment_id),
                    "lexical_rank": x.lexical_rank,
                    "vector_rank": x.vector_rank,
                },
            }
        )

    items.sort(
        key=lambda it: (
            -float(it["score"]["combined"]),
            str(it["segment"]["video_id"]),
            int(it["segment"]["start_ms"]),
            str(it["segment"]["id"]),
        )
    )

    return {
        "items": items,
        "page": {"limit": limit, "offset": offset, "total": len(merged)},
    }
