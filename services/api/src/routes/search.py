from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, HTTPException, Query
from packages.application.errors import AppError
from packages.application.search.dtos import SearchQueryDTO
from pydantic import BaseModel, Field

from services.api.src.wiring.search import run_search

router = APIRouter(prefix="/search", tags=["search"])
MAX_LIMIT = 100


# ---------------------------------------------------------------------
# Backward-compat shims for existing tests.
# Tests may monkeypatch these names; route forwards them to wiring.
# ---------------------------------------------------------------------


def _opensearch_search(body: Any):
    raise RuntimeError("_opensearch_search shim should be monkeypatched in tests")


def _opensearch_mget(ids: Any):
    raise RuntimeError("_opensearch_mget shim should be monkeypatched in tests")


def vector_search(*, query_text: str, filters: dict | None, top_k: int):
    raise RuntimeError("vector_search shim should be monkeypatched in tests")


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
    status_code = 500
    if e.code == "validation_error":
        status_code = 400
    elif e.code == "not_found":
        status_code = 404
    elif e.code == "conflict":
        status_code = 409
    elif e.code == "unauthorized":
        status_code = 401
    elif e.code == "forbidden":
        status_code = 403
    elif e.code == "unavailable":
        status_code = 503
    return HTTPException(
        status_code=status_code,
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
        return run_search(
            _to_dto(req),
            opensearch_search_fn=_opensearch_search,
            opensearch_mget_fn=_opensearch_mget,
            vector_impl=vector_search,
        )
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
