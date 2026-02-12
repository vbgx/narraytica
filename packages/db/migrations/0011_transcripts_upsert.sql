-- 0011_transcripts_upsert.sql
-- EPIC 03 — ISSUE 03.07 — Persist transcript metadata in DB (upsert + duration)

-- Add duration (seconds) if not present
ALTER TABLE transcripts
  ADD COLUMN IF NOT EXISTS duration_seconds DOUBLE PRECISION NULL;

-- Deterministic rerun behavior (no duplicates):
-- artifact_key is stable across reruns for a given job/version.
-- Use a PARTIAL unique index to avoid conflicts with legacy rows where artifact_key is NULL.
CREATE UNIQUE INDEX IF NOT EXISTS transcripts_unique_artifact
  ON transcripts (video_id, artifact_key, version)
  WHERE artifact_key IS NOT NULL;

-- Speed filtering by video/provider
CREATE INDEX IF NOT EXISTS transcripts_video_provider_idx
  ON transcripts (video_id, provider);
