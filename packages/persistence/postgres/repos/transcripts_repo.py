from __future__ import annotations

from typing import Any

import psycopg
from packages.persistence.postgres.errors import (
    Conflict,
    NotFound,
    RetryableDbError,
)
from packages.persistence.postgres.mappers.transcripts import transcript_row_to_contract
from packages.persistence.postgres.tx import transaction
from psycopg.rows import dict_row

JsonObj = dict[str, Any]


class TranscriptsRepo:
    def __init__(self, conn: psycopg.Connection):
        self._conn = conn

    def create_transcript(self, transcript: JsonObj) -> JsonObj:
        try:
            with transaction(self._conn):
                cur = self._conn.cursor(row_factory=dict_row)
                cur.execute(
                    """
                    INSERT INTO transcripts (
                        id, tenant_id, video_id,
                        provider, language, status,
                        artifact_bucket, artifact_key, artifact_format,
                        artifact_bytes, artifact_sha256,
                        version, is_latest, metadata
                    )
                    VALUES (
                        %(id)s, %(tenant_id)s, %(video_id)s,
                        %(provider)s, %(language)s, %(status)s,
                        %(artifact_bucket)s, %(artifact_key)s, %(artifact_format)s,
                        %(artifact_bytes)s, %(artifact_sha256)s,
                        %(version)s, %(is_latest)s, %(metadata)s
                    )
                    RETURNING
                        id, tenant_id, video_id,
                        provider, language, status,
                        artifact_bucket, artifact_key, artifact_format,
                        artifact_bytes, artifact_sha256,
                        version, is_latest,
                        metadata,
                        created_at, updated_at
                    """,
                    transcript,
                )
                row = cur.fetchone()
                assert row is not None
                return transcript_row_to_contract(row)
        except psycopg.errors.ForeignKeyViolation as e:
            raise NotFound(str(e)) from e
        except psycopg.errors.UniqueViolation as e:
            raise Conflict(str(e)) from e
        except psycopg.Error as e:
            raise RetryableDbError(str(e)) from e

    def upsert_transcript(self, transcript: JsonObj) -> JsonObj:
        try:
            with transaction(self._conn):
                cur = self._conn.cursor(row_factory=dict_row)
                cur.execute(
                    """
                    INSERT INTO transcripts (
                        id, tenant_id, video_id,
                        provider, language, status,
                        artifact_bucket, artifact_key, artifact_format,
                        artifact_bytes, artifact_sha256,
                        version, is_latest, metadata
                    )
                    VALUES (
                        %(id)s, %(tenant_id)s, %(video_id)s,
                        %(provider)s, %(language)s, %(status)s,
                        %(artifact_bucket)s, %(artifact_key)s, %(artifact_format)s,
                        %(artifact_bytes)s, %(artifact_sha256)s,
                        %(version)s, %(is_latest)s, %(metadata)s
                    )
                    ON CONFLICT (id)
                    DO UPDATE SET
                        tenant_id = COALESCE(
                            EXCLUDED.tenant_id, transcripts.tenant_id
                        ),
                        video_id = EXCLUDED.video_id,
                        provider = COALESCE(
                            EXCLUDED.provider, transcripts.provider
                        ),
                        language = COALESCE(
                            EXCLUDED.language, transcripts.language
                        ),
                        status = EXCLUDED.status,
                        artifact_bucket = COALESCE(
                            EXCLUDED.artifact_bucket, transcripts.artifact_bucket
                        ),
                        artifact_key = COALESCE(
                            EXCLUDED.artifact_key, transcripts.artifact_key
                        ),
                        artifact_format = COALESCE(
                            EXCLUDED.artifact_format, transcripts.artifact_format
                        ),
                        artifact_bytes = COALESCE(
                            EXCLUDED.artifact_bytes, transcripts.artifact_bytes
                        ),
                        artifact_sha256 = COALESCE(
                            EXCLUDED.artifact_sha256, transcripts.artifact_sha256
                        ),
                        version = EXCLUDED.version,
                        is_latest = EXCLUDED.is_latest,
                        metadata = transcripts.metadata || EXCLUDED.metadata
                    RETURNING
                        id, tenant_id, video_id,
                        provider, language, status,
                        artifact_bucket, artifact_key, artifact_format,
                        artifact_bytes, artifact_sha256,
                        version, is_latest,
                        metadata,
                        created_at, updated_at
                    """,
                    transcript,
                )
                row = cur.fetchone()
                assert row is not None
                return transcript_row_to_contract(row)
        except psycopg.errors.ForeignKeyViolation as e:
            raise NotFound(str(e)) from e
        except psycopg.errors.UniqueViolation as e:
            raise Conflict(str(e)) from e
        except psycopg.Error as e:
            raise RetryableDbError(str(e)) from e

    def get_transcript(self, transcript_id: str) -> JsonObj:
        cur = self._conn.cursor(row_factory=dict_row)
        cur.execute(
            """
            SELECT
                id, tenant_id, video_id,
                provider, language, status,
                artifact_bucket, artifact_key, artifact_format,
                artifact_bytes, artifact_sha256,
                version, is_latest,
                metadata,
                created_at, updated_at
            FROM transcripts
            WHERE id = %s
            """,
            (transcript_id,),
        )
        row = cur.fetchone()
        if not row:
            raise NotFound(f"transcript not found: {transcript_id}")
        return transcript_row_to_contract(row)
