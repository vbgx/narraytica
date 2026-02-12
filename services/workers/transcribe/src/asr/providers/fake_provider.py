from __future__ import annotations

from asr.types import TranscriptResult, TranscriptSegment


class TestAsrProvider:
    """
    Deterministic fake ASR provider for integration tests.
    - No external dependencies
    - Always returns the same transcript + segments
    """

    name = "test"

    def __init__(self) -> None:
        pass

    def transcribe(self, *, audio_path: str) -> TranscriptResult:
        # Fixed output to keep tests deterministic and flake-free
        segments = [
            TranscriptSegment(start_s=0.0, end_s=0.5, text="bonjour"),
            TranscriptSegment(start_s=0.5, end_s=1.2, text="à tous"),
        ]
        text = "bonjour à tous"

        raw = {
            "provider": "test",
            "audio_path": audio_path,
            "duration": 1.2,
            "language": "fr",
        }

        return TranscriptResult(
            text=text,
            language="fr",
            segments=segments,
            raw=raw,
        )
