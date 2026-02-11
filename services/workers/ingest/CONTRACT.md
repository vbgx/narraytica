# Ingest Worker Contract — Narralytica

This document defines the canonical job payload and output artifacts
for the Ingest worker.

It is the formal contract between:

The API / orchestrator (job producer)

The ingest worker (job consumer)

Downstream processing steps

This contract is versioned.

📥 Job Input Contract (v2)

{
"type": "video_ingestion",
"version": "2.0",
"job_id": "string",
"video_id": "string",

"source": {
"kind": "youtube | upload | external_url",
"url": "string (if remote source)",
"object_key": "string (if upload)",
"provider": "youtube | custom",
"submitted_by": "user_id_or_system"
},

"dedupe": {
"strategy": "source_url | upload_hash",
"key": "normalized_value"
},

"artifacts": {
"video": {
"bucket": "raw-videos",
"object_key": "videos/{video_id}/source.mp4"
},
"audio": {
"bucket": "audio-tracks",
"object_key": "videos/{video_id}/audio.wav",
"format": "wav"
}
},

"metadata": {
"title": "string (optional)",
"channel": "string (optional)",
"language_hint": "string (optional)",
"capture_source_metadata": true
}
}

Field Descriptions

Core

type: Must be "video_ingestion"

version: Contract version (current = 2.0)

job_id: Unique ingestion job identifier

video_id: Canonical platform video ID

Source
Defines origin of media.

Rules:

youtube/external_url → url required

upload → object_key required

Deduplication
Ensures idempotent ingestion.

Strategy:

youtube/external_url → normalized canonical URL

upload → SHA256 of file

Worker MUST:

Check if artifacts already exist

Skip download if present

Never create duplicate artifacts

Artifacts (Deterministic Paths)

Paths MUST contain video_id.

This guarantees:

Safe retries

Predictable storage layout

No duplication on reprocessing

📤 Output Artifacts

After successful ingestion, the worker must produce:

Artifact	Location	Description
Original video file	Object storage	Raw media file
Extracted audio file	Object storage	Audio track for transcription
Normalized metadata	Database	Cleaned and standardized fields
Ingestion status update	Database	Job marked as completed

🔄 State Transitions

State	Meaning
pending	Job created but not started
running	Ingest worker is processing
downloading	Media retrieval phase
processing	Audio extraction / normalization
storing	Writing artifacts
failed	Ingestion failed
completed	Ingestion succeeded

🧱 Guarantees

The ingest worker guarantees:

Media files are stored before marking job complete

Audio extraction succeeds or job fails

Metadata is normalized before downstream steps

Reprocessing the same job does not create duplicates

Idempotent behavior based on dedupe.key

🚫 Non-Responsibilities

The ingest worker does not:

Perform transcription

Create segments

Run AI enrichment

Index search data

Those steps occur in later pipeline stages.

📚 Related Contracts

Transcript and segments → packages/contracts/schemas/transcript.schema.json
Segment indexing → packages/contracts/schemas/segment.schema.json
