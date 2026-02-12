from __future__ import annotations

from fastapi import FastAPI

from .config import settings
from .middleware import RateLimitMiddleware


def create_app() -> FastAPI:
    app = FastAPI(
        title="Narralytica API",
        version="v1",
    )

    # ------------------------------------------------------------------
    # Middleware
    # ------------------------------------------------------------------
    app.add_middleware(
        RateLimitMiddleware,
        enabled=settings.rate_limit_enabled,
        limit=settings.rate_limit_limit,
        window_seconds=settings.rate_limit_window_seconds,
        redis_url=settings.redis_url,
        path_prefix=settings.rate_limit_path_prefix,
    )

    # ------------------------------------------------------------------
    # API Routers (single entrypoint)
    # ------------------------------------------------------------------
    from .routes.v1 import router as v1_router

    app.include_router(v1_router)

    return app


# ASGI entrypoint
app = create_app()
