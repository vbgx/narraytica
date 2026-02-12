from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class ApiVersionHeaderMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, api_version: str) -> None:
        super().__init__(app)
        self._api_version = api_version

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers.setdefault("X-API-Version", self._api_version)
        return response
