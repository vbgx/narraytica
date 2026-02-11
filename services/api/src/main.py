from __future__ import annotations

import logging

from config import settings
from fastapi import FastAPI
from routes.health import router as health_router
from routes.jobs import router as jobs_router
from routes.metrics import router as metrics_router
from routes.segments import router as segments_router
from routes.speakers import router as speakers_router
from routes.transcripts import router as transcripts_router
from routes.videos import router as videos_router
from telemetry.http_logging import HttpLoggingMiddleware
from telemetry.logging import setup_logging
from telemetry.otel import setup_otel
from telemetry.request_id import RequestIdMiddleware

logger = logging.getLogger(__name__)


def _is_truthy(v: object) -> bool:
    return str(v).strip().lower() in ("1", "true", "yes", "on")


def create_app() -> FastAPI:
    setup_logging(settings.log_level)

    otel_enabled = _is_truthy(getattr(settings, "otel_enabled", False))
    otlp_endpoint = getattr(
        settings, "otel_exporter_otlp_endpoint", "http://localhost:4318"
    )

    setup_otel(
        service_name=getattr(settings, "service_name", "narralytica-api"),
        enabled=otel_enabled,
        otlp_endpoint=otlp_endpoint,
    )

    app = FastAPI(title="Narralytica API", version="0.0.0")

    # Correlation + access logs
    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(HttpLoggingMiddleware)

    # System routes
    app.include_router(health_router)
    app.include_router(metrics_router)

    # Domain routes (canonical models)
    app.include_router(videos_router)
    app.include_router(transcripts_router)
    app.include_router(segments_router)
    app.include_router(speakers_router)
    app.include_router(jobs_router)

    # OTel instrumentation (safe, opt-in)
    if otel_enabled:
        try:
            from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

            FastAPIInstrumentor.instrument_app(app)
        except Exception as e:
            logger.warning("otel_instrumentation_failed", extra={"error": str(e)})

    logger.info("api_start")
    return app


app = create_app()
