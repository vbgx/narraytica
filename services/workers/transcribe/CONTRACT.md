# Transcribe Worker Contract — Narralytica

This document defines the **job payload and output artifacts** for the Transcribe worker.

It is the formal contract between:
- The orchestrator or API (job producer)
- The transcribe worker (job consumer)
- Downstream segmentation and enrichment steps

---

## 📥 Job Input Contract

The transcribe worker expects a job payload structured as follows:

```json
{
  "job_id": "string",
  "video_id": "string",
  "audio_object_key": "string",
  "language_hint": "string (optional)",
  "provider": "string (optional)"
}
```

## Field Descriptions

| Field              | Description                                   |
| ------------------ | --------------------------------------------- |
| `job_id`           | Unique identifier for this transcription job  |
| `video_id`         | Canonical video ID                            |
| `audio_object_key` | Storage location of the extracted audio       |
| `language_hint`    | Optional hint to guide ASR language selection |
| `provider`         | Optional ASR provider override                |

## 📤 Output Artifacts

After successful transcription, the worker must produce:

| Artifact            | Location       | Description                       |
| ------------------- | -------------- | --------------------------------- |
| Transcript file     | Object storage | Full transcript with timecodes    |
| Transcript metadata | Database       | Language, duration, provider used |
| Job status update   | Database       | Job marked as completed           |


Transcript format must align with the canonical schema defined in:

pgsql```
packages/contracts/schemas/transcript.schema.json
```

## 🔄 State Transitions

| State       | Meaning                           |
| ----------- | --------------------------------- |
| `pending`   | Job created but not started       |
| `running`   | ASR processing in progress        |
| `failed`    | Transcription failed              |
| `completed` | Transcript successfully generated |

---

## 🧱 Guarantees

The transcribe worker guarantees:

Transcript is fully time-aligned

Language is detected or confirmed

Artifacts are stored before marking job complete

Reprocessing does not create duplicate transcripts

## 🚫 Non-Responsibilities

The transcribe worker does not:

Split transcripts into semantic segments

Run AI enrichment layers

Generate embeddings

Index search data

Those steps occur in downstream workers.

## 📚 Related Contracts

Segment schema → packages/contracts/schemas/segment.schema.json

Video schema → packages/contracts/schemas/video.schema.json

---
