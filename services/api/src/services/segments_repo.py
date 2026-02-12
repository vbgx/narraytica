from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from ..services.db import get_db  # adjust if your DB helper path differs


@dataclass(frozen=True)
class SegmentWord:
    start_ms: int
    end_ms: int
    text: str
    confidence: float | None = None


@dataclass(frozen=True)
class SegmentV1:
    start_ms: int
    end_ms: int
    text: str
    words: list[SegmentWord] | None = None


class SegmentsRepo(Protocol):
    def list_segments(
        self,
        *,
        video_id: str | None,
        speaker_id: str | None,
        start_ms_gte: int | None,
        end_ms_lte: int | None,
        limit: int,
        offset: int,
    ) -> tuple[list[SegmentV1], int]: ...

    def get_segment(self, segment_id: str) -> SegmentV1 | None: ...


class PostgresSegmentsRepo:
    def __init__(self, database_url: str):
        self.database_url = database_url

    def list_segments(
        self,
        *,
        video_id: str | None,
        speaker_id: str | None,
        start_ms_gte: int | None,
        end_ms_lte: int | None,
        limit: int,
        offset: int,
    ) -> tuple[list[SegmentV1], int]:
        where = []
        params: dict[str, object] = {"limit": limit, "offset": offset}

        if video_id:
            where.append("s.video_id = %(video_id)s")
            params["video_id"] = video_id
        if speaker_id:
            where.append("s.speaker_id = %(speaker_id)s")
            params["speaker_id"] = speaker_id
        if start_ms_gte is not None:
            where.append("s.start_ms >= %(start_ms_gte)s")
            params["start_ms_gte"] = start_ms_gte
        if end_ms_lte is not None:
            where.append("s.end_ms <= %(end_ms_lte)s")
            params["end_ms_lte"] = end_ms_lte

        where_sql = ""
        if where:
            where_sql = "WHERE " + " AND ".join(where)

        count_sql = f"SELECT COUNT(*) FROM segments s {where_sql}"
        rows_sql = f"""
            SELECT s.start_ms, s.end_ms, s.text
            FROM segments s
            {where_sql}
            ORDER BY s.start_ms ASC, s.end_ms ASC, s.id ASC
            LIMIT %(limit)s OFFSET %(offset)s
        """

        with get_db(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute(count_sql, params)
                total = int(cur.fetchone()[0])

                cur.execute(rows_sql, params)
                out: list[SegmentV1] = []
                for start_ms, end_ms, text in cur.fetchall():
                    out.append(
                        SegmentV1(
                            start_ms=int(start_ms), end_ms=int(end_ms), text=str(text)
                        )
                    )
                return out, total

    def get_segment(self, segment_id: str) -> SegmentV1 | None:
        sql = """
            SELECT start_ms, end_ms, text
            FROM segments
            WHERE id = %(id)s
            LIMIT 1
        """
        with get_db(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, {"id": segment_id})
                row = cur.fetchone()
                if not row:
                    return None
                start_ms, end_ms, text = row
                return SegmentV1(
                    start_ms=int(start_ms), end_ms=int(end_ms), text=str(text)
                )


def get_segments_repo() -> SegmentsRepo:
    from ..config import settings

    if not settings.database_url:
        raise RuntimeError("DATABASE_URL not configured")
    return PostgresSegmentsRepo(settings.database_url)
