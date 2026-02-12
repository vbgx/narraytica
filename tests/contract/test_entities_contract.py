from __future__ import annotations

from pathlib import Path

from ._helpers import load_json, load_schema, validate_payload


def test_video_matches_contract():
    payload = load_json(Path("tests/fixtures/contracts/video.min.json"))
    schema = load_schema("video.schema.json")
    validate_payload(schema=schema, payload=payload)


def test_segment_matches_contract():
    payload = load_json(Path("tests/fixtures/contracts/segment.min.json"))
    schema = load_schema("segment.schema.json")
    validate_payload(schema=schema, payload=payload)


def test_transcript_matches_contract():
    payload = load_json(Path("tests/fixtures/contracts/transcript.min.json"))
    schema = load_schema("transcript.schema.json")
    validate_payload(schema=schema, payload=payload)


def test_speaker_matches_contract():
    payload = load_json(Path("tests/fixtures/contracts/speaker.min.json"))
    schema = load_schema("speaker.schema.json")
    validate_payload(schema=schema, payload=payload)
