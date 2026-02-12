from __future__ import annotations

from pathlib import Path


def _repo_root() -> Path:
    # .../services/workers/transcribe/tests/integration/test_*.py
    return Path(__file__).resolve().parents[5]


def _add_transcribe_src_to_syspath() -> Path:
    root = _repo_root()
    src = root / "services" / "workers" / "transcribe" / "src"
    import sys

    # Put transcribe/src first so `import db.jobs` resolves to transcribe, not ingest
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))
    return src
