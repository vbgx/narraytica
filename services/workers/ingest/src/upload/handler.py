import logging
from typing import Any

logger = logging.getLogger("ingest-worker.upload")


def migrate_upload_to_canonical(
    storage,
    *,
    upload_bucket: str,
    upload_key: str,
    canonical_bucket: str,
    canonical_key: str,
) -> dict[str, Any]:
    """
    Move/copy an uploaded object from a staging uploads location to
    the canonical raw video location.

    For now: server-side COPY (safe). Cleanup (delete) can be added later.
    """
    logger.info(
        "upload_migration_start",
        extra={
            "upload_bucket": upload_bucket,
            "upload_key": upload_key,
            "canonical_bucket": canonical_bucket,
            "canonical_key": canonical_key,
        },
    )

    storage.copy_object(upload_bucket, upload_key, canonical_bucket, canonical_key)

    logger.info(
        "upload_migration_complete",
        extra={
            "canonical_bucket": canonical_bucket,
            "canonical_key": canonical_key,
        },
    )

    return {
        "upload_bucket": upload_bucket,
        "upload_key": upload_key,
        "canonical_bucket": canonical_bucket,
        "canonical_key": canonical_key,
    }
