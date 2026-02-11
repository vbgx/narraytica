-- 0007_speakers.sql
-- EPIC01-05 — Postgres schema: speakers (identity & diarization-ready)

CREATE TABLE IF NOT EXISTS speakers (
  id              TEXT PRIMARY KEY,

  tenant_id       TEXT NULL, -- allows per-tenant or global speakers

  display_name    TEXT NULL,
  external_ref    TEXT NULL, -- optional external identity (YouTube channel, CRM id, etc.)

  metadata        JSONB NOT NULL DEFAULT '{}'::jsonb,

  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- optional lookup helpers
CREATE INDEX IF NOT EXISTS speakers_tenant_idx ON speakers (tenant_id);
CREATE INDEX IF NOT EXISTS speakers_external_ref_idx ON speakers (external_ref);

DROP TRIGGER IF EXISTS trg_speakers_set_updated_at ON speakers;
CREATE TRIGGER trg_speakers_set_updated_at
BEFORE UPDATE ON speakers
FOR EACH ROW
EXECUTE FUNCTION narralytica_set_updated_at();


-- =====================================================
-- Segment ↔ Speaker mapping (many-to-many, diarization)
-- =====================================================

CREATE TABLE IF NOT EXISTS segment_speakers (
  segment_id   TEXT NOT NULL REFERENCES segments(id) ON DELETE CASCADE,
  speaker_id   TEXT NULL REFERENCES speakers(id) ON DELETE SET NULL,

  -- confidence or diarization metadata
  confidence   REAL NULL CHECK (confidence >= 0 AND confidence <= 1),
  metadata     JSONB NOT NULL DEFAULT '{}'::jsonb,

  created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),

  PRIMARY KEY (segment_id, speaker_id)
);

CREATE INDEX IF NOT EXISTS segment_speakers_speaker_idx
  ON segment_speakers (speaker_id);

CREATE INDEX IF NOT EXISTS segment_speakers_segment_idx
  ON segment_speakers (segment_id);
