from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/segments", tags=["segments"])


@router.get("")
def list_segments(transcript_id: str | None = Query(default=None)) -> list[dict]:
    # Returns Segment[] (canonical)
    return []


@router.get("/{segment_id}")
def get_segment(segment_id: str) -> dict:
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
