cat > packages/shared/ids/CONVENTIONS.md <<'EOF'
# ID & Foreign Key Conventions (Canonical)

This document defines the **canonical identifier and foreign key conventions** across Narralytica.

It is referenced by:
- `docs/architecture/data-model.md`
- Postgres schema and migrations in `packages/db/`
- JSON Schemas and OpenAPI definitions in `packages/contracts/`

---

## Goals

- Make identifiers **stable across system boundaries**
- Prevent schema drift between DB and contracts
- Ensure naming is **predictable and grep-able**
- Enable safe exposure of IDs in public APIs

---

## ID format

### Canonical requirement
IDs MUST be:
- Globally unique
- Stable (never reused)
- Safe to expose externally
- Consistent across services

### Recommended formats
Prefer sortable IDs to improve DB locality and operational debugging:
- **ULID** (preferred)
- **UUIDv7** (acceptable)

### Storage type
- If ULID: store as `text` (or `char(26)` if you enforce fixed length)
- If UUIDv7: store as `uuid`

### Naming
- Primary key column MUST be named: `id`
- IDs must not include semantic meaning (no prefixes like `vid_`, `seg_`, etc.)

---

## Foreign key conventions

### Column naming
Foreign key columns MUST be named:

`<referenced_entity>_id`

Examples:
- `transcripts.video_id` → `videos.id`
- `segments.transcript_id` → `transcripts.id`
- `layers.segment_id` → `segments.id`
- `segment_speakers.segment_id` → `segments.id`
- `segment_speakers.speaker_id` → `speakers.id`
- `jobs.source_video_id` → `videos.id` (nullable lineage)
- `jobs.produced_layer_id` → `layers.id` (nullable lineage)

### Constraint naming
FK constraints SHOULD be named:

`fk_<child_table>_<parent_table>`

Examples:
- `fk_transcripts_videos`
- `fk_segments_transcripts`
- `fk_layers_segments`

### Referential actions (canonical intent)
- Ownership hierarchy uses `ON DELETE CASCADE`
- Lineage/log entities MUST NOT delete domain data (`NO CASCADE`)

Typical:
- `videos → transcripts` CASCADE
- `transcripts → segments` CASCADE
- `segments → layers` CASCADE
- `segments → segment_speakers` CASCADE
- `speakers → segment_speakers` CASCADE
- `jobs → domain entities` NO CASCADE (jobs are logs)

---

## Multi-tenancy

Tenant isolation is a first-class requirement.

### Tenant-scoped root entities
The following entities MUST include `tenant_id`:
- `videos`
- `speakers`
- `jobs`

Derived entities (transcripts/segments/layers) inherit tenant scope via FK chains and do not require redundant tenant columns.

### Rules
- Cross-tenant foreign keys are forbidden
- All queries MUST be tenant-filtered at the application boundary
- Tenant-scoped tables SHOULD be indexed by `(tenant_id, created_at)` and other common filters

---

## Versioning references

IDs identify objects; versions identify **snapshots of meaning**.

For AI outputs:
- Layer rows MUST include versioning metadata (e.g. `layer_type`, `model_version`, and optionally `prompt_hash`)
- Prefer uniqueness on `(segment_id, layer_type, model_version)` to prevent silent overwrite

---

## Do / Don’t

### Do
- Use `id` everywhere as PK
- Use `<entity>_id` everywhere as FK
- Keep ID generation centralized in `packages/shared/ids`
- Treat jobs/logs as append-only (no destructive cascades)

### Don’t
- Don’t expose internal numeric IDs in APIs
- Don’t encode semantics inside IDs
- Don’t create ad-hoc relationship columns without updating contracts + docs

EOF
