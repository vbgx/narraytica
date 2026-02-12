from __future__ import annotations

from typing import Any

from faster_whisper import WhisperModel

from ..errors import ASR_ERR_TRANSCRIPTION_FAILED, AsrError
from ..types import TranscriptResult, TranscriptSegment


class FasterWhisperProvider:
    name = "faster_whisper"

    def __init__(self, *, model: str, device: str, compute_type: str) -> None:
        self._model_name = model
        self._device = device
        self._compute_type = compute_type
        self._model = WhisperModel(model, device=device, compute_type=compute_type)

    def transcribe(self, *, audio_path: str) -> TranscriptResult:
        try:
            segments_it, info = self._model.transcribe(audio_path)

            segments: list[TranscriptSegment] = []
            full_parts: list[str] = []

            for s in segments_it:
                text = (s.text or "").strip()
                if text:
                    full_parts.append(text)
                segments.append(
                    TranscriptSegment(
                        start_s=float(s.start),
                        end_s=float(s.end),
                        text=text,
                    )
                )

            raw: dict[str, Any] = {
                "model": self._model_name,
                "device": self._device,
                "compute_type": self._compute_type,
                "language": getattr(info, "language", None),
                "duration": getattr(info, "duration", None),
            }

            return TranscriptResult(
                text=" ".join(full_parts).strip(),
                language=getattr(info, "language", None),
                segments=segments,
                raw=raw,
            )
        except Exception as e:
            raise AsrError(ASR_ERR_TRANSCRIPTION_FAILED, str(e)) from e
