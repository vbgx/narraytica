import pytest

pytest.skip(
    "No runtime worker under services/workers/transcription/. "
    "The actual worker is services/workers/transcribe/src/worker.py. "
    "Run integration tests under services/workers/transcribe/tests/ instead.",
    allow_module_level=True,
)
