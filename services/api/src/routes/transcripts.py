from __future__ import annotations

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/transcripts", tags=["transcripts"])


@router.get("")
def list_transcripts() -> list[dict]:
    # TranscriptSummary (see OpenAPI)
    return []


@router.get("/{transcript_id}")
def get_transcript(transcript_id: str) -> dict:
    raise HTTPException(
        status_code=404,
        detail={
            "error": {
                "code": "resource_not_found",
                "message": "Transcript not found",
                "details": {"transcript_id": transcript_id},
                "correlation_id": None,
            }
        },
    )
