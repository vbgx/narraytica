from __future__ import annotations

from typing import Any

import psycopg
from packages.persistence.postgres.errors import (
    Conflict,
    NotFound,
    RetryableDbError,
)
from packages.persistence.postgres.mappers.videos import video_row_to_contract
from packages.persistence.postgres.tx import transaction
from psycopg.rows import dict_row

JsonObj = dict[str, Any]


class VideosRepo:
    def __init__(self, conn: psycopg.Connection):
        self._conn = conn

    def upsert_video(self, video: JsonObj) -> JsonObj:
        """
        Idempotency key: (source_type, source_uri) per videos_source_unique.
        """
        try:
            with transaction(self._conn):
                cur = self._conn.cursor(row_factory=dict_row)
                cur.execute(
                    """
                    INSERT INTO videos (
                        id, tenant_id, org_id, user_id,
                        source_type, source_uri,
                        title, channel, duration_ms,
                        language, published_at,
                        storage_bucket, storage_key,
                        metadata
                    )
                    VALUES (
                        %(id)s, %(tenant_id)s, %(org_id)s, %(user_id)s,
                        %(source_type)s, %(source_uri)s,
                        %(title)s, %(channel)s, %(duration_ms)s,
                        %(language)s, %(published_at)s,
                        %(storage_bucket)s, %(storage_key)s,
                        %(metadata)s
                    )
                    ON CONFLICT (source_type, source_uri)
                    DO UPDATE SET
                        tenant_id = COALESCE(
                            EXCLUDED.tenant_id, videos.tenant_id
                        ),
                        org_id = COALESCE(
                            EXCLUDED.org_id, videos.org_id
                        ),
                        user_id = COALESCE(
                            EXCLUDED.user_id, videos.user_id
                        ),
                        title = COALESCE(
                            EXCLUDED.title, videos.title
                        ),
                        channel = COALESCE(
                            EXCLUDED.channel, videos.channel
                        ),
                        duration_ms = COALESCE(
                            EXCLUDED.duration_ms, videos.duration_ms
                        ),
                        language = COALESCE(
                            EXCLUDED.language, videos.language
                        ),
                        published_at = COALESCE(
                            EXCLUDED.published_at, videos.published_at
                        ),
                        storage_bucket = COALESCE(
                            EXCLUDED.storage_bucket, videos.storage_bucket
                        ),
                        storage_key = COALESCE(
                            EXCLUDED.storage_key, videos.storage_key
                        ),
                        metadata = videos.metadata || EXCLUDED.metadata
                    RETURNING
                        id, tenant_id, org_id, user_id,
                        source_type, source_uri,
                        title, channel, duration_ms,
                        language, published_at,
                        storage_bucket, storage_key,
                        metadata,
                        created_at, updated_at
                    """,
                    video,
                )
                row = cur.fetchone()
                assert row is not None
                return video_row_to_contract(row)
        except psycopg.errors.CheckViolation as e:
            raise Conflict(str(e)) from e
        except psycopg.Error as e:
            raise RetryableDbError(str(e)) from e

    def get_video(self, video_id: str) -> JsonObj:
        cur = self._conn.cursor(row_factory=dict_row)
        cur.execute(
            """
            SELECT
                id, tenant_id, org_id, user_id,
                source_type, source_uri,
                title, channel, duration_ms,
                language, published_at,
                storage_bucket, storage_key,
                metadata,
                created_at, updated_at
            FROM videos
            WHERE id = %s
            """,
            (video_id,),
        )
        row = cur.fetchone()
        if not row:
            raise NotFound(f"video not found: {video_id}")
        return video_row_to_contract(row)
