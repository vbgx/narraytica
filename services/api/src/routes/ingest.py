from __future__ import annotations

from typing import Literal
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, HttpUrl

from ..domain.ingestion_contract import IngestionJobPayload
from ..domain.ingestion_validation import normalize_url, validate_source_fields

router = APIRouter()


class IngestSourceRequest(BaseModel):
    kind: Literal["youtube", "upload", "external_url"]
    url: HttpUrl | None = None
    upload_ref: str | None = None
    provider: str | None = None
    submitted_by: str | None = None


class IngestRequest(BaseModel):
    source: IngestSourceRequest
    metadata: dict | None = None


@router.post("/ingest", status_code=201)
async def create_ingestion_job(request: IngestRequest):
    try:
        source = request.source.dict()

        validate_source_fields(request.source)

        video_id = str(uuid4())
        job_id = str(uuid4())

        if source["kind"] in ("youtube", "external_url"):
            dedupe_key = normalize_url(source["url"])
            strategy = "source_url"
        else:
            dedupe_key = source["upload_ref"]
            strategy = "upload_hash"

        job_payload = IngestionJobPayload(
            type="video_ingestion",
            version="2.0",
            video_id=video_id,
            source=source,
            dedupe={"strategy": strategy, "key": dedupe_key},
            artifacts={
                "video": {
                    "bucket": "raw-videos",
                    "object_key": f"videos/{video_id}/source.mp4",
                },
                "audio": {
                    "bucket": "audio-tracks",
                    "object_key": f"videos/{video_id}/audio.wav",
                    "format": "wav",
                },
            },
            metadata={
                "expected_outputs": ["video_file", "audio_file"],
                "capture_source_metadata": True,
            },
        )

        job_payload_dict = job_payload.model_dump()

        return {
            "job_id": job_id,
            "video_id": video_id,
            "status": "queued",
            "payload_version": job_payload_dict["version"],
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
