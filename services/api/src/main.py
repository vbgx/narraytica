from __future__ import annotations

from fastapi import FastAPI

from .config import settings
from .middleware import RateLimitMiddleware
from .routes import search as search_routes


def create_app() -> FastAPI:
    app = FastAPI(title="Narralytica API")

    # Middleware
    app.add_middleware(
        RateLimitMiddleware,
        enabled=settings.rate_limit_enabled,
        limit=settings.rate_limit_limit,
        window_seconds=settings.rate_limit_window_seconds,
        redis_url=settings.redis_url,
        path_prefix=settings.rate_limit_path_prefix,
    )

    # Routers
    app.include_router(search_routes.router, prefix="/api/v1")

    return app


app = create_app()
