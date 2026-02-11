from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/videos", tags=["videos"])


def _now() -> str:
    return datetime.now(UTC).isoformat()


@router.get("")
def list_videos() -> list[dict]:
    # Explicit partial view: VideoSummary (see OpenAPI)
    return []


@router.get("/{video_id}")
def get_video(video_id: str) -> dict:
    # Return documented error model (resource_not_found)
    raise HTTPException(
        status_code=404,
        detail={
            "error": {
                "code": "resource_not_found",
                "message": "Video not found",
                "details": {"video_id": video_id},
                "correlation_id": None,
            }
        },
    )
