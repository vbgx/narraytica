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

    def upsert_transcript_by_artifact(
        self,
        *,
        transcript: JsonObj,
    ) -> None:
        """
        Worker-compatible UPSERT:
        - matches partial unique index transcripts_unique_artifact
          ON (video_id, artifact_key, version) WHERE artifact_key IS NOT NULL
        - writes duration_seconds + storage_ref (added in 0011 + 0010)
        - keeps legacy artifact_* columns for now (backward compat)
        """
        try:
            with transaction(self._conn):
                cur = self._conn.cursor()
                cur.execute(
                    """
                    INSERT INTO transcripts (
                        id,
                        tenant_id,
                        video_id,
                        provider,
                        language,
                        duration_seconds,
                        status,
                        artifact_bucket,
                        artifact_key,
                        artifact_format,
                        artifact_bytes,
                        artifact_sha256,
                        version,
                        is_latest,
                        metadata,
                        storage_ref,
                        created_at,
                        updated_at
                    )
                    VALUES (
                        %(id)s,
                        %(tenant_id)s,
                        %(video_id)s,
                        %(provider)s,
                        %(language)s,
                        %(duration_seconds)s,
                        %(status)s,
                        %(artifact_bucket)s,
                        %(artifact_key)s,
                        %(artifact_format)s,
                        %(artifact_bytes)s,
                        %(artifact_sha256)s,
                        %(version)s,
                        %(is_latest)s,
                        %(metadata)s::jsonb,
                        %(storage_ref)s::jsonb,
                        now(),
                        now()
                    )
                    ON CONFLICT (video_id, artifact_key, version)
                    WHERE artifact_key IS NOT NULL
                    DO UPDATE SET
                        tenant_id = EXCLUDED.tenant_id,
                        provider = EXCLUDED.provider,
                        language = EXCLUDED.language,
                        duration_seconds = EXCLUDED.duration_seconds,
                        status = EXCLUDED.status,
                        artifact_bucket = EXCLUDED.artifact_bucket,
                        artifact_key = EXCLUDED.artifact_key,
                        artifact_format = EXCLUDED.artifact_format,
                        artifact_bytes = EXCLUDED.artifact_bytes,
                        artifact_sha256 = EXCLUDED.artifact_sha256,
                        is_latest = EXCLUDED.is_latest,
                        metadata = EXCLUDED.metadata,
                        storage_ref = EXCLUDED.storage_ref,
                        updated_at = now()
                    """,
                    transcript,
                )
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
                storage_ref,
                duration_seconds,
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
