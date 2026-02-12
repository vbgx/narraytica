from __future__ import annotations

import json
import os
import subprocess
import sys
from typing import Any

from .errors import (
    ASR_ERR_TRANSCRIPTION_FAILED,
    ASR_ERR_TRANSCRIPTION_TIMEOUT,
    AsrError,
)
from .registry import get_provider
from .types import TranscriptResult, TranscriptSegment


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if not raw:
        return default
    try:
        return int(raw)
    except Exception:
        return default


def transcribe_with_timeout(
    *,
    audio_path: str,
    timeout_s: float | None,
) -> TranscriptResult:
    """
    Run ASR with an optional hard timeout.
    For faster_whisper we use a subprocess so we can enforce timeout reliably.
    """
    provider = get_provider()

    # No timeout requested
    if not timeout_s or timeout_s <= 0:
        return provider.transcribe(audio_path=audio_path)

    # Hard-timeout path for faster_whisper (local compute can hang on long files)
    if getattr(provider, "name", None) == "faster_whisper":
        model = os.getenv("FASTER_WHISPER_MODEL", "small").strip()
        device = os.getenv("FASTER_WHISPER_DEVICE", "cpu").strip()
        compute = os.getenv("FASTER_WHISPER_COMPUTE_TYPE", "int8").strip()

        cmd = [
            sys.executable,
            "-m",
            "services.workers.transcribe.src.asr.subprocess_faster_whisper",
            "--audio-path",
            audio_path,
            "--model",
            model,
            "--device",
            device,
            "--compute-type",
            compute,
        ]

        try:
            cp = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=float(timeout_s),
                check=False,
            )
        except subprocess.TimeoutExpired as e:
            raise AsrError(
                ASR_ERR_TRANSCRIPTION_TIMEOUT,
                f"attempt_timeout_s={timeout_s}",
            ) from e

        if cp.returncode != 0:
            msg = (cp.stderr or cp.stdout or "").strip()
            raise AsrError(ASR_ERR_TRANSCRIPTION_FAILED, msg or "subprocess_failed")

        try:
            data = json.loads((cp.stdout or "").strip())
        except Exception as e:
            raise AsrError(
                ASR_ERR_TRANSCRIPTION_FAILED,
                "invalid_subprocess_json",
            ) from e

        segs = [
            TranscriptSegment(
                start_s=float(s.get("start_s", 0.0)),
                end_s=float(s.get("end_s", 0.0)),
                text=str(s.get("text", "")),
            )
            for s in (data.get("segments") or [])
        ]
        raw: dict[str, Any] = data.get("raw") or {}
        return TranscriptResult(
            text=str(data.get("text") or ""),
            language=data.get("language"),
            segments=segs,
            raw=raw,
        )

    # Fallback: provider has no enforceable hard timeout path (best-effort)
    return provider.transcribe(audio_path=audio_path)
