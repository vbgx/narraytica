import logging
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from settings import settings
from telemetry.logging import setup_logging
from routes.health import router as health_router

log = logging.getLogger("api")

def create_app() -> FastAPI:
    setup_logging(settings.log_level)

    app = FastAPI(title="Narralytica API", version="0.0.0")

    app.include_router(health_router)

    @app.middleware("http")
    async def request_logging(request: Request, call_next):
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        request.state.request_id = request_id

        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            duration_ms = int((time.perf_counter() - start) * 1000)
            log.exception("request_failed", extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": 500,
                "duration_ms": duration_ms,
            })
            return JSONResponse(status_code=500, content={"error": {"code": "internal_error", "request_id": request_id}})

        duration_ms = int((time.perf_counter() - start) * 1000)
        log.info("request", extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        })

        response.headers["x-request-id"] = request_id
        return response

    return app

app = create_app()

# ---- OpenSearch bootstrap (EPIC 00 / 00.07) ----
from search.opensearch.bootstrap import bootstrap_opensearch  # noqa: E402


@app.on_event("startup")
def _startup_search_bootstrap() -> None:
    bootstrap_opensearch()
