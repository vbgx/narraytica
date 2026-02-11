# Ingest Worker Contract — Narralytica

This document defines the **job payload and output artifacts** for the Ingest worker.

It is the formal contract between:
- The API / orchestrator (job producer)
- The ingest worker (job consumer)
- Downstream processing steps

---

## 📥 Job Input Contract

The ingest worker expects a job payload with the following structure:

```json
{
  "job_id": "string",
  "video_id": "string",
  "source": {
    "type": "youtube | upload",
    "url": "string (if youtube)",
    "object_key": "string (if upload)"
  },
  "metadata": {
    "title": "string",
    "channel": "string",
    "language_hint": "string (optional)"
  }
}
```

## Field Descriptions

Field	Description
job_id	Unique identifier for this ingestion job
video_id	Canonical ID of the video in the platform
source.type	Source type (youtube or upload)
source.url	Video URL for remote ingestion
source.object_key	Storage key for uploaded file
metadata	Optional initial metadata

## 📤 Output Artifacts
After successful ingestion, the worker must produce:

Artifact	Location	Description
Original video file	Object storage	Raw media file
Extracted audio file	Object storage	Audio track for transcription
Normalized metadata	Database	Cleaned and standardized fields
Ingestion status update	Database	Job marked as completed

## 🔄 State Transitions
State	Meaning
pending	Job created but not yet started
running	Ingest worker is processing
failed	Ingestion failed
completed	Ingestion succeeded

## 🧱 Guarantees
The ingest worker guarantees:

Media files are stored before marking job complete

Audio extraction succeeds or job fails

Metadata is normalized before downstream steps

Reprocessing the same job does not create duplicates

## 🚫 Non-Responsibilities
The ingest worker does not:

Perform transcription

Create segments

Run AI enrichment

Index search data

Those steps occur in later pipeline stages.

## 📚 Related Contracts
Transcript and segments → packages/contracts/schemas/transcript.schema.json

Segment indexing → packages/contracts/schemas/segment.schema.json

---