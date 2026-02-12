from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from ..services.speakers_repo import SpeakersRepo, SpeakerV1, get_speakers_repo

router = APIRouter(prefix="/speakers", tags=["speakers"])

MAX_LIMIT = 200


class PageMeta(BaseModel):
    limit: int = Field(..., ge=1)
    offset: int = Field(..., ge=0)
    total: int = Field(..., ge=0)


class SpeakerResponse(BaseModel):
    speaker_id: str
    video_id: str
    label: str | None = None
    name: str | None = None
    language: str | None = None
    metadata: dict | None = None
    created_at: datetime | None = None


class SpeakersListResponse(BaseModel):
    items: list[SpeakerResponse]
    page: PageMeta


def _to_response(s: SpeakerV1) -> SpeakerResponse:
    return SpeakerResponse(
        speaker_id=s.speaker_id,
        video_id=s.video_id,
        label=s.label,
        name=s.name,
        language=s.language,
        metadata=s.metadata,
        created_at=s.created_at,
    )


@router.get("")
def list_speakers(
    video_id: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=MAX_LIMIT),
    offset: int = Query(default=0, ge=0),
) -> SpeakersListResponse:
    repo: SpeakersRepo = get_speakers_repo()
    items, total = repo.list_speakers(
        video_id=video_id,
        limit=limit,
        offset=offset,
    )
    return SpeakersListResponse(
        items=[_to_response(s) for s in items],
        page=PageMeta(limit=limit, offset=offset, total=total),
    )


@router.get("/{speaker_id}")
def get_speaker(
    speaker_id: str,
) -> SpeakerResponse:
    repo: SpeakersRepo = get_speakers_repo()
    s = repo.get_speaker(speaker_id)
    if not s:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "resource_not_found",
                    "message": "Speaker not found",
                    "details": {"speaker_id": speaker_id},
                    "correlation_id": None,
                }
            },
        )
    return _to_response(s)
