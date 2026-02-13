from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ListJobsQueryDTO:
    limit: int = 50
    offset: int = 0


@dataclass(frozen=True)
class ListJobEventsQueryDTO:
    job_id: str
    limit: int = 50
    offset: int = 0


def as_dict(x: Any) -> dict[str, Any]:
    if isinstance(x, dict):
        return x
    raise TypeError(f"expected dict, got {type(x).__name__}")
