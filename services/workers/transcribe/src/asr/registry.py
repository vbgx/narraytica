from __future__ import annotations

import os

from .errors import ASR_ERR_PROVIDER_UNAVAILABLE, AsrError
from .interface import AsrProvider
from .providers.fake_provider import TestAsrProvider
from .providers.faster_whisper_provider import FasterWhisperProvider


def get_provider() -> AsrProvider:
    provider = os.getenv("ASR_PROVIDER", "faster_whisper").strip()

    if provider == "test":
        return TestAsrProvider()

    if provider == "faster_whisper":
        model = os.getenv("FASTER_WHISPER_MODEL", "small").strip()
        device = os.getenv("FASTER_WHISPER_DEVICE", "cpu").strip()
        compute = os.getenv("FASTER_WHISPER_COMPUTE_TYPE", "int8").strip()
        return FasterWhisperProvider(model=model, device=device, compute_type=compute)

    raise AsrError(ASR_ERR_PROVIDER_UNAVAILABLE, f"unknown ASR_PROVIDER={provider}")
