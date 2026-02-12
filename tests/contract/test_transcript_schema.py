from __future__ import annotations

import json
from pathlib import Path

import jsonschema


def _load_schema(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_transcript_payload_conforms_to_schema() -> None:
    base = Path("packages/contracts/schemas").resolve()

    transcript_schema = _load_schema(base / "transcript.schema.json")
    segment_schema = _load_schema(base / "segment.schema.json")
    storage_ref_schema = _load_schema(base / "storage_ref.schema.json")

    # Minimal payload that matches current worker output.
    payload = {
        "video_id": "vid_123",
        "provider": "faster-whisper",
        "language": "fr",
        "text": "bonjour",
        "segments": [
            {"start_ms": 0, "end_ms": 500, "text": "bonjour"},
            {"start_ms": 500, "end_ms": 900, "text": "à tous"},
        ],
        "asr": {"opaque": True},
        "audio_ref": {"bucket": "uploads", "key": "audio/vid_123.wav"},
    }

    # Resolve local relative refs like "segment.schema.json"
    base_uri = base.as_uri() + "/"

    resolver = jsonschema.RefResolver(base_uri=base_uri, referrer=transcript_schema)

    # Also pin the schemas by their declared $id to avoid any remote fetch
    for sch in (transcript_schema, segment_schema, storage_ref_schema):
        sid = sch.get("$id")
        if isinstance(sid, str) and sid:
            resolver.store[sid] = sch

    # And pin explicit file URIs as well (extra-safe)
    resolver.store[base_uri + "transcript.schema.json"] = transcript_schema
    resolver.store[base_uri + "segment.schema.json"] = segment_schema
    resolver.store[base_uri + "storage_ref.schema.json"] = storage_ref_schema

    jsonschema.validate(instance=payload, schema=transcript_schema, resolver=resolver)
