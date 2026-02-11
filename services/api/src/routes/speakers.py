from __future__ import annotations

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/speakers", tags=["speakers"])


@router.get("")
def list_speakers() -> list[dict]:
    # Returns Speaker[] (canonical)
    return []


@router.get("/{speaker_id}")
def get_speaker(speaker_id: str) -> dict:
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
