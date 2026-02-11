import io
import logging
from typing import Any

import yt_dlp

logger = logging.getLogger("ingest-worker.youtube")


def download_youtube_video(url: str) -> tuple[bytes, dict[str, Any]]:
    """
    Downloads a YouTube video into memory and returns:
    - raw video bytes
    - extracted metadata
    """

    buffer = io.BytesIO()
    metadata: dict[str, Any] = {}

    def _write_hook(data):
        buffer.write(data)

    ydl_opts = {
        "format": "mp4/bestvideo+bestaudio/best",
        "outtmpl": "-",  # stdout
        "quiet": True,
        "no_warnings": True,
        "progress_hooks": [],
    }

    logger.info("youtube_download_start", extra={"url": url})

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        metadata = {
            "title": info.get("title"),
            "duration": info.get("duration"),
            "uploader": info.get("uploader"),
            "webpage_url": info.get("webpage_url"),
        }

        ydl.process_info({**info, "requested_formats": None, "filepath": None})
        video_bytes = buffer.getvalue()

    logger.info("youtube_download_complete", extra={"url": url})
    return video_bytes, metadata
