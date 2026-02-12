from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter(tags=["videos"])


# -----------------------------------------------------------------------------
# Contract models (API response surface)
# -----------------------------------------------------------------------------
class PageMeta(BaseModel):
    limit: int
    offset: int
    total: int


class VideoV1(BaseModel):
    """
    Contract-facing video representation.

    NOTE: keep this in sync with packages/contracts/schemas/video.schema.json.
    """

    video_id: str = Field(..., description="Canonical video id")

    status: str = Field(
        ...,
        description="Processing status (queued|processing|done|failed)",
    )
    created_at: datetime = Field(..., description="RFC3339 timestamp")

    # Optional common fields (fill when DB layer provides them)
    source: dict[str, Any] | None = None
    artifacts: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None


class VideosListResponseV1(BaseModel):
    items: list[VideoV1]
    page: PageMeta


# -----------------------------------------------------------------------------
# Filters + pagination
# -----------------------------------------------------------------------------
MAX_LIMIT = 100


class VideoListFilters(BaseModel):
    status: str | None = None
    created_after: datetime | None = None
    created_before: datetime | None = None


def _parse_filters(
    status: str | None,
    created_after: datetime | None,
    created_before: datetime | None,
) -> VideoListFilters:
    if created_after and created_before and created_before <= created_after:
        raise HTTPException(
            status_code=400,
            detail="created_before must be > created_after",
        )

    return VideoListFilters(
        status=status.strip() if status and status.strip() else None,
        created_after=created_after,
        created_before=created_before,
    )


# -----------------------------------------------------------------------------
# Repository abstraction (keep routes thin)
# -----------------------------------------------------------------------------
class VideosRepo:
    def list_videos(
        self,
        *,
        filters: VideoListFilters,
        limit: int,
        offset: int,
    ) -> tuple[list[VideoV1], int]:
        raise NotImplementedError

    def get_video(self, *, video_id: str) -> VideoV1 | None:
        raise NotImplementedError


def get_videos_repo() -> VideosRepo:
    """
    Wire this to your real repo (DB/ORM) implementation.
    Keeping a tiny interface makes routes stable and testable.
    """
    from ..services.videos_repo import get_repo  # local import to avoid cycles

    return get_repo()


# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------
@router.get("/videos", response_model=VideosListResponseV1)
def list_videos(
    status: str | None = Query(default=None),  # noqa: B008 (FastAPI standard)
    created_after: datetime | None = Query(default=None),  # noqa: B008
    created_before: datetime | None = Query(default=None),  # noqa: B008
    limit: int = Query(default=20, ge=1, le=MAX_LIMIT),  # noqa: B008
    offset: int = Query(default=0, ge=0),  # noqa: B008
    repo: VideosRepo = Depends(get_videos_repo),  # noqa: B008
) -> VideosListResponseV1:
    f = _parse_filters(status, created_after, created_before)
    items, total = repo.list_videos(filters=f, limit=limit, offset=offset)

    return VideosListResponseV1(
        items=items,
        page=PageMeta(limit=limit, offset=offset, total=total),
    )


@router.get("/videos/{video_id}", response_model=VideoV1)
def get_video(
    video_id: str,
    repo: VideosRepo = Depends(get_videos_repo),  # noqa: B008
) -> VideoV1:
    v = repo.get_video(video_id=video_id)
    if not v:
        raise HTTPException(status_code=404, detail="Video not found")
    return v
