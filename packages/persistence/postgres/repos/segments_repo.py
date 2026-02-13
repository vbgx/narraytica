from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import psycopg
from packages.persistence.postgres.errors import (
    Conflict,
    NotFound,
    RetryableDbError,
)
from packages.persistence.postgres.mappers.segments import segment_row_to_contract
from packages.persistence.postgres.tx import transaction
from psycopg.rows import dict_row

JsonObj = dict[str, Any]


class SegmentsRepo:
    def __init__(self, conn: psycopg.Connection):
        self._conn = conn

    def bulk_upsert_segments(
        self,
        segments: Sequence[JsonObj],
        *,
        batch_size: int = 500,
    ) -> int:
        """
        Upsert segments per unique key (transcript_id, segment_index)
        per segments_transcript_order_unique.

        Returns number of rows inserted/updated (best-effort).
        """
        if not segments:
            return 0

        if batch_size <= 0:
            raise ValueError("batch_size must be > 0")

        total = 0
        try:
            with transaction(self._conn):
                cur = self._conn.cursor()
                for i in range(0, len(segments), batch_size):
                    batch = segments[i : i + batch_size]
                    cur.executemany(
                        """
                        INSERT INTO segments (
                            id, transcript_id, segment_index,
                            start_ms, end_ms, text,
                            metadata
                        )
                        VALUES (
                            %(id)s, %(transcript_id)s, %(segment_index)s,
                            %(start_ms)s, %(end_ms)s, %(text)s,
                            %(metadata)s
                        )
                        ON CONFLICT (transcript_id, segment_index)
                        DO UPDATE SET
                            id = EXCLUDED.id,
                            start_ms = EXCLUDED.start_ms,
                            end_ms = EXCLUDED.end_ms,
                            text = EXCLUDED.text,
                            metadata = segments.metadata || EXCLUDED.metadata
                        """,
                        batch,
                    )
                    total += len(batch)
            return total
        except psycopg.errors.ForeignKeyViolation as e:
            raise NotFound(str(e)) from e
        except psycopg.errors.UniqueViolation as e:
            raise Conflict(str(e)) from e
        except psycopg.Error as e:
            raise RetryableDbError(str(e)) from e

    def list_segments_by_transcript(self, transcript_id: str) -> list[JsonObj]:
        cur = self._conn.cursor(row_factory=dict_row)
        cur.execute(
            """
            SELECT
                id, transcript_id, segment_index,
                start_ms, end_ms, text,
                metadata,
                created_at, updated_at
            FROM segments
            WHERE transcript_id = %s
            ORDER BY segment_index ASC
            """,
            (transcript_id,),
        )
        return [segment_row_to_contract(r) for r in cur.fetchall()]
