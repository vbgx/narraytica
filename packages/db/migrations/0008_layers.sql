-- 0008_layers.sql
-- EPIC01-06 — Postgres schema: layers (AI outputs attached to segments)

CREATE TABLE IF NOT EXISTS layers (
  id               TEXT PRIMARY KEY,

  segment_id       TEXT NOT NULL REFERENCES segments(id) ON DELETE CASCADE,

  layer_type       TEXT NOT NULL,

  model_provider   TEXT NULL,
  model_name       TEXT NULL,
  model_version    TEXT NULL,
  prompt_hash      TEXT NULL,

  payload          JSONB NOT NULL,
  metadata         JSONB NOT NULL DEFAULT '{}'::jsonb,

  created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS layers_segment_idx
  ON layers (segment_id);

CREATE INDEX IF NOT EXISTS layers_type_created_idx
  ON layers (layer_type, created_at DESC);

CREATE UNIQUE INDEX IF NOT EXISTS layers_unique_versioned
  ON layers (segment_id, layer_type, model_version, prompt_hash);

DROP TRIGGER IF EXISTS trg_layers_set_updated_at ON layers;
CREATE TRIGGER trg_layers_set_updated_at
BEFORE UPDATE ON layers
FOR EACH ROW
EXECUTE FUNCTION narralytica_set_updated_at();
