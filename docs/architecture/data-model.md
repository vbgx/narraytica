# Data Model Architecture

## Purpose

This document defines the **canonical data model** of the system:
how core entities are structured, how they relate to each other, and how canonical and derived data are separated.

The data model is designed to be:

- Clear in ownership
- Consistent across services
- Evolvable without breaking contracts
- Aligned with system and pipeline boundaries

---

## Canonical vs Derived Data

The system distinguishes between **canonical data** and **derived data**.

### Canonical Data

Canonical data is the **source of truth** stored in the primary database (Postgres).

Examples in this system:

- Videos
- Transcripts
- Segments
- Speakers
- AI Layers
- Jobs

Canonical data must be:

- Strongly consistent
- Traceable
- Auditable
- Authoritative across services

---

### Derived Data

Derived data is computed from canonical sources and optimized for performance or specialized use cases.

Examples:

- Search indexes
- AI vector embeddings
- Aggregations and projections
- Materialized views

Derived data:

- Can be rebuilt from canonical sources
- Is eventually consistent
- Is never considered authoritative

---

## Core Domain Entities

The platform models spoken video as structured, queryable data.

| Entity | Description |
|--------|-------------|
| **Video** | A single video source and its metadata |
| **Transcript** | A full timecoded transcript of a video |
| **Segment** | A time-bounded unit of speech within a transcript |
| **Speaker** | A speaker identity detected or assigned |
| **Layer** | AI-generated analytical data attached to segments |
| **Job** | A processing job tracking pipeline execution |

---

## Canonical Relationships & Cardinalities

This section defines the **baseline relationship model** used consistently across:

- Postgres schema
- JSON Schemas
- OpenAPI contracts
- Pipelines

---

### Video → Transcript
**Cardinality:** `1 → N`

A video may have multiple transcripts (different providers, languages, or retries).

**Foreign key:**

`transcripts.video_id → videos.id``


**Ownership:**
Transcripts are owned by the video.

---

### Transcript → Segment
**Cardinality:** `1 → N`

A transcript consists of ordered, time-bounded speech segments.

**Foreign key:**

`segments.transcript_id → transcripts.id``


**Invariants:**

- `start_ms < end_ms`
- Deterministic order via `segment_index`
- Recommended uniqueness: `(transcript_id, segment_index)`

---

### Segment ↔ Speaker (Diarization)

**Cardinality:** `N ↔ N` via mapping table

A segment may contain multiple speakers, and a speaker may appear in many segments.

**Mapping table:**

| Column | Reference |
|--------|-----------|
| segment_id | → segments.id |
| speaker_id | → speakers.id |

This supports future overlap and complex diarization models.

---

### Segment → Layer
**Cardinality:** `1 → N`

Segments can have multiple AI-generated analytical layers.

Examples: summary, sentiment, topics, embeddings.

**Foreign key:**

`layers.segment_id → segments.id``

**Recommended uniqueness constraint:**

(segment_id, layer_type, model_version)


---

### Job Lineage (Processing Traceability)

Jobs do not own domain data.
They provide **traceability of processing operations**.

Jobs may reference:

- Source video
- Source transcript
- Source segment
- Produced layer

All such references are **nullable** and used for lineage only.

---

## Deletion Rules

Content hierarchy cascades downward.
Jobs are immutable logs and must not delete domain data.

| Parent | Child | Rule |
|--------|-------|------|
| videos | transcripts | CASCADE |
| transcripts | segments | CASCADE |
| segments | layers | CASCADE |
| segments | segment_speakers | CASCADE |
| speakers | segment_speakers | CASCADE |
| jobs | domain entities | NO CASCADE |

---

## Multi-Tenancy Considerations

Tenant isolation is a first-class requirement.

### Tenant-Scoped Root Entities

- Video
- Speaker
- Job

Each must include:

`tenant_id``


### Derived Scope

Transcripts, Segments, and Layers inherit tenant scope through foreign key chains and do not require redundant tenant columns.

### Rules

- Cross-tenant foreign keys are forbidden
- Queries must always be tenant-filtered
- Indexes should include `tenant_id` where applicable

---

## Identifiers

All entities use globally unique identifiers.

### Guidelines

- IDs must be stable across services
- IDs must never be reused
- Exposed IDs must be safe for public APIs
- Prefer ULID or UUIDv7 for sortability

### Naming Conventions

| Type | Format |
|------|--------|
| Primary key | `id` |
| Foreign key | `<entity>_id` |
| FK constraint | `fk_<child>_<parent>` |

Examples:

- `transcripts.video_id`
- `segments.transcript_id`
- `layers.segment_id`

---

## Schema Evolution

The data model must evolve safely.

### Rules

- Prefer additive changes
- Avoid renaming fields without migration
- Maintain backward compatibility in contracts
- Use DB migrations for structural changes
- Contract tests must guard cross-service expectations

---

## Denormalization Strategy

For performance:

- Some data may be denormalized into derived stores
- Canonical storage remains normalized and authoritative
- Derived representations must be rebuildable

---

## Validation and Constraints

Integrity is enforced through:

- Database constraints (FKs, uniqueness)
- Application-level validation
- Schema validation at pipeline boundaries

Validation should occur as early as possible.

---

## Summary

The data model architecture is built around:

- Clear separation of canonical vs derived data
- Strong tenant and identity boundaries
- Explicit, enforceable relationships
- Evolvable schemas with safe migration paths

A well-structured canonical data model enables:

- Reliable pipelines
- Consistent APIs
- Scalable AI enrichment
- Long-term system evolution

---

**End of Data Model Architecture Document**

---

## Storage references (canonical)

Large artifacts are not stored in Postgres. Postgres stores *references* using a canonical `storage_ref` object (JSONB).

`storage_ref` minimal fields:
- provider, bucket, key

Used for:
- video media objects (uploads, normalized media)
- transcript full artifacts (json/vtt/srt)
- derived blobs (future: embeddings exports, etc.)

Contract:
- packages/contracts/schemas/storage_ref.schema.json

---

## Storage references

Large artifacts are not stored in Postgres. Postgres stores references using the canonical `storage_ref` object (JSONB).

Used for:
- video media objects (uploads, normalized media)
- transcript full artifacts (json/vtt/srt)
- large derived blobs (optional: embeddings exports, etc.)

Contract:
- packages/contracts/schemas/storage_ref.schema.json
