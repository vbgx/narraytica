import os

from .test_provider import TestTranscriptionProvider


def get_provider():
    name = (os.getenv("TRANSCRIPTION_PROVIDER") or "test").strip().lower()
    if name == "test":
        return TestTranscriptionProvider()
    raise ValueError(f"Unknown TRANSCRIPTION_PROVIDER={name}")
