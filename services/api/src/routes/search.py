from __future__ import annotations

from typing import Any

import requests
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field, ValidationError

from ..config import settings
from ..domain.search_filters import SearchFiltersV1
from ..search.hybrid.merge import merge_results
from ..search.opensearch.lexical_query import build_lexical_query
from ..search.qdrant.vector_search import VectorSearchError, vector_search

router = APIRouter(prefix="/search", tags=["search"])

MAX_LIMIT = 100


class SearchRequest(BaseModel):
    query: str | None = Field(default=None)
    filters: dict | None = Field(default=None)
    limit: int = Field(default=20, ge=1, le=MAX_LIMIT)
    offset: int = Field(default=0, ge=0)
    semantic: bool | None = Field(
        default=None,
        description="If true, run vector search (requires non-empty query).",
    )


class SearchHit(BaseModel):
    segment_id: str
    score: float
    lexical_rank: int | None = None
    vector_rank: int | None = None
    source: dict[str, Any] | None = None


class SearchResponse(BaseModel):
    items: list[SearchHit]
    limit: int
    offset: int
    total: int


def parse_search_filters(filters: dict | None) -> SearchFiltersV1:
    try:
        return SearchFiltersV1.model_validate(filters or {})
    except (ValidationError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


def _opensearch_auth() -> tuple[str, str] | None:
    user = getattr(settings, "OPENSEARCH_USERNAME", None) or getattr(
        settings, "opensearch_username", None
    )
    pwd = getattr(settings, "OPENSEARCH_PASSWORD", None) or getattr(
        settings, "opensearch_password", None
    )
    if user and pwd:
        return (str(user), str(pwd))
    return None


def _opensearch_url() -> str:
    url = getattr(settings, "OPENSEARCH_URL", None) or getattr(
        settings, "opensearch_url", None
    )
    if not url:
        raise HTTPException(status_code=503, detail="OpenSearch not configured")
    return str(url).rstrip("/")


def _segments_index() -> str:
    return (
        getattr(settings, "OPENSEARCH_SEGMENTS_INDEX", None)
        or getattr(settings, "opensearch_segments_index", None)
        or "narralytica-segments-v1"
    )


def _request_timeout() -> float:
    t = getattr(settings, "OPENSEARCH_TIMEOUT_SECONDS", None) or getattr(
        settings, "opensearch_timeout_seconds", None
    )
    try:
        return float(t) if t is not None else 10.0
    except Exception:
        return 10.0


def _opensearch_search(
    body: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, dict]]:
    url = f"{_opensearch_url()}/{_segments_index()}/_search"
    auth = _opensearch_auth()

    try:
        r = requests.post(
            url,
            json=body,
            timeout=_request_timeout(),
            auth=auth,
        )
        r.raise_for_status()
        data = r.json()
    except requests.RequestException as e:
        raise HTTPException(
            status_code=503,
            detail=f"OpenSearch unavailable: {e}",
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"OpenSearch error: {e}",
        ) from e

    hits = (((data or {}).get("hits") or {}).get("hits")) or []
    lexical: list[dict[str, Any]] = []
    sources_by_id: dict[str, dict] = {}

    for h in hits:
        if not isinstance(h, dict):
            continue
        sid = h.get("_id") or (h.get("_source") or {}).get("id")
        if sid is None:
            continue
        sid_s = str(sid)
        lexical.append({"segment_id": sid_s})
        src = h.get("_source")
        if isinstance(src, dict):
            sources_by_id[sid_s] = src

    return lexical, sources_by_id


def _run_search(req: SearchRequest) -> SearchResponse:
    f = parse_search_filters(req.filters)

    query_text = (req.query or "").strip()
    semantic = req.semantic
    if semantic is None:
        semantic = bool(query_text)

    if semantic and not query_text:
        raise HTTPException(
            status_code=400,
            detail="semantic search requires a non-empty query",
        )

    fetch_n = min(MAX_LIMIT, req.limit + req.offset)

    lexical_body = build_lexical_query(
        query=query_text if query_text else None,
        filters={"__compiled__": f.to_opensearch_filters()},
        limit=fetch_n,
        offset=0,
    )
    lexical_hits, sources_by_id = _opensearch_search(lexical_body)

    vector_hits: list[dict[str, Any]] = []
    if semantic:
        try:
            v = vector_search(
                query_text=query_text,
                filters=f.model_dump(exclude_none=True),
                top_k=fetch_n,
            )
            vector_hits = [{"segment_id": x.segment_id, "score": x.score} for x in v]
        except VectorSearchError as e:
            raise HTTPException(status_code=503, detail=str(e)) from e

    merged = merge_results(lexical=lexical_hits, vector=vector_hits)

    page = merged[req.offset : req.offset + req.limit]
    out_items: list[SearchHit] = []
    for it in page:
        out_items.append(
            SearchHit(
                segment_id=it.segment_id,
                score=it.score,
                lexical_rank=it.lexical_rank,
                vector_rank=it.vector_rank,
                source=sources_by_id.get(it.segment_id),
            )
        )

    return SearchResponse(
        items=out_items,
        limit=req.limit,
        offset=req.offset,
        total=len(merged),
    )


@router.get("", response_model=SearchResponse)
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
) -> SearchResponse:
    req = SearchRequest(
        query=q,
        filters={
            "language": language,
            "source": source,
            "video_id": video_id,
            "speaker_id": speaker_id,
            "date_from": date_from,
            "date_to": date_to,
        },
        limit=limit,
        offset=offset,
        semantic=semantic,
    )
    return _run_search(req)


@router.post("", response_model=SearchResponse)
def search_post(req: SearchRequest) -> SearchResponse:
    return _run_search(req)
