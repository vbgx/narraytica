# Diarize Worker Contract — Narralytica

This document defines the **job payload and output artifacts** for the Diarize worker.

It is the formal contract between:
- The orchestrator (job producer)
- The diarize worker (job consumer)
- Downstream enrichment and speaker analysis steps

---

## 📥 Job Input Contract

The diarize worker expects a job payload structured as follows:

```json
{
  "job_id": "string",
  "video_id": "string",
  "transcript_object_key": "string",
  "audio_object_key": "string",
  "config": {
    "min_speakers": "number (optional)",
    "max_speakers": "number (optional)"
  }
}
```

## Field Descriptions
Field	Description
job_id	Unique identifier for this diarization job
video_id	Canonical video ID
transcript_object_key	Storage location of the transcript
audio_object_key	Storage location of the audio file
config	Optional diarization configuration

## 📤 Output Artifacts
After successful diarization, the worker must produce:

Artifact	Location	Description
Speaker segments	Database	Transcript segments labeled with speaker IDs
Speaker timeline	Database	Ordered timeline of speaker turns
Job status update	Database	Job marked as completed
Output must align with:

`packages/contracts/schemas/speaker.schema.json`

## 🔄 State Transitions
State	Meaning
pending	Job created but not started
running	Diarization in progress
failed	Diarization failed
completed	Speaker segmentation succeeded

## 🧱 Guarantees
The diarize worker guarantees:

Speaker turns align with transcript timestamps

Speaker labels are consistent within a video

Artifacts are stored before marking job complete

Reprocessing replaces previous speaker segmentation safely

## 🚫 Non-Responsibilities
The diarize worker does not:

Identify real-world speaker identity

Run semantic AI enrichment

Generate embeddings

Index search data

These tasks belong to later stages of the pipeline.

## 📚 Related Contracts
Transcript schema → packages/contracts/schemas/transcript.schema.json

Segment schema → packages/contracts/schemas/segment.schema.json

---
