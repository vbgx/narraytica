from __future__ import annotations

import os
from hashlib import sha256
from typing import Any, Literal

import requests
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field, ValidationError

from ..domain.search_filters import SearchFiltersV1
from ..search.hybrid.merge import merge_results
from ..search.opensearch.lexical_query import build_lexical_query
from ..search.qdrant.vector_search import VectorSearchError, vector_search

router = APIRouter(prefix="/search", tags=["search"])

MAX_LIMIT = 100


class SearchFiltersModel(BaseModel):
    language: str | None = None
    source: str | None = None
    video_id: str | None = None
    speaker_id: str | None = None
    date_from: str | None = None
    date_to: str | None = None


class SearchRequestV1(BaseModel):
    query: str | None = Field(default=None)
    filters: SearchFiltersModel | None = Field(default=None)
    limit: int = Field(default=20, ge=1, le=MAX_LIMIT)
    offset: int = Field(default=0, ge=0)
    mode: Literal["lexical", "semantic", "hybrid"] | None = Field(default=None)
    semantic: bool | None = Field(default=None)


class PageMeta(BaseModel):
    limit: int = Field(..., ge=1)
    offset: int = Field(..., ge=0)
    total: int | None = Field(default=None, ge=0)


class SearchHighlight(BaseModel):
    field: Literal["text", "title", "speaker", "metadata"]
    text: str = Field(..., min_length=1)


class SearchSegment(BaseModel):
    id: str = Field(..., min_length=1)
    video_id: str = Field(..., min_length=1)
    transcript_id: str | None = None
    speaker_id: str | None = None
    segment_index: int | None = Field(default=None, ge=0)
    start_ms: int = Field(..., ge=0)
    end_ms: int = Field(..., ge=0)
    text: str
    language: str | None = None
    source: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


class SearchVideo(BaseModel):
    id: str = Field(..., min_length=1)
    title: str | None = None
    source: str | None = None
    published_at: str | None = None


class SearchSpeaker(BaseModel):
    id: str = Field(..., min_length=1)
    name: str | None = None


class SearchScore(BaseModel):
    combined: float
    lexical: float | None = None
    vector: float | None = None
    lexical_rank: int | None = Field(default=None, ge=1)
    vector_rank: int | None = Field(default=None, ge=1)


class SearchItem(BaseModel):
    segment: SearchSegment
    video: SearchVideo | None = None
    speaker: SearchSpeaker | None = None
    highlights: list[SearchHighlight] | None = None
    score: SearchScore


class SearchResponseV1(BaseModel):
    items: list[SearchItem]
    page: PageMeta


def _opensearch_url() -> str:
    url = os.environ.get("OPENSEARCH_URL")
    if not url:
        raise HTTPException(status_code=503, detail="OpenSearch not configured")
    return url.rstrip("/")


def _segments_index() -> str:
    idx = os.environ.get("OPENSEARCH_SEGMENTS_INDEX")
    if not idx:
        raise HTTPException(
            status_code=503, detail="OPENSEARCH_SEGMENTS_INDEX not configured"
        )
    return idx


def _os_auth() -> tuple[str, str] | None:
    user = os.environ.get("OPENSEARCH_USERNAME")
    pwd = os.environ.get("OPENSEARCH_PASSWORD")
    if user and pwd:
        return (user, pwd)
    return None


def _query_fingerprint(q: str) -> str:
    return sha256(q.encode()).hexdigest()[:12]


def _parse_filters(filters: SearchFiltersModel | None) -> SearchFiltersV1:
    try:
        raw = (filters.model_dump(exclude_none=True) if filters else {}) or {}
        return SearchFiltersV1.model_validate(raw)
    except (ValidationError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


def _parse_mode(
    req: SearchRequestV1, query_text: str
) -> Literal["lexical", "semantic", "hybrid"]:
    # Explicit mode wins.
    if req.mode:
        return req.mode

    # Legacy boolean compatibility:
    # - semantic=True  => hybrid
    # - semantic=False => lexical
    if req.semantic is True:
        return "hybrid"
    if req.semantic is False:
        return "lexical"

    # Default behavior:
    # - if query present => hybrid (best effort)
    # - if empty query   => lexical (filters-only browsing)
    return "hybrid" if query_text else "lexical"


def _highlight_to_items(h: dict[str, Any]) -> list[SearchHighlight]:
    """
    Convert OpenSearch highlight fragments into stable API highlights.

    Determinism:
    - iterate highlight keys in sorted order, so dict ordering never leaks
    """
    out: list[SearchHighlight] = []
    if not isinstance(h, dict):
        return out

    for k in sorted(h.keys()):
        v = h.get(k)
        if not isinstance(v, list):
            continue

        field: Literal["text", "title", "speaker", "metadata"] = "text"
        if k in ("title", "speaker", "metadata"):
            field = k  # type: ignore[assignment]

        for frag in v:
            if isinstance(frag, str) and frag.strip():
                out.append(SearchHighlight(field=field, text=frag))

    return out


def _segment_from_source(segment_id: str, src: dict[str, Any]) -> SearchSegment:
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
        raise HTTPException(
            status_code=500,
            detail=f"segment source missing required fields for {segment_id}",
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

    return SearchSegment(
        id=str(segment_id),
        video_id=str(video_id),
        transcript_id=str(transcript_id) if transcript_id is not None else None,
        speaker_id=str(speaker_id) if speaker_id is not None else None,
        segment_index=int(segment_index) if segment_index is not None else None,
        start_ms=int(start_ms),
        end_ms=int(end_ms),
        text=str(text),
        language=str(src["language"]) if src.get("language") is not None else None,
        source=str(src["source"]) if src.get("source") is not None else None,
        created_at=(
            str(src["created_at"]) if src.get("created_at") is not None else None
        ),
        updated_at=(
            str(src["updated_at"]) if src.get("updated_at") is not None else None
        ),
    )


def _opensearch_search(
    body: dict[str, Any],
) -> tuple[
    list[dict[str, Any]],
    dict[str, dict],
    dict[str, Any],
    dict[str, list[SearchHighlight]],
]:
    url = f"{_opensearch_url()}/{_segments_index()}/_search"
    auth = _os_auth()

    try:
        with requests.Session() as session:
            session.trust_env = False
            r = session.post(url, json=body, timeout=10, auth=auth)
        if 400 <= r.status_code < 500:
            raise HTTPException(
                status_code=400, detail=f"OpenSearch query error: {r.text}"
            )
        r.raise_for_status()
        data = r.json()
    except HTTPException:
        raise
    except requests.RequestException as e:
        raise HTTPException(
            status_code=503, detail=f"OpenSearch unavailable: {e}"
        ) from e

    hits = (((data or {}).get("hits") or {}).get("hits")) or []
    lexical: list[dict[str, Any]] = []
    sources: dict[str, dict] = {}
    lexical_scores: dict[str, Any] = {}
    highlights: dict[str, list[SearchHighlight]] = {}

    for h in hits:
        sid = h.get("_id")
        if not sid:
            continue
        sid = str(sid)

        lexical.append({"segment_id": sid, "score": float(h.get("_score") or 0.0)})

        if "_score" in h:
            lexical_scores[sid] = h.get("_score")

        src = h.get("_source")
        if isinstance(src, dict):
            sources[sid] = src

        hl = h.get("highlight")
        if isinstance(hl, dict):
            items = _highlight_to_items(hl)
            if items:
                highlights[sid] = items

    return lexical, sources, lexical_scores, highlights


def _opensearch_mget(ids: list[str]) -> dict[str, dict]:
    if not ids:
        return {}
    url = f"{_opensearch_url()}/{_segments_index()}/_mget"
    auth = _os_auth()

    try:
        with requests.Session() as session:
            session.trust_env = False
            r = session.post(url, json={"ids": ids}, timeout=10, auth=auth)
        if 400 <= r.status_code < 500:
            raise HTTPException(
                status_code=400, detail=f"OpenSearch mget error: {r.text}"
            )
        r.raise_for_status()
        data = r.json()
    except HTTPException:
        raise
    except requests.RequestException as e:
        raise HTTPException(
            status_code=503, detail=f"OpenSearch unavailable: {e}"
        ) from e

    docs = data.get("docs")
    if not isinstance(docs, list):
        return {}

    out: dict[str, dict] = {}
    for d in docs:
        if not isinstance(d, dict):
            continue
        sid = d.get("_id")
        found = d.get("found")
        src = d.get("_source")
        if sid and found and isinstance(src, dict):
            out[str(sid)] = src

    return out


def _run_search(req: SearchRequestV1) -> SearchResponseV1:
    query_text = (req.query or "").strip()
    mode = _parse_mode(req, query_text)

    f = _parse_filters(req.filters)
    fetch_n = min(MAX_LIMIT, req.limit + req.offset)

    lexical_body = build_lexical_query(
        query=query_text or None,
        filters={"__compiled__": f.to_opensearch_filters()},
        limit=fetch_n,
        offset=0,
    )

    lexical_hits, sources, lexical_scores, highlights = _opensearch_search(lexical_body)

    vector_hits: list[dict[str, Any]] = []
    vector_scores: dict[str, float] = {}

    if mode in ("semantic", "hybrid"):
        if not query_text:
            raise HTTPException(
                status_code=400, detail="semantic search requires a query"
            )
        try:
            v = vector_search(
                query_text=query_text,
                filters=f.model_dump(exclude_none=True),
                top_k=fetch_n,
            )
            vector_hits = [{"segment_id": x.segment_id, "score": x.score} for x in v]
            for x in v:
                vector_scores[str(x.segment_id)] = float(x.score)
        except VectorSearchError:
            vector_hits = []

    if mode == "semantic":
        merged = merge_results(lexical=[], vector=vector_hits)
    elif mode == "lexical":
        merged = merge_results(lexical=lexical_hits, vector=[])
    else:
        merged = merge_results(lexical=lexical_hits, vector=vector_hits)

    page = merged[req.offset : req.offset + req.limit]
    page_ids = [x.segment_id for x in page]

    missing_ids = [sid for sid in page_ids if sid not in sources]
    if missing_ids:
        sources.update(_opensearch_mget(missing_ids))

    items: list[SearchItem] = []
    for x in page:
        src = sources.get(x.segment_id) or {}
        segment = _segment_from_source(x.segment_id, src)

        lex = lexical_scores.get(x.segment_id)
        lex_score = float(lex) if isinstance(lex, (int, float)) else None
        vec_score = vector_scores.get(x.segment_id)

        items.append(
            SearchItem(
                segment=segment,
                video=None,
                speaker=None,
                highlights=highlights.get(x.segment_id),
                score=SearchScore(
                    combined=float(x.score),
                    lexical=lex_score,
                    vector=vec_score,
                    lexical_rank=x.lexical_rank,
                    vector_rank=x.vector_rank,
                ),
            )
        )

    # Deterministic response ordering: stable tie-breaks when scores collide.
    items.sort(
        key=lambda it: (
            -float(it.score.combined),
            str(it.segment.video_id),
            int(it.segment.start_ms),
            str(it.segment.id),
        )
    )

    total: int | None = len(merged)
    return SearchResponseV1(
        items=items,
        page=PageMeta(limit=req.limit, offset=req.offset, total=total),
    )


@router.post("", response_model=SearchResponseV1)
def search_post(req: SearchRequestV1) -> SearchResponseV1:
    return _run_search(req)


@router.get("", response_model=SearchResponseV1)
def search_get(
    q: str | None = Query(default=None),
    language: str | None = Query(default=None),
    source: str | None = Query(default=None),
    video_id: str | None = Query(default=None),
    speaker_id: str | None = Query(default=None),
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=MAX_LIMIT),
    offset: int = Query(default=0, ge=0),
    semantic: bool | None = Query(default=None),
    mode: Literal["lexical", "semantic", "hybrid"] | None = Query(default=None),
) -> SearchResponseV1:
    req = SearchRequestV1(
        query=q,
        filters=SearchFiltersModel(
            language=language,
            source=source,
            video_id=video_id,
            speaker_id=speaker_id,
            date_from=date_from,
            date_to=date_to,
        ),
        limit=limit,
        offset=offset,
        semantic=semantic,
        mode=mode,
    )
    return _run_search(req)
