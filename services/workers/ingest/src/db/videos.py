import json
import logging
from typing import Any

from .postgres import get_db_conn

logger = logging.getLogger("ingest-worker.db.videos")


def upsert_video_normalized_metadata(
    *,
    video_id: str,
    duration_seconds: float | None,
    container_format: str | None,
    source_platform: str,
    source_url: str | None,
    raw_json: dict[str, Any],
    video_bucket: str,
    video_key: str,
    audio_bucket: str,
    audio_key: str,
    video_size_bytes: int | None,
    audio_size_bytes: int | None,
) -> None:
    if not video_id:
        raise ValueError("video_id_required")

    sql = """
    INSERT INTO public.videos (
      id,
      source_platform,
      source_url,
      duration_seconds,
      container_format,
      raw_video_bucket,
      raw_video_object_key,
      audio_bucket,
      audio_object_key,
      raw_video_size_bytes,
      audio_size_bytes,
      metadata_json
    )
    VALUES (
      %(id)s,
      %(source_platform)s,
      %(source_url)s,
      %(duration_seconds)s,
      %(container_format)s,
      %(raw_video_bucket)s,
      %(raw_video_object_key)s,
      %(audio_bucket)s,
      %(audio_object_key)s,
      %(raw_video_size_bytes)s,
      %(audio_size_bytes)s,
      %(metadata_json)s::jsonb
    )
    ON CONFLICT (id) DO UPDATE SET
      source_platform = EXCLUDED.source_platform,
      source_url = EXCLUDED.source_url,
      duration_seconds = EXCLUDED.duration_seconds,
      container_format = EXCLUDED.container_format,
      raw_video_bucket = EXCLUDED.raw_video_bucket,
      raw_video_object_key = EXCLUDED.raw_video_object_key,
      audio_bucket = EXCLUDED.audio_bucket,
      audio_object_key = EXCLUDED.audio_object_key,
      raw_video_size_bytes = EXCLUDED.raw_video_size_bytes,
      audio_size_bytes = EXCLUDED.audio_size_bytes,
      metadata_json = EXCLUDED.metadata_json,
      updated_at = NOW();
    """

    params = {
        "id": video_id,
        "source_platform": source_platform,
        "source_url": source_url,
        "duration_seconds": duration_seconds,
        "container_format": container_format,
        "raw_video_bucket": video_bucket,
        "raw_video_object_key": video_key,
        "audio_bucket": audio_bucket,
        "audio_object_key": audio_key,
        "raw_video_size_bytes": video_size_bytes,
        "audio_size_bytes": audio_size_bytes,
        "metadata_json": json.dumps(raw_json, ensure_ascii=False),
    }

    logger.info("video_metadata_upsert_start", extra={"video_id": video_id})

    with get_db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
        conn.commit()

    logger.info("video_metadata_upsert_complete", extra={"video_id": video_id})


def persist_video_metadata(norm, *, source_url: str | None) -> None:
    upsert_video_normalized_metadata(
        video_id=norm.video_id,
        duration_seconds=norm.duration_seconds,
        container_format=norm.container_format,
        source_platform=norm.source_platform,
        source_url=source_url,
        raw_json=norm.raw,
        video_bucket=norm.video_ref.bucket,
        video_key=norm.video_ref.key,
        audio_bucket=norm.audio_ref.bucket,
        audio_key=norm.audio_ref.key,
        video_size_bytes=norm.video_ref.size_bytes,
        audio_size_bytes=norm.audio_ref.size_bytes,
    )
