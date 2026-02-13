from __future__ import annotations

from typing import Any

import psycopg
from packages.persistence.postgres.errors import (
    Conflict,
    NotFound,
    RetryableDbError,
)
from packages.persistence.postgres.mappers.speakers import (
    segment_speaker_row_to_contract,
    speaker_row_to_contract,
)
from packages.persistence.postgres.tx import transaction
from psycopg.rows import dict_row

JsonObj = dict[str, Any]


class SpeakersRepo:
    def __init__(self, conn: psycopg.Connection):
        self._conn = conn

    def upsert_speaker(self, speaker: JsonObj) -> JsonObj:
        try:
            with transaction(self._conn):
                cur = self._conn.cursor(row_factory=dict_row)
                cur.execute(
                    """
                    INSERT INTO speakers (
                        id, tenant_id, display_name,
                        external_ref, metadata
                    )
                    VALUES (
                        %(id)s, %(tenant_id)s, %(display_name)s,
                        %(external_ref)s, %(metadata)s
                    )
                    ON CONFLICT (id)
                    DO UPDATE SET
                        tenant_id = COALESCE(
                            EXCLUDED.tenant_id, speakers.tenant_id
                        ),
                        display_name = COALESCE(
                            EXCLUDED.display_name, speakers.display_name
                        ),
                        external_ref = COALESCE(
                            EXCLUDED.external_ref, speakers.external_ref
                        ),
                        metadata = speakers.metadata || EXCLUDED.metadata
                    RETURNING
                        id, tenant_id, display_name,
                        external_ref, metadata,
                        created_at, updated_at
                    """,
                    speaker,
                )
                row = cur.fetchone()
                assert row is not None
                return speaker_row_to_contract(row)
        except psycopg.errors.UniqueViolation as e:
            raise Conflict(str(e)) from e
        except psycopg.Error as e:
            raise RetryableDbError(str(e)) from e

    def link_segment_speaker(self, link: JsonObj) -> JsonObj:
        try:
            with transaction(self._conn):
                cur = self._conn.cursor(row_factory=dict_row)
                cur.execute(
                    """
                    INSERT INTO segment_speakers (
                        id, segment_id, speaker_id,
                        confidence, metadata
                    )
                    VALUES (
                        %(id)s, %(segment_id)s, %(speaker_id)s,
                        %(confidence)s, %(metadata)s
                    )
                    ON CONFLICT (id)
                    DO UPDATE SET
                        segment_id = EXCLUDED.segment_id,
                        speaker_id = EXCLUDED.speaker_id,
                        confidence = EXCLUDED.confidence,
                        metadata = segment_speakers.metadata || EXCLUDED.metadata
                    RETURNING
                        id, segment_id, speaker_id,
                        confidence, metadata, created_at
                    """,
                    link,
                )
                row = cur.fetchone()
                assert row is not None
                return segment_speaker_row_to_contract(row)
        except psycopg.errors.ForeignKeyViolation as e:
            raise NotFound(str(e)) from e
        except psycopg.errors.UniqueViolation as e:
            raise Conflict(str(e)) from e
        except psycopg.Error as e:
            raise RetryableDbError(str(e)) from e
