from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TranscriptResult:
    text: str
    language: str = "en"
    segments: list[dict[str, Any]] | None = None


class TestTranscriptionProvider:
    name = "test"

    def transcribe(
        self, *, audio_path: str, language_hint: str | None = None, **_: Any
    ) -> TranscriptResult:
        return TranscriptResult(
            text="Hello world. Deterministic transcript.",
            language=language_hint or "en",
            segments=[
                {"start_ms": 0, "end_ms": 1000, "text": "Hello world."},
                {"start_ms": 1000, "end_ms": 2500, "text": "Deterministic transcript."},
            ],
        )
