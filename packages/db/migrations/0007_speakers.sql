-- 0007_speakers.sql
-- EPIC01-05 — Postgres schema: speakers (identity & diarization-ready)

CREATE TABLE IF NOT EXISTS speakers (
  id              TEXT PRIMARY KEY,
  tenant_id       TEXT NULL,
  display_name    TEXT NULL,
  external_ref    TEXT NULL,
  metadata        JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS speakers_tenant_idx ON speakers (tenant_id);
CREATE INDEX IF NOT EXISTS speakers_external_ref_idx ON speakers (external_ref);

DROP TRIGGER IF EXISTS trg_speakers_set_updated_at ON speakers;
CREATE TRIGGER trg_speakers_set_updated_at
BEFORE UPDATE ON speakers
FOR EACH ROW
EXECUTE FUNCTION narralytica_set_updated_at();

-- Diarization-ready mapping (supports unknown speakers + overlaps)
CREATE TABLE IF NOT EXISTS segment_speakers (
  id          TEXT PRIMARY KEY,

  segment_id  TEXT NOT NULL REFERENCES segments(id) ON DELETE CASCADE,
  speaker_id  TEXT NULL REFERENCES speakers(id) ON DELETE SET NULL,

  confidence  REAL NULL CHECK (confidence >= 0 AND confidence <= 1),
  metadata    JSONB NOT NULL DEFAULT '{}'::jsonb,

  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS segment_speakers_segment_idx
  ON segment_speakers (segment_id);

CREATE INDEX IF NOT EXISTS segment_speakers_speaker_idx
  ON segment_speakers (speaker_id);

CREATE UNIQUE INDEX IF NOT EXISTS segment_speakers_unique_pair
  ON segment_speakers (segment_id, speaker_id)
  WHERE speaker_id IS NOT NULL;
