from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, HTTPException, Query
from packages.application.errors import AppError
from packages.application.search.dtos import SearchQueryDTO
from packages.application.search.use_case import execute
from pydantic import BaseModel, Field

from services.api.src.search.adapter import opensearch_mget as _os_mget_impl
from services.api.src.search.adapter import opensearch_search as _os_search_impl
from services.api.src.search.qdrant.vector_search import (
    vector_search as _vector_search_impl,
)
from services.api.src.wiring.search_deps import build_search_deps

router = APIRouter(prefix="/search", tags=["search"])
MAX_LIMIT = 100


def _opensearch_search(body):
    return _os_search_impl(body)


def _opensearch_mget(ids):
    return _os_mget_impl(ids)


def vector_search(*, query_text: str, filters: dict | None, top_k: int):
    return _vector_search_impl(query_text=query_text, filters=filters, top_k=top_k)


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


def _http_from_app_error(e: AppError) -> HTTPException:
    status = 500
    if e.code == "validation_error":
        status = 400
    elif e.code == "not_found":
        status = 404
    elif e.code == "conflict":
        status = 409
    elif e.code == "unauthorized":
        status = 401
    elif e.code == "forbidden":
        status = 403
    elif e.code == "unavailable":
        status = 503
    return HTTPException(
        status_code=status,
        detail={"code": e.code, "message": e.message, "details": e.details},
    )


def _to_dto(req: SearchRequestV1) -> SearchQueryDTO:
    return SearchQueryDTO(
        query=req.query,
        filters=(req.filters.model_dump(exclude_none=True) if req.filters else None),
        limit=int(req.limit),
        offset=int(req.offset),
        mode=req.mode,
        semantic=req.semantic,
    )


def _run(req: SearchRequestV1) -> dict:
    try:
        out = execute(
            req=_to_dto(req),
            deps=build_search_deps(
                opensearch_search_fn=_opensearch_search,
                opensearch_mget_fn=_opensearch_mget,
                vector_impl=vector_search,
            ),
        )
        return out.data
    except AppError as e:
        raise _http_from_app_error(e) from e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@router.post("")
def search_post(req: SearchRequestV1) -> dict:
    return _run(req)


@router.get("")
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
) -> dict:
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
    return _run(req)
