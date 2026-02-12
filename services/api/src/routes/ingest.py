from __future__ import annotations

from hashlib import sha256
from typing import Any, Literal
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, HttpUrl

from ..domain.ingestion_contract import IngestionJobPayload
from ..domain.ingestion_validation import normalize_url, validate_source_fields
from ..services.idempotency import IdempotencyStore, get_idempotency_store

router = APIRouter(tags=["ingest"])


# -----------------------------------------------------------------------------
# Actor dependency (API key identity)
# -----------------------------------------------------------------------------
class Actor(BaseModel):
    api_key_id: str = "anon"


def get_actor() -> Actor:
    """
    Return an Actor with api_key_id.

    Production wiring: replace this body with your API-key auth dependency.
    Tests/local-dev: fallback to "anon".
    """
    try:
        # If you already have an auth dependency, wire it here.
        # Example (adjust to your codebase):
        # from ..auth.deps import require_api_key
        # a = require_api_key()
        # api_key_id = (
        #     getattr(a, "api_key_id", None)
        #     or getattr(a, "id", None)
        #     or "anon"
        # )
        # return Actor(api_key_id=str(api_key_id))
        return Actor()
    except Exception:
        return Actor()


# -----------------------------------------------------------------------------
# Request/Response contract (API surface)
# -----------------------------------------------------------------------------
class IngestSourceRequest(BaseModel):
    kind: Literal["youtube", "upload", "external_url"]

    url: HttpUrl | None = None
    upload_ref: str | None = None

    provider: str | None = None
    submitted_by: str | None = None


class IngestRequestV2(BaseModel):
    external_id: str | None = Field(default=None, max_length=200)
    source: IngestSourceRequest
    metadata: dict[str, Any] | None = None


class IngestResponseV2(BaseModel):
    job_id: str
    video_id: str
    status: Literal["queued"]
    payload_version: str
    idempotent_replay: bool = False


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def _dedupe_from_source(source: dict[str, Any]) -> dict[str, str]:
    if source["kind"] in ("youtube", "external_url"):
        dedupe_key = normalize_url(source["url"])
        strategy = "source_url"
    else:
        dedupe_key = source["upload_ref"]
        strategy = "upload_hash"
    return {"strategy": strategy, "key": str(dedupe_key)}


def _canonical_artifacts(video_id: str) -> dict[str, Any]:
    return {
        "video": {
            "bucket": "raw-videos",
            "object_key": f"videos/{video_id}/source.mp4",
        },
        "audio": {
            "bucket": "audio-tracks",
            "object_key": f"videos/{video_id}/audio.wav",
            "format": "wav",
        },
    }


def _idempotency_key(api_key_id: str, external_id: str) -> str:
    raw = f"{api_key_id}:{external_id}".encode()
    return sha256(raw).hexdigest()


# -----------------------------------------------------------------------------
# Route
# -----------------------------------------------------------------------------
@router.post("/ingest", response_model=IngestResponseV2, status_code=201)
async def create_ingestion_job(
    request: IngestRequestV2,
    actor: Actor = Depends(get_actor),  # noqa: B008
    store: IdempotencyStore = Depends(get_idempotency_store),  # noqa: B008
) -> IngestResponseV2:
    try:
        validate_source_fields(request.source)

        # Idempotency if external_id is provided
        idem_key: str | None = None
        if request.external_id:
            idem_key = _idempotency_key(actor.api_key_id, request.external_id)
            existing = store.get(idem_key)
            if existing:
                existing = dict(existing)
                existing["idempotent_replay"] = True
                return IngestResponseV2(**existing)

        video_id = str(uuid4())
        job_id = str(uuid4())

        source = request.source.model_dump()

        job_payload = IngestionJobPayload(
            type="video_ingestion",
            version="2.0",
            video_id=video_id,
            source=source,
            dedupe=_dedupe_from_source(source),
            artifacts=_canonical_artifacts(video_id),
            metadata=request.metadata,
        )
        _ = job_payload  # constructed + validated (future: publish/enqueue)

        out = IngestResponseV2(
            job_id=job_id,
            video_id=video_id,
            status="queued",
            payload_version="2.0",
        )

        if idem_key:
            store.set(idem_key, out.model_dump())

        return out

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
