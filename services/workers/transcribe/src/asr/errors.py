from __future__ import annotations


class AsrError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


ASR_ERR_PROVIDER_UNAVAILABLE = "asr_provider_unavailable"
ASR_ERR_AUDIO_REF_MISSING = "asr_audio_ref_missing"
ASR_ERR_AUDIO_DOWNLOAD_FAILED = "asr_audio_download_failed"
ASR_ERR_TRANSCRIPTION_FAILED = "asr_transcription_failed"
