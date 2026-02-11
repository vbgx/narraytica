import json
import logging
import subprocess
from typing import Any

logger = logging.getLogger("ingest-worker.metadata.ffprobe")


def probe_media(path: str) -> dict[str, Any]:
    """
    Run ffprobe on a media file and return parsed JSON metadata.

    Raises:
        RuntimeError: if ffprobe is missing, fails, or returns invalid JSON.
    """
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        path,
    ]

    logger.info("ffprobe_start", extra={"path": path})

    try:
        res = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as e:
        logger.error("ffprobe_not_found", extra={"path": path})
        raise RuntimeError(
            "ffprobe_not_found: ensure ffmpeg is installed and on PATH"
        ) from e
    except subprocess.CalledProcessError as e:
        stderr = (e.stderr or "").strip()
        logger.error(
            "ffprobe_failed",
            extra={"path": path, "stderr_tail": stderr[-400:]},
        )
        raise RuntimeError(f"ffprobe_failed: {stderr[-400:]}") from e

    stdout = (res.stdout or "").strip()

    try:
        data = json.loads(stdout)
    except json.JSONDecodeError as e:
        logger.error(
            "ffprobe_invalid_json",
            extra={"path": path, "stdout_tail": stdout[-400:]},
        )
        raise RuntimeError("ffprobe_output_invalid_json") from e

    logger.info("ffprobe_complete", extra={"path": path})
    return data
