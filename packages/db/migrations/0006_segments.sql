-- 0006_segments.sql
-- EPIC01-04 — Postgres schema: segments (timecoded speech units)

CREATE TABLE IF NOT EXISTS segments (
  id              TEXT PRIMARY KEY,

  transcript_id   TEXT NOT NULL REFERENCES transcripts(id) ON DELETE CASCADE,

  segment_index   INTEGER NOT NULL CHECK (segment_index >= 0),

  start_ms        INTEGER NOT NULL CHECK (start_ms >= 0),
  end_ms          INTEGER NOT NULL CHECK (end_ms > start_ms),

  text            TEXT NULL, -- optional short text snippet

  metadata        JSONB NOT NULL DEFAULT '{}'::jsonb,

  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Ensure deterministic ordering per transcript
CREATE UNIQUE INDEX IF NOT EXISTS segments_transcript_order_unique
  ON segments (transcript_id, segment_index);

-- Time-based retrieval within transcript
CREATE INDEX IF NOT EXISTS segments_transcript_time_idx
  ON segments (transcript_id, start_ms);

-- Auto-update updated_at
DROP TRIGGER IF EXISTS trg_segments_set_updated_at ON segments;
CREATE TRIGGER trg_segments_set_updated_at
BEFORE UPDATE ON segments
FOR EACH ROW
EXECUTE FUNCTION narralytica_set_updated_at();
