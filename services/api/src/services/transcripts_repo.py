from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import psycopg


def _database_url() -> str:
    url = os.getenv("API_DATABASE_URL") or os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("API_DATABASE_URL not configured")
    if url.startswith("postgresql+psycopg://"):
        url = "postgresql://" + url[len("postgresql+psycopg://") :]
    return url


@dataclass(frozen=True)
class TranscriptRecord:
    transcript_id: str
    video_id: str
    provider: str
    language: str | None
    text: str
    segments: list[dict[str, Any]]
    audio_ref: dict[str, Any]
    storage_ref: dict[str, Any]
    asr: dict[str, Any] | None
    created_at: datetime


class TranscriptsRepo:
    def __init__(self, database_url: str | None = None) -> None:
        self.database_url = database_url or _database_url()

    def _connect(self) -> psycopg.Connection:
        return psycopg.connect(self.database_url)

    def get_by_id(self, transcript_id: str) -> TranscriptRecord | None:
        q = """
        SELECT
          id,
          video_id,
          provider,
          language,
          text,
          segments,
          audio_ref,
          storage_ref,
          asr,
          created_at
        FROM transcripts
        WHERE id = %s
        """
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(q, (transcript_id,))
            row = cur.fetchone()
            if not row:
                return None
            return TranscriptRecord(
                transcript_id=str(row[0]),
                video_id=str(row[1]),
                provider=str(row[2]),
                language=row[3],
                text=str(row[4]),
                segments=list(row[5] or []),
                audio_ref=dict(row[6] or {}),
                storage_ref=dict(row[7] or {}),
                asr=row[8],
                created_at=row[9],
            )

    def latest_for_video(
        self,
        *,
        video_id: str,
        artifact_bucket: str | None = None,
        artifact_key: str | None = None,
    ) -> TranscriptRecord | None:
        if artifact_bucket and artifact_key:
            q = """
            SELECT
              id,
              video_id,
              provider,
              language,
              text,
              segments,
              audio_ref,
              storage_ref,
              asr,
              created_at
            FROM transcripts
            WHERE video_id = %s
              AND (storage_ref->>'bucket') = %s
              AND (storage_ref->>'key') = %s
            ORDER BY created_at DESC
            LIMIT 1
            """
            params = (video_id, artifact_bucket, artifact_key)
        else:
            q = """
            SELECT
              id,
              video_id,
              provider,
              language,
              text,
              segments,
              audio_ref,
              storage_ref,
              asr,
              created_at
            FROM transcripts
            WHERE video_id = %s
            ORDER BY created_at DESC
            LIMIT 1
            """
            params = (video_id,)

        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(q, params)
            row = cur.fetchone()
            if not row:
                return None
            return TranscriptRecord(
                transcript_id=str(row[0]),
                video_id=str(row[1]),
                provider=str(row[2]),
                language=row[3],
                text=str(row[4]),
                segments=list(row[5] or []),
                audio_ref=dict(row[6] or {}),
                storage_ref=dict(row[7] or {}),
                asr=row[8],
                created_at=row[9],
            )
