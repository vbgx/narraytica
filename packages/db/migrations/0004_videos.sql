-- 0004_videos.sql
-- EPIC01-02 — Postgres schema: videos (canonical)

CREATE TABLE IF NOT EXISTS videos (
  id                TEXT PRIMARY KEY,

  -- multi-tenant (nullable at v0 but schema-ready)
  tenant_id         TEXT NULL,
  org_id            TEXT NULL,
  user_id           TEXT NULL,

  -- provenance / identity
  source_type       TEXT NOT NULL,
  source_uri        TEXT NOT NULL,

  -- common metadata (hot path)
  title             TEXT NULL,
  channel           TEXT NULL,
  duration_ms       INTEGER NULL CHECK (duration_ms >= 0),
  language          TEXT NULL, -- BCP-47 ("en", "fr", "en-US", etc.)
  published_at      TIMESTAMPTZ NULL,

  -- object storage references
  storage_bucket    TEXT NULL,
  storage_key       TEXT NULL,

  -- extensible metadata
  metadata          JSONB NOT NULL DEFAULT '{}'::jsonb,

  created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT now(),

  CONSTRAINT videos_source_type_nonempty CHECK (length(trim(source_type)) > 0),
  CONSTRAINT videos_source_uri_nonempty  CHECK (length(trim(source_uri)) > 0)
);

-- prevent duplicate ingestion of same source
CREATE UNIQUE INDEX IF NOT EXISTS videos_source_unique
  ON videos (source_type, source_uri);

-- common listing queries
CREATE INDEX IF NOT EXISTS videos_created_at_idx
  ON videos (created_at DESC);

CREATE INDEX IF NOT EXISTS videos_tenant_created_at_idx
  ON videos (tenant_id, created_at DESC);

CREATE INDEX IF NOT EXISTS videos_org_created_at_idx
  ON videos (org_id, created_at DESC);

CREATE INDEX IF NOT EXISTS videos_user_created_at_idx
  ON videos (user_id, created_at DESC);

-- auto-update updated_at
CREATE OR REPLACE FUNCTION narralytica_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_videos_set_updated_at ON videos;
CREATE TRIGGER trg_videos_set_updated_at
BEFORE UPDATE ON videos
FOR EACH ROW
EXECUTE FUNCTION narralytica_set_updated_at();
