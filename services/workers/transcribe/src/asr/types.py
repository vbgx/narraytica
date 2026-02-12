from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TranscriptSegment:
    start_s: float
    end_s: float
    text: str


@dataclass(frozen=True)
class TranscriptResult:
    text: str
    language: str | None
    segments: list[TranscriptSegment]
    raw: dict[str, Any]
