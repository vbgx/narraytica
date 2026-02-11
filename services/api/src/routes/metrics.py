from __future__ import annotations

from fastapi import APIRouter
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from starlette.responses import Response

router = APIRouter()


@router.get("/metrics", include_in_schema=False)
def metrics() -> Response:
    payload = generate_latest()
    return Response(content=payload, media_type=CONTENT_TYPE_LATEST)
