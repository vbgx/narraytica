from __future__ import annotations

import os

import psycopg
import pytest
from packages.persistence.postgres.repos.segments_repo import SegmentsRepo
from packages.persistence.postgres.repos.speakers_repo import SpeakersRepo
from packages.persistence.postgres.repos.transcripts_repo import TranscriptsRepo
from packages.persistence.postgres.repos.videos_repo import VideosRepo


def _dsn() -> str:
    dsn = os.environ.get("POSTGRES_DSN")
    if not dsn:
        pytest.skip("POSTGRES_DSN not set (integration test skipped)")
    return dsn


def test_speaker_and_segment_link_roundtrip():

    with psycopg.connect(_dsn()) as conn:
        videos = VideosRepo(conn)
        transcripts = TranscriptsRepo(conn)
        segments = SegmentsRepo(conn)
        speakers = SpeakersRepo(conn)

        video = {
            "id": "video_test_2",
            "tenant_id": None,
            "org_id": None,
            "user_id": None,
            "source_type": "youtube",
            "source_uri": "https://example.test/v/2",
            "title": "Test2",
            "channel": None,
            "duration_ms": 1000,
            "language": "en",
            "published_at": None,
            "storage_bucket": None,
            "storage_key": None,
            "metadata": {},
        }
        v = videos.upsert_video(video)

        transcript = {
            "id": "tr_test_2",
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

        segs = [
            {
                "id": "seg_test_3",
                "transcript_id": t["id"],
                "segment_index": 0,
                "start_ms": 0,
                "end_ms": 400,
                "text": "a",
                "metadata": {},
            }
        ]
        segments.bulk_upsert_segments(segs)

        sp = {
            "id": "sp_test_1",
            "tenant_id": None,
            "display_name": "Speaker 1",
            "external_ref": None,
            "metadata": {},
        }
        s = speakers.upsert_speaker(sp)
        assert s["id"] == "sp_test_1"

        link = {
            "id": "ss_test_1",
            "segment_id": "seg_test_3",
            "speaker_id": s["id"],
            "confidence": 0.9,
            "metadata": {},
        }
        ss = speakers.link_segment_speaker(link)
        assert ss["segment_id"] == "seg_test_3"
        assert ss["speaker_id"] == s["id"]
