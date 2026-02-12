from __future__ import annotations

import logging

from fastapi import FastAPI

from .config import settings
from .routes.health import router as health_router
from .routes.metrics import router as metrics_router
from .routes.v1 import router as v1_router
from .telemetry.api_version import ApiVersionHeaderMiddleware
from .telemetry.http_logging import HttpLoggingMiddleware
from .telemetry.logging import setup_logging
from .telemetry.otel import setup_otel
from .telemetry.request_id import RequestIdMiddleware

logger = logging.getLogger(__name__)


def _is_truthy(value: object) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def create_app() -> FastAPI:
    setup_logging(settings.log_level)

    otel_enabled = _is_truthy(getattr(settings, "otel_enabled", False))
    otlp_endpoint = getattr(
        settings,
        "otel_exporter_otlp_endpoint",
        "http://localhost:4318",
    )

    setup_otel(
        service_name=getattr(settings, "service_name", "narralytica-api"),
        enabled=otel_enabled,
        otlp_endpoint=otlp_endpoint,
    )

    app = FastAPI(
        title="Narralytica API",
        version="1.0.0",
    )

    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(HttpLoggingMiddleware)
    app.add_middleware(ApiVersionHeaderMiddleware, api_version="v1")

    # System endpoints (not versioned)
    app.include_router(health_router, tags=["system"])
    app.include_router(metrics_router, tags=["system"])

    # Public API v1
    app.include_router(v1_router)

    if otel_enabled:
        try:
            from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

            FastAPIInstrumentor.instrument_app(app)
        except Exception as e:
            logger.warning(
                "otel_instrumentation_failed",
                extra={"error": str(e)},
            )

    logger.info("api_start")
    return app


app = create_app()
