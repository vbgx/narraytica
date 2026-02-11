# EPIC 02 — Video Ingestion Pipeline

## 🎯 Goal

Build the pipeline that brings **raw video sources into Narralytica** and prepares them for downstream processing.

This EPIC transforms an external video reference (URL or upload) into structured internal assets: media files, audio tracks, and normalized metadata.

---

## 📦 Scope

This EPIC includes:

- API endpoint to register new videos for ingestion
- Job creation and orchestration for ingestion
- Media download from supported platforms (e.g. YouTube)
- Handling of direct uploads
- Storage of original video and extracted audio
- Metadata normalization and persistence

---

## 🚫 Non-Goals

This EPIC does **not** include:

- Speech-to-text transcription
- Speaker diarization
- AI enrichment
- Search indexing

It focuses only on **acquiring and preparing media**.

---

## 🧱 Pipeline Overview

1. User or system submits a video for ingestion
2. API creates a Video record and Ingestion job
3. Orchestrator schedules ingest worker
4. Worker downloads or receives media
5. Audio track is extracted
6. Media artifacts are stored in object storage
7. Metadata is normalized and saved
8. Job is marked as completed

---

## 🗂 Deliverables

- `/ingest` API route to submit ingestion jobs
- Job model extended for ingestion tracking
- Ingest worker implementation
- Media storage integration (MinIO/S3)
- Audio extraction pipeline
- Metadata normalization logic
- Status updates and error handling

---

## 🗂 Issues

1. Implement API endpoint to create ingestion job
2. Define ingestion job payload contract
3. Implement ingest worker skeleton
4. Add YouTube downloader module
5. Add upload ingestion path
6. Integrate object storage client
7. Implement audio extraction (ffmpeg)
8. Store normalized metadata in DB
9. Update job state transitions
10. Add logging and telemetry for ingestion
11. Write integration tests for ingestion flow
12. Document ingestion process in runbooks

---

## ✅ Definition of Done

EPIC 02 is complete when:

- A video URL can be submitted via API
- Media is downloaded and stored
- Audio file is extracted successfully
- Video metadata is persisted in DB
- Job state reflects completion or failure
- Re-running ingestion does not duplicate artifacts
- Logs clearly show ingestion lifecycle
- Runbook exists for ingestion troubleshooting

---

## ⚠️ Risks / Mitigations

| Risk | Mitigation |
|------|------------|
| Platform download restrictions | Use modular provider adapters |
| Large file handling issues | Stream downloads, avoid memory overload |
| Duplicate ingestion | Use dedupe keys and storage checks |
| Storage failures | Implement retries and integrity checks |

---

## 🔗 Links

- Pipelines overview → `docs/architecture/pipelines.md`
- Storage architecture → `docs/architecture/overview.md`
- Ingest worker → `services/workers/ingest/README.md`
- Job contracts → `services/workers/ingest/CONTRACT.md`
