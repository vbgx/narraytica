from __future__ import annotations

import uuid
from collections.abc import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from .request_context import set_request_id

REQUEST_ID_HEADER = "X-Request-Id"


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        rid = request.headers.get(REQUEST_ID_HEADER) or str(uuid.uuid4())

        # store in request.state (local access)
        request.state.request_id = rid

        # store in contextvar (global structured logging access)
        set_request_id(rid)

        response = await call_next(request)
        response.headers[REQUEST_ID_HEADER] = rid
        return response
