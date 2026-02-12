from __future__ import annotations

import json
import uuid
from typing import Any

from .postgres import get_db_conn


def _uuid() -> str:
    return str(uuid.uuid4())


def create_mock_transcript(
    *, video_id: str, metadata: dict[str, Any] | None = None
) -> str:
    """
    Skeleton implementation:
      - creates a transcripts row as if transcription completed.
      - real worker will download audio + call ASR provider later.
    """
    transcript_id = _uuid()
    meta = metadata or {}

    sql = """
    INSERT INTO public.transcripts (
      id, video_id, provider, status, language, metadata, created_at, updated_at
    )
    VALUES (
      %(id)s, %(video_id)s, %(provider)s, %(status)s, %(language)s, %(metadata)s::jsonb,
      now(), now()
    );
    """

    params = {
        "id": transcript_id,
        "video_id": video_id,
        "provider": "mock",
        "status": "completed",
        "language": None,
        "metadata": json.dumps(meta, ensure_ascii=False),
    }

    with get_db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
        conn.commit()

    return transcript_id
