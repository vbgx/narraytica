from __future__ import annotations

import os

import psycopg
import pytest
from packages.persistence.postgres.repos.segments_repo import SegmentsRepo
from packages.persistence.postgres.repos.transcripts_repo import TranscriptsRepo
from packages.persistence.postgres.repos.videos_repo import VideosRepo


def _dsn() -> str:
    dsn = os.environ.get("POSTGRES_DSN")
    if not dsn:
        pytest.skip("POSTGRES_DSN not set (integration test skipped)")
    return dsn


def test_transcript_and_segments_roundtrip():

    with psycopg.connect(_dsn()) as conn:
        videos = VideosRepo(conn)
        transcripts = TranscriptsRepo(conn)
        segments = SegmentsRepo(conn)

        video = {
            "id": "video_test_1",
            "tenant_id": None,
            "org_id": None,
            "user_id": None,
            "source_type": "youtube",
            "source_uri": "https://example.test/v/1",
            "title": "Test",
            "channel": None,
            "duration_ms": 1000,
            "language": "en",
            "published_at": None,
            "storage_bucket": None,
            "storage_key": None,
            "metadata": {},
        }
        v = videos.upsert_video(video)
        assert v["id"] == "video_test_1"

        transcript = {
            "id": "tr_test_1",
            "tenant_id": None,
            "video_id": v["id"],
            "provider": "whisper",
            "language": "en",
            "status": "completed",
            "artifact_bucket": None,
            "artifact_key": None,
            "artifact_format": None,
            "artifact_bytes": None,
            "artifact_sha256": None,
            "version": 1,
            "is_latest": True,
            "metadata": {},
        }
        t = transcripts.create_transcript(transcript)
        assert t["id"] == "tr_test_1"
        assert t["video_id"] == v["id"]

        segs = [
            {
                "id": "seg_test_1",
                "transcript_id": t["id"],
                "segment_index": 0,
                "start_ms": 0,
                "end_ms": 500,
                "text": "hello",
                "metadata": {},
            },
            {
                "id": "seg_test_2",
                "transcript_id": t["id"],
                "segment_index": 1,
                "start_ms": 500,
                "end_ms": 900,
                "text": "world",
                "metadata": {},
            },
        ]
        n = segments.bulk_upsert_segments(segs, batch_size=100)
        assert n == 2

        back = segments.list_segments_by_transcript(t["id"])
        assert [s["segment_index"] for s in back] == [0, 1]
        assert back[0]["text"] == "hello"
