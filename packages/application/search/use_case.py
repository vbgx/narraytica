from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..errors import AppError
from .dtos import SearchMode, SearchQueryDTO, SearchResultDTO
from .ports import LexicalSearchPort, MergePort, SegmentsPort, VectorSearchPort

MAX_LIMIT = 100


@dataclass(frozen=True)
class SearchDeps:
    lexical: LexicalSearchPort
    segments: SegmentsPort
    vector: VectorSearchPort
    merger: MergePort
    build_lexical_query: Any  # callable


def _parse_mode(req: SearchQueryDTO, query_text: str) -> SearchMode:
    if req.mode:
        return req.mode
    if req.semantic is True:
        return "hybrid"
    if req.semantic is False:
        return "lexical"
    return "hybrid" if query_text else "lexical"


def _validate_paging(limit: int, offset: int) -> tuple[int, int]:
    if limit < 1 or limit > MAX_LIMIT:
        raise AppError(code="validation_error", message=f"limit must be 1..{MAX_LIMIT}")
    if offset < 0:
        raise AppError(code="validation_error", message="offset must be >= 0")
    return limit, offset


def _segment_from_source(segment_id: str, src: dict[str, Any]) -> dict[str, Any]:
    video_id = src.get("video_id") or src.get("videoId") or src.get("video")

    start_ms = (
        src.get("start_ms")
        if src.get("start_ms") is not None
        else (
            src.get("startMs")
            if src.get("startMs") is not None
            else (
                src.get("start")
                if src.get("start") is not None
                else src.get("start_time_ms")
            )
        )
    )

    end_ms = (
        src.get("end_ms")
        if src.get("end_ms") is not None
        else (
            src.get("endMs")
            if src.get("endMs") is not None
            else (
                src.get("end") if src.get("end") is not None else src.get("end_time_ms")
            )
        )
    )

    text = src.get("text") or src.get("content") or ""

    if not video_id or start_ms is None or end_ms is None:
        raise AppError(
            code="internal_error",
            message=f"segment source missing required fields for {segment_id}",
        )

    transcript_id = src.get("transcript_id")
    if transcript_id is None:
        transcript_id = src.get("transcriptId")

    speaker_id = src.get("speaker_id")
    if speaker_id is None:
        speaker_id = src.get("speakerId")

    segment_index = src.get("segment_index")
    if segment_index is None:
        segment_index = src.get("index")

    return {
        "id": str(segment_id),
        "video_id": str(video_id),
        "transcript_id": str(transcript_id) if transcript_id is not None else None,
        "speaker_id": str(speaker_id) if speaker_id is not None else None,
        "segment_index": int(segment_index) if segment_index is not None else None,
        "start_ms": int(start_ms),
        "end_ms": int(end_ms),
        "text": str(text),
        "language": str(src["language"]) if src.get("language") is not None else None,
        "source": str(src["source"]) if src.get("source") is not None else None,
        "created_at": str(src["created_at"])
        if src.get("created_at") is not None
        else None,
        "updated_at": str(src["updated_at"])
        if src.get("updated_at") is not None
        else None,
    }


def execute(*, req: SearchQueryDTO, deps: SearchDeps) -> SearchResultDTO:
    limit, offset = _validate_paging(req.limit, req.offset)

    query_text = (req.query or "").strip()
    mode = _parse_mode(req, query_text)

    fetch_n = min(MAX_LIMIT, limit + offset)

    lexical_body = deps.build_lexical_query(
        query=query_text or None,
        filters=req.filters,
        limit=fetch_n,
        offset=0,
    )

    lexical_hits, sources, lexical_scores, highlights = deps.lexical.search(
        body=lexical_body
    )

    vector_hits: list[dict[str, Any]] = []
    vector_scores: dict[str, float] = {}

    if mode in ("semantic", "hybrid"):
        if not query_text:
            raise AppError(
                code="validation_error", message="semantic search requires a query"
            )
        v = deps.vector.search(
            query_text=query_text, filters=req.filters, top_k=fetch_n
        )
        vector_hits = [{"segment_id": x["segment_id"], "score": x["score"]} for x in v]
        for x in v:
            vector_scores[str(x["segment_id"])] = float(x["score"])

    if mode == "semantic":
        merged = deps.merger.merge(lexical=[], vector=vector_hits)
    elif mode == "lexical":
        merged = deps.merger.merge(lexical=lexical_hits, vector=[])
    else:
        merged = deps.merger.merge(lexical=lexical_hits, vector=vector_hits)

    page = merged[offset : offset + limit]
    page_ids = [x.segment_id for x in page]

    missing_ids = [sid for sid in page_ids if sid not in sources]
    if missing_ids:
        sources.update(deps.segments.mget(ids=missing_ids))

    items: list[dict[str, Any]] = []
    for x in page:
        sid = str(x.segment_id)
        src = sources.get(sid) or {}
        segment = _segment_from_source(sid, src)

        lex = lexical_scores.get(sid)
        lex_score = float(lex) if isinstance(lex, (int, float)) else None
        vec_score = vector_scores.get(sid)

        items.append(
            {
                "segment": segment,
                "video": None,
                "speaker": None,
                "highlights": highlights.get(sid),
                "score": {
                    "combined": float(x.score),
                    "lexical": lex_score,
                    "vector": vec_score,
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

    return SearchResultDTO(
        data={
            "items": items,
            "page": {"limit": limit, "offset": offset, "total": len(merged)},
        }
    )
