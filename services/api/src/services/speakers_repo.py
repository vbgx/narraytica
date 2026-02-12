from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Protocol

from ..services.db import get_db


@dataclass(frozen=True)
class SpeakerV1:
    speaker_id: str
    video_id: str
    label: str | None = None
    name: str | None = None
    language: str | None = None
    metadata: dict | None = None
    created_at: datetime | None = None

    def to_dict(self) -> dict:
        d = asdict(self)
        if self.created_at is not None:
            d["created_at"] = self.created_at.isoformat()
        return d


class SpeakersRepo(Protocol):
    def list_speakers(
        self,
        *,
        video_id: str | None,
        limit: int,
        offset: int,
    ) -> tuple[list[SpeakerV1], int]: ...

    def get_speaker(self, speaker_id: str) -> SpeakerV1 | None: ...


class PostgresSpeakersRepo:
    def __init__(self, database_url: str):
        self.database_url = database_url

    def list_speakers(
        self,
        *,
        video_id: str | None,
        limit: int,
        offset: int,
    ) -> tuple[list[SpeakerV1], int]:
        where = []
        params: dict[str, object] = {"limit": limit, "offset": offset}

        if video_id:
            where.append("sp.video_id = %(video_id)s")
            params["video_id"] = video_id

        where_sql = ""
        if where:
            where_sql = "WHERE " + " AND ".join(where)

        count_sql = f"SELECT COUNT(*) FROM speakers sp {where_sql}"
        rows_sql = f"""
            SELECT sp.id, sp.video_id, sp.label, sp.name,
                   sp.language, sp.metadata, sp.created_at
            FROM speakers sp
            {where_sql}
            ORDER BY sp.created_at DESC, sp.id ASC
            LIMIT %(limit)s OFFSET %(offset)s
        """

        with get_db(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute(count_sql, params)
                total = int(cur.fetchone()[0])

                cur.execute(rows_sql, params)
                out: list[SpeakerV1] = []
                for (
                    speaker_id,
                    v_id,
                    label,
                    name,
                    language,
                    metadata,
                    created_at,
                ) in cur.fetchall():
                    out.append(
                        SpeakerV1(
                            speaker_id=str(speaker_id),
                            video_id=str(v_id),
                            label=str(label) if label is not None else None,
                            name=str(name) if name is not None else None,
                            language=str(language) if language is not None else None,
                            metadata=metadata if metadata is not None else None,
                            created_at=created_at,
                        )
                    )
                return out, total

    def get_speaker(self, speaker_id: str) -> SpeakerV1 | None:
        sql = """
            SELECT sp.id, sp.video_id, sp.label, sp.name,
                   sp.language, sp.metadata, sp.created_at
            FROM speakers sp
            WHERE sp.id = %(id)s
            LIMIT 1
        """
        with get_db(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, {"id": speaker_id})
                row = cur.fetchone()
                if not row:
                    return None
                (
                    sid,
                    v_id,
                    label,
                    name,
                    language,
                    metadata,
                    created_at,
                ) = row
                return SpeakerV1(
                    speaker_id=str(sid),
                    video_id=str(v_id),
                    label=str(label) if label is not None else None,
                    name=str(name) if name is not None else None,
                    language=str(language) if language is not None else None,
                    metadata=metadata if metadata is not None else None,
                    created_at=created_at,
                )


def get_speakers_repo() -> SpeakersRepo:
    from ..config import settings

    if not settings.database_url:
        raise RuntimeError("DATABASE_URL not configured")
    return PostgresSpeakersRepo(settings.database_url)
