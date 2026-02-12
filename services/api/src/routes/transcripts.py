from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..services.transcripts_repo import TranscriptsRepo

router = APIRouter(prefix="/transcripts", tags=["transcripts"])


class TranscriptV1(BaseModel):
    transcript_id: str | None = Field(default=None)
    video_id: str
    provider: str
    language: str | None = Field(default=None)
    text: str
    segments: list[dict[str, Any]] = Field(default_factory=list)
    audio_ref: dict[str, Any]
    storage_ref: dict[str, Any]
    asr: dict[str, Any] | None = Field(default=None)
    created_at: datetime | None = Field(default=None)


def _not_found(
    transcript_id: str | None = None, video_id: str | None = None
) -> HTTPException:
    details: dict[str, Any] = {}
    if transcript_id:
        details["transcript_id"] = transcript_id
    if video_id:
        details["video_id"] = video_id
    return HTTPException(
        status_code=404,
        detail={
            "error": {
                "code": "resource_not_found",
                "message": "Transcript not found",
                "details": details,
                "correlation_id": None,
            }
        },
    )


@router.get("/{transcript_id}", response_model=TranscriptV1)
def get_transcript(transcript_id: str) -> TranscriptV1:
    repo = TranscriptsRepo()
    rec = repo.get_by_id(transcript_id)
    if not rec:
        raise _not_found(transcript_id=transcript_id)

    return TranscriptV1(
        transcript_id=rec.transcript_id,
        video_id=rec.video_id,
        provider=rec.provider,
        language=rec.language,
        text=rec.text,
        segments=rec.segments,
        audio_ref=rec.audio_ref,
        storage_ref=rec.storage_ref,
        asr=rec.asr,
        created_at=rec.created_at,
    )


@router.get("", response_model=TranscriptV1)
def get_latest_transcript(
    video_id: str,
    artifact_bucket: str | None = None,
    artifact_key: str | None = None,
) -> TranscriptV1:
    repo = TranscriptsRepo()
    rec = repo.latest_for_video(
        video_id=video_id,
        artifact_bucket=artifact_bucket,
        artifact_key=artifact_key,
    )
    if not rec:
        raise _not_found(video_id=video_id)

    return TranscriptV1(
        transcript_id=rec.transcript_id,
        video_id=rec.video_id,
        provider=rec.provider,
        language=rec.language,
        text=rec.text,
        segments=rec.segments,
        audio_ref=rec.audio_ref,
        storage_ref=rec.storage_ref,
        asr=rec.asr,
        created_at=rec.created_at,
    )
