-- 0010_storage_refs.sql
-- EPIC01-08 — Canonical object storage references (storage_ref)

-- Canonical shape lives in contracts:
-- packages/contracts/schemas/storage_ref.schema.json
--
-- DB strategy:
-- - add storage_ref JSONB on entities that reference large artifacts
-- - backfill from existing columns where possible
-- - keep legacy columns for now (deprecated), to avoid breaking code

/* -------------------------------------------------------------------------- */
/* transcripts: backfill from artifact_* columns                               */
/* -------------------------------------------------------------------------- */

ALTER TABLE transcripts
  ADD COLUMN IF NOT EXISTS storage_ref JSONB NULL;

-- Backfill storage_ref from existing artifact columns (only when present)
UPDATE transcripts
SET storage_ref = jsonb_strip_nulls(jsonb_build_object(
  'provider', 'minio',
  'bucket', artifact_bucket,
  'key', artifact_key,
  'content_type',
    CASE
      WHEN artifact_format IS NULL THEN NULL
      WHEN lower(artifact_format) = 'json' THEN 'application/json'
      WHEN lower(artifact_format) = 'vtt'  THEN 'text/vtt'
      WHEN lower(artifact_format) = 'srt'  THEN 'application/x-subrip'
      ELSE NULL
    END,
  'size_bytes', artifact_bytes,
  'checksum',
    CASE
      WHEN artifact_sha256 IS NULL OR length(trim(artifact_sha256)) = 0 THEN NULL
      ELSE 'sha256:' || artifact_sha256
    END
))
WHERE storage_ref IS NULL
  AND artifact_bucket IS NOT NULL
  AND artifact_key IS NOT NULL;

CREATE INDEX IF NOT EXISTS transcripts_storage_ref_gin_idx
  ON transcripts USING GIN (storage_ref);

/* -------------------------------------------------------------------------- */
/* videos: backfill from storage_bucket/storage_key columns                    */
/* -------------------------------------------------------------------------- */

ALTER TABLE videos
  ADD COLUMN IF NOT EXISTS storage_ref JSONB NULL;

UPDATE videos
SET storage_ref = jsonb_strip_nulls(jsonb_build_object(
  'provider', 'minio',
  'bucket', storage_bucket,
  'key', storage_key
))
WHERE storage_ref IS NULL
  AND storage_bucket IS NOT NULL
  AND storage_key IS NOT NULL;

CREATE INDEX IF NOT EXISTS videos_storage_ref_gin_idx
  ON videos USING GIN (storage_ref);

/* -------------------------------------------------------------------------- */
/* layers: optional storage refs for large derived artifacts (future-proof)    */
/* -------------------------------------------------------------------------- */

ALTER TABLE layers
  ADD COLUMN IF NOT EXISTS storage_ref JSONB NULL;

CREATE INDEX IF NOT EXISTS layers_storage_ref_gin_idx
  ON layers USING GIN (storage_ref);
