from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class StorageRef:
    bucket: str
    key: str
    size_bytes: int | None
    content_type: str | None
    etag: str | None


@dataclass(frozen=True)
class NormalizedVideoMetadata:
    video_id: str
    source_platform: str  # youtube | upload | future
    duration_seconds: float | None
    container_format: str | None
    video_ref: StorageRef
    audio_ref: StorageRef
    raw: dict[str, Any]


def _safe_float(v: Any) -> float | None:
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _safe_str(v: Any) -> str | None:
    if v is None:
        return None
    s = str(v).strip()
    return s or None


def _get_duration_seconds(ffprobe_json: dict[str, Any]) -> float | None:
    fmt = ffprobe_json.get("format") or {}
    return _safe_float(fmt.get("duration"))


def _get_container_format(ffprobe_json: dict[str, Any]) -> str | None:
    fmt = ffprobe_json.get("format") or {}
    return _safe_str(fmt.get("format_name"))


def _to_storage_ref(stat: dict[str, Any]) -> StorageRef:
    # Required keys: bucket, key
    bucket = _safe_str(stat.get("bucket"))
    key = _safe_str(stat.get("key"))
    if not bucket or not key:
        raise ValueError("storage_stat_missing_required_fields: bucket/key")

    size_bytes = stat.get("size_bytes")
    if isinstance(size_bytes, str):
        try:
            size_bytes = int(size_bytes)
        except ValueError:
            size_bytes = None
    elif size_bytes is not None and not isinstance(size_bytes, int):
        size_bytes = None

    return StorageRef(
        bucket=bucket,
        key=key,
        size_bytes=size_bytes,
        content_type=_safe_str(stat.get("content_type")),
        etag=_safe_str(stat.get("etag")),
    )


def normalize_video_metadata(
    *,
    video_id: str,
    source_platform: str,
    ffprobe_video: dict[str, Any],
    video_stat: dict[str, Any],
    audio_stat: dict[str, Any],
    extracted_metadata: dict[str, Any] | None = None,
) -> NormalizedVideoMetadata:
    extracted_metadata = extracted_metadata or {}

    return NormalizedVideoMetadata(
        video_id=_safe_str(video_id) or "",
        source_platform=_safe_str(source_platform) or "unknown",
        duration_seconds=_get_duration_seconds(ffprobe_video),
        container_format=_get_container_format(ffprobe_video),
        video_ref=_to_storage_ref(video_stat),
        audio_ref=_to_storage_ref(audio_stat),
        raw={
            "ffprobe": ffprobe_video,
            "extracted": extracted_metadata,
        },
    )
