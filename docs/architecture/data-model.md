# Data Model Architecture

## Purpose

This document defines the **canonical data model** of Narralytica: how core entities are structured, how they relate to each other, and which invariants pipelines and services must respect.

It is the cross-team reference for:
- Postgres schema (canonical truth)
- JSON Schemas (contracts)
- OpenAPI (API surface)
- Pipelines (ingest/transcribe/diarize/enrich/index)

Related:
- DB overview: `packages/db/schema.md`
- Canonical JSON schemas: `packages/contracts/schemas/*`

---

## Canonical vs Derived Data

**Canonical data** is the source of truth stored in Postgres:
- Videos, transcripts, segments, speakers
- Durable AI outputs (layers) stored as versioned artifacts
- Operational lineage (jobs, job_runs, job_events)

**Derived data** is rebuildable and non-authoritative:
- Search indexes
- Vector stores / embeddings indexes
- Projections, aggregations, read models

Rule of thumb:
> If it can be rebuilt deterministically from Postgres, it is derived.

---

## Entities

### Video
A **video** is the root canonical entity representing a single source (upload, YouTube, etc.) and its metadata. Videos support multiple origins via normalized source fields and may reference stored media objects via storage refs (bucket/key or canonical storage_ref).

Key fields:
- `id`
- source identity (e.g. `source_type`, `source_uri`, plus a stable `source_ref`)
- metadata (title/channel/duration/language/…)
- `created_at`, `updated_at`

### Transcript
A **transcript** is a timecoded representation of a video’s speech. Large transcript artifacts may live in object storage; Postgres stores metadata and a reference.

Key fields:
- `id`, `video_id`
- `provider` (optional), `language`, `status`
- artifact reference (bucket/key/format/size/checksum)
- versioning fields: `version`, `is_latest`
- `created_at`, `updated_at`

### Segment
A **segment** is the query backbone: a deterministic, ordered, time-bounded unit of speech within a transcript.

Key fields:
- `id`, `transcript_id`
- `segment_index` (ordering)
- `start_ms`, `end_ms`
- optional short `text`
- `created_at`, `updated_at`

### Speaker
A **speaker** is a canonical identity used for diarization and attribution. Speakers may be tenant-scoped and optionally carry external references.

Key fields:
- `id`, `tenant_id` (if speaker identities are tenant-scoped)
- `display_name`, `external_ref` (optional)
- metadata
- `created_at`, `updated_at`

### SegmentSpeaker (mapping)
A **segment_speakers** mapping attaches 0..N speakers to a segment (supports overlaps and “unknown” speakers). Speaker assignment may carry confidence and diarization metadata.

Key fields:
- `id`
- `segment_id`
- `speaker_id` (nullable for unknown)
- `confidence` (0..1), metadata
- `created_at`

### Layer
A **layer** is a durable, versioned AI output attached to a segment (summary/sentiment/topics/embeddings reference/etc.). Payload is stored as JSONB and must be contract-validatable.

Key fields:
- `id`, `segment_id`
- `layer_type`
- model context: provider/name/version, `prompt_hash`
- `payload` (JSONB), metadata
- `created_at`, `updated_at`

### Job / JobRun / JobEvent
A **job** is a logical pipeline request (ingest/transcribe/diarize/enrich/index). A **job_run** is an execution attempt (retries). A **job_event** is an optional append-only event stream for status transitions and auditability.

Key fields:
- Job: `id`, `type`, `status`, input refs (video/transcript/…), idempotency key, timestamps
- JobRun: `id`, `job_id`, `attempt`, status, started/finished, error model
- JobEvent: `id`, `job_id`, event_type, payload, timestamps

Jobs do not “own” domain data. They provide lineage and traceability.

---

## Relationships and Cardinalities

### Video → Transcript
**1 → N** (a video can have multiple transcripts)

FK:
- `transcripts.video_id → videos.id`

### Transcript → Segment
**1 → N** (a transcript consists of ordered segments)

FK:
- `segments.transcript_id → transcripts.id`

### Segment ↔ Speaker (Diarization)
**N ↔ N** via mapping table `segment_speakers`

FKs:
- `segment_speakers.segment_id → segments.id`
- `segment_speakers.speaker_id → speakers.id` (nullable; unknown speaker supported)

### Segment → Layer
**1 → N** (a segment can have multiple layers)

FK:
- `layers.segment_id → segments.id`

### Job lineage
Jobs may reference inputs/outputs (video/transcript/segment/layer) depending on the pipeline step. These references are for lineage and do not imply ownership.

---

## Storage References (Object Storage)

Large artifacts (media, full transcripts, large AI artifacts) live outside Postgres and are referenced safely.

Canonical contract:
- `packages/contracts/schemas/storage_ref.schema.json`

DB strategy (current):
- entity tables may store bucket/key/format/size/checksum fields (or a JSONB `storage_ref` in future)
- references must be immutable for a given artifact version

Invariants:
- bucket/key identify a stable object version
- checksum is recommended for integrity
- content_type/format must be explicit when multiple encodings exist (json/vtt/srt/…)

---

## Versioning Strategy

### Transcripts
Transcripts support multiple versions per video:
- `version` is monotonically increasing per `(video_id, language/provider context)`
- `is_latest = true` identifies the current canonical transcript for a video
- only one transcript per video should be `is_latest = true` at any time

### Layers
Layers are versioned by model/prompt context. A segment can have multiple layer rows per type, but must remain deterministic per version.

Recommended uniqueness:
- `(segment_id, layer_type, model_version, prompt_hash)`

This enables reproducibility and prevents silent overwrites.

---

## Invariants (must-haves)

### Time bounds and ordering
- Segments: `start_ms >= 0`, `end_ms > start_ms`
- `segment_index >= 0`
- deterministic ordering per transcript via `(transcript_id, segment_index)` unique

### Referential integrity
- Transcript must reference existing video
- Segment must reference existing transcript
- Layer must reference existing segment
- SegmentSpeaker must reference existing segment; speaker may be null (unknown)

### Tenant scoping
- Tenant-scoped roots (when present) must be filtered by tenant on every query
- Speaker identity is tenant-aware via `speakers.tenant_id` (if enabled)
- Derived entities inherit scope through FK chains (video → transcript → segment → layer)

### Deletion rules
Canonical hierarchy cascades downward:
- videos → transcripts (CASCADE)
- transcripts → segments (CASCADE)
- segments → layers and segment_speakers (CASCADE)
Speaker deletion should not delete segments; mappings should be safe (set null or delete mapping row depending on model).

---

## ER Diagram (Mermaid)

```mermaid
erDiagram
  VIDEOS ||--o{ TRANSCRIPTS : has
  TRANSCRIPTS ||--o{ SEGMENTS : has
  SEGMENTS ||--o{ LAYERS : has
  SEGMENTS ||--o{ SEGMENT_SPEAKERS : has
  SPEAKERS ||--o{ SEGMENT_SPEAKERS : appears_in

  JOBS ||--o{ JOB_RUNS : has
  JOBS ||--o{ JOB_EVENTS : emits

  VIDEOS {
    string id PK
    string source_ref
    string source_type
    string source_uri
    string title
    int duration_ms
    string language
    json metadata
    timestamptz created_at
    timestamptz updated_at
  }

  TRANSCRIPTS {
    string id PK
    string video_id FK
    string provider
    string language
    string status
    int version
    bool is_latest
    string artifact_bucket
    string artifact_key
    string artifact_format
    bigint artifact_bytes
    string artifact_sha256
    json metadata
    timestamptz created_at
    timestamptz updated_at
  }

  SEGMENTS {
    string id PK
    string transcript_id FK
    int segment_index
    int start_ms
    int end_ms
    string text
    json metadata
    timestamptz created_at
    timestamptz updated_at
  }

  SPEAKERS {
    string id PK
    string tenant_id
    string display_name
    string external_ref
    json metadata
    timestamptz created_at
    timestamptz updated_at
  }

  SEGMENT_SPEAKERS {
    string id PK
    string segment_id FK
    string speaker_id FK
    float confidence
    json metadata
    timestamptz created_at
  }

  LAYERS {
    string id PK
    string segment_id FK
    string layer_type
    string model_provider
    string model_name
    string model_version
    string prompt_hash
    json payload
    json metadata
    timestamptz created_at
    timestamptz updated_at
  }

  JOBS {
    string id PK
    string type
    string status
    json payload
    timestamptz created_at
    timestamptz updated_at
  }

  JOB_RUNS {
    string id PK
    string job_id FK
    int attempt
    string status
    timestamptz started_at
    timestamptz finished_at
    json error
    json metadata
    timestamptz created_at
    timestamptz updated_at
  }

  JOB_EVENTS {
    string id PK
    string job_id FK
    string event_type
    json payload
    timestamptz created_at
  }
  ```

  ---

  ## Contract Mapping

  Each canonical table has a matching contract schema:

Video → packages/contracts/schemas/video.schema.json

Transcript → packages/contracts/schemas/transcript.schema.json

Segment → packages/contracts/schemas/segment.schema.json

Speaker → packages/contracts/schemas/speaker.schema.json

Layer → packages/contracts/schemas/layer.schema.json

Job → packages/contracts/schemas/job.schema.json

JobRun → packages/contracts/schemas/job_run.schema.json

JobEvent → packages/contracts/schemas/job_event.schema.json

StorageRef → packages/contracts/schemas/storage_ref.schema.json

The DB overview remains in:

`packages/db/schema.md`
