from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from ..services.segments_repo import SegmentsRepo, SegmentV1, get_segments_repo

MAX_LIMIT = 100

router = APIRouter(prefix="/segments", tags=["segments"])


class PageMeta(BaseModel):
    limit: int
    offset: int
    total: int


class SegmentResponse(BaseModel):
    start_ms: int = Field(..., ge=0)
    end_ms: int = Field(..., ge=0)
    text: str
    words: list[dict] | None = None


class SegmentsListResponse(BaseModel):
    items: list[SegmentResponse]
    page: PageMeta


def _clamp_limit(limit: int) -> int:
    return max(1, min(limit, MAX_LIMIT))


def _to_segment_response(s: SegmentV1) -> SegmentResponse:
    return SegmentResponse(
        start_ms=s.start_ms,
        end_ms=s.end_ms,
        text=s.text,
        words=[
            {
                "start_ms": w.start_ms,
                "end_ms": w.end_ms,
                "text": w.text,
                "confidence": w.confidence,
            }
            for w in (s.words or [])
        ]
        if s.words
        else None,
    )


@router.get("", response_model=SegmentsListResponse)
def list_segments(
    video_id: str | None = Query(default=None),
    speaker_id: str | None = Query(default=None),
    start_ms_gte: int | None = Query(default=None, ge=0),
    end_ms_lte: int | None = Query(default=None, ge=0),
    limit: int = Query(default=20, ge=1, le=MAX_LIMIT),
    offset: int = Query(default=0, ge=0),
) -> SegmentsListResponse:
    if start_ms_gte is not None and end_ms_lte is not None:
        if end_ms_lte <= start_ms_gte:
            raise HTTPException(
                status_code=400,
                detail="end_ms_lte must be > start_ms_gte",
            )

    repo: SegmentsRepo = get_segments_repo()

    limit = _clamp_limit(limit)

    items, total = repo.list_segments(
        video_id=video_id,
        speaker_id=speaker_id,
        start_ms_gte=start_ms_gte,
        end_ms_lte=end_ms_lte,
        limit=limit,
        offset=offset,
    )

    return SegmentsListResponse(
        items=[_to_segment_response(s) for s in items],
        page=PageMeta(limit=limit, offset=offset, total=total),
    )


@router.get("/{segment_id}", response_model=SegmentResponse)
def get_segment(segment_id: str) -> SegmentResponse:
    repo: SegmentsRepo = get_segments_repo()

    s = repo.get_segment(segment_id)
    if not s:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "resource_not_found",
                    "message": "Segment not found",
                    "details": {"segment_id": segment_id},
                    "correlation_id": None,
                }
            },
        )

    return _to_segment_response(s)
