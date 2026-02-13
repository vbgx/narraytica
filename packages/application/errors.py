from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

ErrorCode = Literal[
    "validation_error",
    "not_found",
    "conflict",
    "unauthorized",
    "forbidden",
    "unavailable",
    "internal_error",
]


@dataclass(frozen=True)
class AppError(Exception):
    code: ErrorCode
    message: str
    details: Any | None = None
