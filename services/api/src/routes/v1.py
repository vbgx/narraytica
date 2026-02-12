from __future__ import annotations

from fastapi import APIRouter, Depends

from ..auth.deps import require_api_key
from .ingest import router as ingest_router  # EPIC-02
from .jobs import router as jobs_router
from .search import router as search_router
from .segments import router as segments_router
from .speakers import router as speakers_router
from .transcripts import router as transcripts_router
from .videos import router as videos_router

API_V1_PREFIX = "/api/v1"

router = APIRouter(
    prefix=API_V1_PREFIX,
    dependencies=[Depends(require_api_key)],
)

router.include_router(ingest_router, tags=["ingestion"])
router.include_router(videos_router, tags=["videos"])
router.include_router(transcripts_router, tags=["transcripts"])
router.include_router(segments_router, tags=["segments"])
router.include_router(speakers_router, tags=["speakers"])
router.include_router(jobs_router, tags=["jobs"])
router.include_router(search_router, tags=["search"])
