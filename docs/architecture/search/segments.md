Segment Search Document (V1)

Purpose

Define the canonical searchable representation of a transcript segment.
This is a derived document used for retrieval (OpenSearch / Qdrant),
not a source of truth.

This specification defines:
- the canonical document shape (fields and invariants)
- ID rules (stable keys)
- DB field mapping
- storage split between OpenSearch and Qdrant

Source Tables (V1)

segments
transcripts

Canonical Identifiers

segment_id (required)
Stable identifier for a segment.

Rule (V1):
segment_id = segments.id

video_id (required)
Stable identifier of the parent media item.

Rule (V1):
video_id = transcripts.video_id

transcript_id (required for indexing pipeline)
Used internally to join segment to transcript.

Rule (V1):
transcript_id = segments.transcript_id

SegmentSearchDocument (V1) — Canonical Shape

Required fields:
- segment_id (string)
- video_id (string)
- start_ms (integer, >= 0)
- end_ms (integer, > start_ms)
- text (string, non-empty after normalization)

Optional filtering fields:
- language (string or null)
- source (string or null)
- speaker_id (string or null)
- speaker_name (string or null)

Optional timestamp fields:
- created_at (RFC3339 date-time string or null)
- updated_at (RFC3339 date-time string or null)

Optional retrieval ergonomics:
- snippet (string or null)
- tags (array of string or null)

Normalization Rules (V1)

Text:
- Trim leading and trailing whitespace
- Collapse consecutive whitespace into a single space
- Must remain non-empty after normalization

Timing:
0 <= start_ms < end_ms

Language:
- Prefer short language codes (fr, en, etc.)
- If unknown, set null

Source:
- Derived from transcripts.provider
- If unknown, set null

DB Mapping (V1)

segment_id  -> segments.id
video_id    -> transcripts.video_id
start_ms    -> segments.start_ms
end_ms      -> segments.end_ms
text        -> segments.text
language    -> transcripts.language
source      -> transcripts.provider
created_at  -> segments.created_at
updated_at  -> segments.updated_at

Storage Split

OpenSearch (lexical + filtering)

Index:
- text as analyzed full-text
- keyword fields:
  segment_id, video_id, language, source, speaker_id
- numeric fields:
  start_ms, end_ms
- date fields:
  created_at, updated_at

Qdrant (vector retrieval)

Vector:
- embedding of text

Payload:
- segment_id
- video_id
- language
- source
- start_ms
- end_ms
- created_at
- updated_at

Versioning

This is Version 1.

Breaking changes require:
- new OpenSearch index (segments-v2)
- new Qdrant collection (segments-v2)
- full reindex
