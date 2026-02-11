# EPIC 02 — Video Ingestion Pipeline

## 🎯 Goal

Build the pipeline that brings **raw video sources into Narralytica** and prepares them for downstream processing.

This EPIC transforms an external video reference (URL or upload) into structured internal assets: media files, audio tracks, and normalized metadata.

## 📦 Scope

This EPIC includes:

- Defining the ingestion job contract
- API endpoint to register new videos for ingestion
- Job creation and orchestration for ingestion
- Media download from supported platforms (e.g. YouTube)
- Handling of direct uploads
- Storage of original video and extracted audio
- Metadata normalization and persistence
- Observability of the ingestion lifecycle

## 🚫 Non-Goals

This EPIC does **not** include:

- Speech-to-text transcription
- Speaker diarization
- AI enrichment
- Search indexing

It focuses only on **acquiring and preparing media**.

## 🧱 Pipeline Overview

1. Client submits a video URL or upload for ingestion
2. API validates the request and creates:
   - a **Video** record
   - an **Ingestion Job**
3. Orchestrator schedules the ingest worker
4. Worker retrieves media (download or upload source)
5. Media is stored in object storage
6. Audio track is extracted from the video
7. Metadata is normalized and persisted
8. Job state is updated through the lifecycle
9. Logs and telemetry capture the full ingestion trace

## 🗂 Deliverables

- Canonical ingestion job payload contract
- `/ingest` API route to submit ingestion jobs
- Job model extended for ingestion tracking and states
- Ingest worker implementation (pipeline skeleton)
- Media storage integration (MinIO/S3)
- YouTube downloader module
- Upload ingestion path
- Audio extraction pipeline (ffmpeg)
- Metadata normalization logic
- Logging, metrics, and error tracking
- Integration tests for ingestion flow
- Runbook for ingestion operations

## 🗂 Issues (Execution Order)

### Foundation Layer

1. **Define ingestion job payload contract**
   Establish the canonical structure of an ingestion job: source type, identifiers, deduplication keys, storage targets, and expected outputs.

2. **Implement API endpoint to create ingestion job**
   Create `/ingest` route that validates input, creates Video + Job records, and triggers orchestration.

3. **Update job state transitions**
   Define ingestion-specific job lifecycle states (queued → downloading → processing → completed/failed).

### Pipeline Core

4. **Implement ingest worker skeleton**
   Create the structured pipeline flow with placeholder stages and error boundaries.

5. **Integrate object storage client**
   Provide a unified interface to store original video and derived assets.

### Source Acquisition

6. **Add YouTube downloader module**
   Provider adapter to fetch media from YouTube (extensible for other platforms).

7. **Add upload ingestion path**
   Support ingestion of directly uploaded media files.

### Media Processing

8. **Implement audio extraction (ffmpeg)**
   Extract audio track from stored video and save as a new storage artifact.

9. **Store normalized metadata in DB**
   Parse and normalize metadata (duration, format, size, source info) and persist it.

### Observability & Quality

10. **Add logging and telemetry for ingestion**
    Ensure traceability of ingestion lifecycle, errors, durations, and storage references.

11. **Write integration tests for ingestion flow**
    End-to-end validation: API → job → worker → storage → metadata → job completion.

12. **Document ingestion process in runbooks**
    Operational guide for debugging, retries, and failure handling.

## ✅ Definition of Done

EPIC 02 is complete when:

- A video URL or upload can be submitted via API
- An ingestion job is created with a valid canonical payload
- Media is downloaded or received and stored
- Audio file is extracted successfully
- Video metadata is normalized and persisted in DB
- Job state reflects completion or failure accurately
- Re-running ingestion does not duplicate artifacts
- Logs clearly show the ingestion lifecycle
- Integration tests validate the full pipeline
- Runbook exists for ingestion troubleshooting

## ⚠️ Risks / Mitigations

| Risk | Mitigation |
|------|------------|
| Platform download restrictions | Use modular provider adapters |
| Large file handling issues | Stream downloads, avoid memory overload |
| Duplicate ingestion | Use dedupe keys and storage checks |
| Storage failures | Implement retries and integrity checks |

## 🔗 Links

- Pipelines overview → `docs/architecture/pipelines.md`
- Storage architecture → `docs/architecture/overview.md`
- Ingest worker → `services/workers/ingest/README.md`
- Job contracts → `services/workers/ingest/CONTRACT.md`
