#!/usr/bin/env bash
set -euo pipefail

# Load env files if present
for f in .env.local .env; do
  if [ -f "$f" ]; then
    set -a
    . "$f"
    set +a
  fi
done

# Never let libpq defaults override our explicit URLs
unset PGHOST PGPORT PGUSER PGDATABASE PGSSLMODE PGOPTIONS

# Prefer API_DATABASE_URL (SQLAlchemy style) as the single source of truth.
# Example: postgresql+psycopg://user:pass@127.0.0.1:15432/dbname
if [ -n "${API_DATABASE_URL:-}" ]; then
  DB_URL="$(python3 - <<'PY'
import os, re
u = os.environ["API_DATABASE_URL"]
u = re.sub(r"^postgresql\+\w+://", "postgresql://", u)  # strip +psycopg
print(u)
PY
)"
else
  DB_HOST="${POSTGRES_HOST:-127.0.0.1}"
  DB_PORT="${POSTGRES_PORT:-15432}"
  DB_USER="${POSTGRES_USER:-narralytica}"
  DB_PASS="${POSTGRES_PASSWORD:-narralytica}"
  DB_NAME="${POSTGRES_DB:-narralytica}"
  export PGPASSWORD="$DB_PASS"
  DB_URL="postgresql://$DB_USER@$DB_HOST:$DB_PORT/$DB_NAME"
fi

# Admin DB = same DB, we just need a place to CREATE/DROP DATABASE
ADMIN_URL="$DB_URL"

DB_NAME="narralytica_migrate_test_$RANDOM"

echo "Using DB_URL=$DB_URL"
export PGPASSWORD="${POSTGRES_PASSWORD:-${DB_PASS:-}}"

# Create empty DB
psql "$ADMIN_URL" -v ON_ERROR_STOP=1 -c "CREATE DATABASE $DB_NAME;"

# Apply migrations in order
for f in $(ls -1 packages/db/migrations/*.sql | sort); do
  psql "${DB_URL%/*}/$DB_NAME" -v ON_ERROR_STOP=1 -f "$f"
done

# Basic presence check (core model)
psql "${DB_URL%/*}/$DB_NAME" -v ON_ERROR_STOP=1 <<'SQL'
SELECT 'videos'      AS tbl, to_regclass('public.videos')      IS NOT NULL AS exists UNION ALL
SELECT 'transcripts' AS tbl, to_regclass('public.transcripts') IS NOT NULL AS exists UNION ALL
SELECT 'segments'    AS tbl, to_regclass('public.segments')    IS NOT NULL AS exists UNION ALL
SELECT 'speakers'    AS tbl, to_regclass('public.speakers')    IS NOT NULL AS exists UNION ALL
SELECT 'layers'      AS tbl, to_regclass('public.layers')      IS NOT NULL AS exists UNION ALL
SELECT 'jobs'        AS tbl, to_regclass('public.jobs')        IS NOT NULL AS exists UNION ALL
SELECT 'job_runs'    AS tbl, to_regclass('public.job_runs')    IS NOT NULL AS exists UNION ALL
SELECT 'job_events'  AS tbl, to_regclass('public.job_events')  IS NOT NULL AS exists;
SQL

# Cleanup
psql "$ADMIN_URL" -v ON_ERROR_STOP=1 -c "DROP DATABASE $DB_NAME;"

echo "OK: migrations apply cleanly from empty DB ($DB_NAME)."
