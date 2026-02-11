import logging
import subprocess

logger = logging.getLogger("ingest-worker.media.audio")


def extract_audio_wav_16k_mono(video_path: str, audio_path: str) -> None:
    """
    Extract audio from video into WAV PCM 16-bit, 16kHz, mono.
    Raises RuntimeError on ffmpeg failure.
    """
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        video_path,
        "-vn",
        "-acodec",
        "pcm_s16le",
        "-ar",
        "16000",
        "-ac",
        "1",
        audio_path,
    ]

    logger.info(
        "ffmpeg_extract_start",
        extra={"video_path": video_path, "audio_path": audio_path},
    )
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except FileNotFoundError as e:
        raise RuntimeError(
            "ffmpeg_not_found: install ffmpeg and ensure it is on PATH"
        ) from e
    except subprocess.CalledProcessError as e:
        stderr = (e.stderr or "").strip()
        raise RuntimeError(f"ffmpeg_failed: {stderr[-400:]}") from e

    logger.info("ffmpeg_extract_complete", extra={"audio_path": audio_path})
