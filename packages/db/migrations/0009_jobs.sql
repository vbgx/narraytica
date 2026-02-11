-- 0009_jobs.sql
-- EPIC01-07 — Postgres schema: jobs (pipeline tracking)
-- EPIC01-09 — Must run from empty DB

-- Ensure jobs exists for fresh DB
CREATE TABLE IF NOT EXISTS jobs (
  id         TEXT PRIMARY KEY,
  video_id   TEXT NOT NULL,
  type       TEXT NOT NULL,
  status     TEXT NOT NULL,
  payload    JSONB NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Ensure payload is JSONB for contract validation & indexing
ALTER TABLE jobs
  ALTER COLUMN payload TYPE JSONB
  USING COALESCE(payload, '{}'::jsonb);

-- Canonical timestamps for job lifecycle
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS queued_at    TIMESTAMPTZ NOT NULL DEFAULT now();
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS started_at   TIMESTAMPTZ NULL;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS finished_at  TIMESTAMPTZ NULL;

-- Idempotency
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS idempotency_key TEXT NULL;

-- Input refs (future-proof)
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS transcript_id TEXT NULL;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS segment_id    TEXT NULL;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS layer_id      TEXT NULL;

-- Optional scoping (tenant-ready)
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS tenant_id     TEXT NULL;

-- Update trigger
DROP TRIGGER IF EXISTS trg_jobs_set_updated_at ON jobs;
CREATE TRIGGER trg_jobs_set_updated_at
BEFORE UPDATE ON jobs
FOR EACH ROW
EXECUTE FUNCTION narralytica_set_updated_at();

-- Foreign keys (Postgres has no ADD CONSTRAINT IF NOT EXISTS)
DO $$
BEGIN
  BEGIN
    ALTER TABLE jobs ADD CONSTRAINT jobs_video_id_fkey
      FOREIGN KEY (video_id) REFERENCES videos(id) ON DELETE CASCADE;
  EXCEPTION WHEN duplicate_object THEN NULL; END;

  BEGIN
    ALTER TABLE jobs ADD CONSTRAINT jobs_transcript_id_fkey
      FOREIGN KEY (transcript_id) REFERENCES transcripts(id) ON DELETE SET NULL;
  EXCEPTION WHEN duplicate_object THEN NULL; END;

  BEGIN
    ALTER TABLE jobs ADD CONSTRAINT jobs_segment_id_fkey
      FOREIGN KEY (segment_id) REFERENCES segments(id) ON DELETE SET NULL;
  EXCEPTION WHEN duplicate_object THEN NULL; END;

  BEGIN
    ALTER TABLE jobs ADD CONSTRAINT jobs_layer_id_fkey
      FOREIGN KEY (layer_id) REFERENCES layers(id) ON DELETE SET NULL;
  EXCEPTION WHEN duplicate_object THEN NULL; END;
END $$;

-- Indexes for common API queries
CREATE INDEX IF NOT EXISTS jobs_video_created_idx
  ON jobs (video_id, created_at DESC);

CREATE INDEX IF NOT EXISTS jobs_status_created_idx
  ON jobs (status, created_at DESC);

CREATE INDEX IF NOT EXISTS jobs_type_created_idx
  ON jobs (type, created_at DESC);

CREATE INDEX IF NOT EXISTS jobs_queued_at_idx
  ON jobs (queued_at DESC);

-- Unique idempotency (only when present)
CREATE UNIQUE INDEX IF NOT EXISTS jobs_idempotency_unique
  ON jobs (idempotency_key)
  WHERE idempotency_key IS NOT NULL;


-- ---------------------------------------------------------------------------
-- job_runs: retries/attempts for a logical job
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS job_runs (
  id            TEXT PRIMARY KEY,

  job_id        TEXT NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
  attempt       INTEGER NOT NULL CHECK (attempt >= 1),

  status        TEXT NOT NULL,

  started_at    TIMESTAMPTZ NULL,
  finished_at   TIMESTAMPTZ NULL,

  -- error model aligned with services/api/ERROR_MODEL.md
  error_code           TEXT NULL,
  error_message        TEXT NULL,
  error_details        JSONB NULL,
  error_correlation_id TEXT NULL,

  metadata      JSONB NOT NULL DEFAULT '{}'::jsonb,

  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS job_runs_job_attempt_unique
  ON job_runs (job_id, attempt);

CREATE INDEX IF NOT EXISTS job_runs_job_created_idx
  ON job_runs (job_id, created_at DESC);

CREATE INDEX IF NOT EXISTS job_runs_status_created_idx
  ON job_runs (status, created_at DESC);

DROP TRIGGER IF EXISTS trg_job_runs_set_updated_at ON job_runs;
CREATE TRIGGER trg_job_runs_set_updated_at
BEFORE UPDATE ON job_runs
FOR EACH ROW
EXECUTE FUNCTION narralytica_set_updated_at();


-- ---------------------------------------------------------------------------
-- job_events: append-only event log (optional)
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS job_events (
  id           TEXT PRIMARY KEY,

  job_id       TEXT NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
  run_id       TEXT NULL REFERENCES job_runs(id) ON DELETE CASCADE,

  event_type   TEXT NOT NULL,
  payload      JSONB NOT NULL DEFAULT '{}'::jsonb,

  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS job_events_job_created_idx
  ON job_events (job_id, created_at DESC);

CREATE INDEX IF NOT EXISTS job_events_run_created_idx
  ON job_events (run_id, created_at DESC);
