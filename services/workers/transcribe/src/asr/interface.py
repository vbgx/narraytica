from __future__ import annotations

from typing import Protocol

from .types import TranscriptResult


class AsrProvider(Protocol):
    name: str

    def transcribe(self, *, audio_path: str) -> TranscriptResult: ...
