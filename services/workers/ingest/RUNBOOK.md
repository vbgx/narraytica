# Ingest Worker Runbook --- Narralytica

This runbook describes how to operate, debug, and rerun the ingest
worker safely.

Use this guide when ingestion jobs fail, stall, or need to be
reprocessed.

------------------------------------------------------------------------

## When to Use This Runbook

Use this runbook if:

-   A video ingestion job is stuck
-   A download failed
-   Audio extraction failed
-   Metadata looks incorrect
-   Media files are missing from storage
-   A backfill requires re-ingesting videos

------------------------------------------------------------------------

## Step 1 --- Identify the Job

1.  Find the job ID via:
    -   Admin Console
    -   API `/jobs` endpoint
    -   Logs or alerts
2.  Check job status in the database:
    -   pending
    -   running
    -   failed
    -   completed

------------------------------------------------------------------------

## Step 2 --- Inspect Logs

Check worker logs for:

-   Download errors (timeouts, 403, platform blocks)
-   Storage upload failures
-   Audio extraction errors (ffmpeg issues)
-   File corruption or incomplete downloads

Logs should include the job ID for tracing.

------------------------------------------------------------------------

## Step 3 --- Verify Artifacts

Confirm the following exist in object storage:

  Artifact                Expected?
  ----------------------- -----------
  Original video file     Yes
  Extracted audio file    Yes
  Metadata record in DB   Yes

If artifacts are missing, ingestion did not complete properly.

------------------------------------------------------------------------

## Step 4 --- Retry the Job

Before retrying, confirm:

-   No duplicate media already stored
-   Previous partial files can be safely overwritten

Retry methods:

-   Use Admin Console Retry Job
-   Re-submit ingestion request via API
-   Manually reset job status (only if documented and safe)

The ingest worker must be idempotent.

------------------------------------------------------------------------

## Step 5 --- Clean Up Corrupt Artifacts

If a job left corrupted or partial files:

1.  Remove broken artifacts from object storage
2.  Reset job status to allow reprocessing
3.  Document cleanup in incident log if production

Never delete valid media without confirmation.

------------------------------------------------------------------------

## Common Failure Causes

  Issue                      Cause
  -------------------------- ------------------------------
  Video download blocked     Platform restrictions
  Timeout during download    Network instability
  Audio extraction failure   Corrupt or unsupported codec
  Storage upload error       Credentials or network issue

------------------------------------------------------------------------

## When to Escalate

Escalate if:

-   Multiple jobs fail with the same source
-   Storage system is unavailable
-   Worker crashes repeatedly
-   Corruption appears systemic

Follow incident procedures in:

-   docs/runbooks/incident.md

------------------------------------------------------------------------

## Related Docs

-   Pipeline overview → docs/architecture/pipelines.md
-   Storage architecture → docs/architecture/overview.md
-   Incident response → docs/runbooks/incident.md

------------------------------------------------------------------------

## Ingestion Phase Ownership

The ingest worker is responsible for updating ingestion_phase. The
orchestrator only manages the global job status.

### Phase Updates

  Phase                  status      ingestion_phase
  ---------------------- ----------- -----------------
  Start processing       running     downloading
  Audio extraction       running     processing
  Persisting artifacts   running     storing
  Success                succeeded   null
  Failure                failed      null

This separation ensures:

-   Orchestrator remains generic
-   Worker owns execution details
-   Database reflects real execution state
