-- 0005_transcripts.sql
-- EPIC01-03 — Postgres schema: transcripts (canonical + storage refs)

CREATE TABLE IF NOT EXISTS transcripts (
  id                TEXT PRIMARY KEY,

  -- multi-tenant (nullable at v0 but schema-ready)
  tenant_id         TEXT NULL,

  -- parent video (canonical)
  video_id          TEXT NOT NULL REFERENCES videos(id) ON DELETE CASCADE,

  -- transcription metadata
  provider          TEXT NULL,        -- e.g. "whisper", "deepgram", "assemblyai"
  language          TEXT NULL,        -- BCP-47 ("fr", "en", "en-US", etc.)

  status            TEXT NOT NULL DEFAULT 'pending',
  CONSTRAINT transcripts_status_valid CHECK (
    status IN ('pending', 'processing', 'completed', 'failed')
  ),

  -- artifact storage reference (full transcript as JSON/VTT/SRT, etc.)
  artifact_bucket   TEXT NULL,
  artifact_key      TEXT NULL,
  artifact_format   TEXT NULL,        -- e.g. "json", "vtt", "srt"
  artifact_bytes    BIGINT NULL CHECK (artifact_bytes >= 0),
  artifact_sha256   TEXT NULL,        -- optional integrity

  -- versioning (lightweight; aligns with future versioning strategy)
  version           INTEGER NOT NULL DEFAULT 1 CHECK (version >= 1),
  is_latest         BOOLEAN NOT NULL DEFAULT TRUE,

  -- extensible metadata (provider payloads, confidence stats, etc.)
  metadata          JSONB NOT NULL DEFAULT '{}'::jsonb,

  created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- updated_at trigger (function defined in 0004_videos.sql)
DROP TRIGGER IF EXISTS trg_transcripts_set_updated_at ON transcripts;
CREATE TRIGGER trg_transcripts_set_updated_at
BEFORE UPDATE ON transcripts
FOR EACH ROW
EXECUTE FUNCTION narralytica_set_updated_at();

-- Indexes: common queries
CREATE INDEX IF NOT EXISTS transcripts_video_id_idx
  ON transcripts (video_id);

CREATE INDEX IF NOT EXISTS transcripts_status_idx
  ON transcripts (status);

CREATE INDEX IF NOT EXISTS transcripts_created_at_idx
  ON transcripts (created_at DESC);

-- Common pattern: list transcripts for a video with newest first
CREATE INDEX IF NOT EXISTS transcripts_video_created_at_idx
  ON transcripts (video_id, created_at DESC);

-- Optional scoping index (if/when tenant scoping is enforced)
CREATE INDEX IF NOT EXISTS transcripts_tenant_created_at_idx
  ON transcripts (tenant_id, created_at DESC);

-- Optional: help retrieving latest version quickly
CREATE INDEX IF NOT EXISTS transcripts_video_is_latest_idx
  ON transcripts (video_id, is_latest)
  WHERE is_latest = TRUE;
