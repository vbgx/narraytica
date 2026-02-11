-- 0008_layers.sql
-- EPIC01-06 — Postgres schema: layers (AI outputs attached to segments)

CREATE TABLE IF NOT EXISTS layers (
  id               TEXT PRIMARY KEY,

  segment_id       TEXT NOT NULL REFERENCES segments(id) ON DELETE CASCADE,

  layer_type       TEXT NOT NULL,  -- e.g. summary, embedding, sentiment

  model_provider   TEXT NULL,      -- openai, local, anthropic, etc.
  model_name       TEXT NULL,      -- gpt-4o, mistral-large, etc.
  model_version    TEXT NULL,      -- version or revision
  prompt_hash      TEXT NULL,      -- reproducibility hash

  payload          JSONB NOT NULL, -- validated against contracts

  metadata         JSONB NOT NULL DEFAULT '{}'::jsonb,

  created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Fast lookup of layers for a segment
CREATE INDEX IF NOT EXISTS layers_segment_idx
  ON layers (segment_id);

-- Filtering by layer type and recency
CREATE INDEX IF NOT EXISTS layers_type_created_idx
  ON layers (layer_type, created_at DESC);

-- Ensure deterministic uniqueness per model + version context
CREATE UNIQUE INDEX IF NOT EXISTS layers_unique_versioned
  ON layers (segment_id, layer_type, model_version, prompt_hash);

DROP TRIGGER IF EXISTS trg_layers_set_updated_at ON layers;
CREATE TRIGGER trg_layers_set_updated_at
BEFORE UPDATE ON layers
FOR EACH ROW
EXECUTE FUNCTION narralytica_set_updated_at();
