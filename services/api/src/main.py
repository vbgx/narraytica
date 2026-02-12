from __future__ import annotations

from fastapi import FastAPI

from .config import settings
from .middleware import RateLimitMiddleware


def create_app() -> FastAPI:
    app = FastAPI(title="Narralytica API")

    app.add_middleware(
        RateLimitMiddleware,
        enabled=settings.rate_limit_enabled,
        limit=settings.rate_limit_limit,
        window_seconds=settings.rate_limit_window_seconds,
        redis_url=settings.redis_url,
        path_prefix=settings.rate_limit_path_prefix,
    )

    from .routes import ingest, search, transcripts, videos

    app.include_router(ingest.router, prefix="/api/v1")
    app.include_router(search.router, prefix="/api/v1")
    app.include_router(videos.router, prefix="/api/v1")
    app.include_router(transcripts.router, prefix="/api/v1")

    return app


app = create_app()
