from __future__ import annotations

import json
import logging
import subprocess
from pathlib import Path
from typing import Any

logger = logging.getLogger("ingest-worker.metadata.ffprobe")


def probe_media(path: str) -> dict[str, Any]:
    """
    Best-effort ffprobe wrapper.

    IMPORTANT:
    - ffprobe failure must NOT fail ingestion.
    - Return {} on error; downstream normalization should handle missing keys.
    """
    p = str(Path(path))

    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        p,
    ]

    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
        data = json.loads(out)
        if isinstance(data, dict):
            return data
        return {}
    except Exception:
        # Keep the existing log key used by your tests/log parsing.
        logger.exception("ffprobe_failed")
        return {}
