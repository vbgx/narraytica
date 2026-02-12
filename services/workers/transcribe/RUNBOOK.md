# Transcribe Worker Runbook — Narralytica

This runbook explains how to **operate, debug, and safely rerun** the transcription pipeline.

Use it whenever transcription jobs fail, stall, or produce incorrect output.

---

## 🎯 When to Use This Runbook

Use this guide if:

- A transcription job is stuck in `running`
- A job failed with an ASR/provider error
- Transcripts are missing, empty, or incomplete
- Language detection is wrong
- You need to backfill or re-transcribe historical audio
- Transcription latency or failure rate spikes

---

## 🧭 Transcription Pipeline Overview

**Flow**

1. Audio artifact becomes available (from ingest worker)
2. Transcribe worker picks up the job
3. ASR provider processes audio
4. Transcript artifact is stored
5. Transcript metadata is written to DB
6. Job marked `completed`

If any step fails, job may remain `running` or move to `failed`.

---

## 🔍 Step 1 — Identify the Job

Locate the job using:

- Admin Console
- API `GET /jobs`
- Alert payload
- Worker logs

Record:

- `job_id`
- `video_id`
- Audio storage reference (`bucket`, `object_key`)
- Current job status (`queued`, `running`, `failed`, `completed`)

---

## 🪵 Step 2 — Inspect Worker Logs

Check logs for the specific job.

Filter by:

- `job_id`
- `video_id`

Look for these common errors:

| Error Type | Possible Cause |
|------------|----------------|
| ASR timeout | Provider delay, very long audio |
| Provider authentication error | Invalid API key, expired key, quota exceeded |
| Rate limit error | Too many concurrent ASR calls |
| Unsupported audio format | Corrupt file or unsupported codec |
| Empty transcript | Silent audio or provider failure |
| Worker crash | Memory exhaustion or unhandled exception |

If logs stop abruptly → worker may have crashed or restarted.

---

## 📦 Step 3 — Verify Audio Artifact

Confirm the audio file used for transcription:

- Exists in object storage
- Has non-zero size
- Matches expected duration

### Example check (local)

```
ffprobe s3://audio-bucket/videos/{video_id}/audio.wav
```

Or download locally and run:

```
ffprobe audio.wav
```

If audio is invalid or missing → problem originated in **ingestion**, not transcription.

---

## 🧾 Step 4 — Verify Transcript Output

Check for both **storage** and **database** consistency.

| Check | Expected |
|------|----------|
| Transcript artifact in storage | Present |
| Transcript record in DB | Present |
| Language metadata | Present |
| Duration metadata | Matches audio |

If transcript file exists but DB row is missing → indexing step failed.
If DB row exists but file missing → storage write failed.

---

## 📉 Step 5 — Check System Metrics

When issues are systemic (not a single job), check:

| Metric | What to Watch |
|-------|----------------|
| Transcription latency | Sudden increase → provider slowdown |
| Failure rate | Spike → provider outage or auth issue |
| Retry count | High retries → unstable provider |
| Cost per minute | Unexpected spike → model mismatch |

Metrics help distinguish **single-job issue vs system issue**.

---

## 🔁 Step 6 — Retry the Job Safely

Before retrying:

- Confirm a **valid transcript does NOT already exist**
- Confirm the audio file is valid
- Confirm ASR provider quota is available

### Safe Retry Methods

**Option 1 — Admin Console**
Click **Retry Job**

**Option 2 — API**
```
POST /jobs/{job_id}/retry
```

**Option 3 — Manual (advanced only)**

- Delete corrupted transcript artifact
- Reset job state to `queued`
- Re-enqueue job

⚠️ Transcription must be **idempotent**. Never create duplicate transcript records.

---

## 🧼 Step 7 — Cleaning Partial or Corrupted Results

If a transcript is corrupted or truncated:

1. Delete the broken transcript artifact from storage
2. Remove or reset transcript DB record
3. Reset job to `queued`
4. Re-run transcription

Never overwrite a valid transcript without verification.

---

## ⚠️ Common Failure Causes

| Issue | Root Cause |
|------|-------------|
| Long audio timeout | Provider max duration limit |
| API rate limit | Too many parallel jobs |
| Unsupported language | Model doesn’t support detected language |
| Silent transcript | Audio contains silence or extreme noise |
| Worker OOM | Audio too large, memory limit exceeded |
| Repeated retries | Provider instability |

---

## 🛑 When to Escalate

Escalate to engineering if:

- Multiple jobs fail across different videos
- Provider returns 5xx errors consistently
- Failure rate > normal baseline
- Transcripts are systematically corrupted
- Worker crashes repeatedly

Follow incident process:
`docs/runbooks/incident.md`

---

## 🧪 Local Debug Procedure

To reproduce locally:

1. Download audio artifact
2. Run transcription worker locally with same provider config
3. Compare output with production transcript

Example:

```
python -m workers.transcribe.run --audio sample.wav
```

---

## 🔐 Safety Rules

- Never delete transcripts without verifying corruption
- Never retry jobs blindly in bulk
- Always confirm provider quotas before backfills
- Avoid reprocessing already successful jobs

---

## 📚 Related Documentation

- Pipeline overview → `docs/architecture/pipelines.md`
- Transcription contracts → `packages/contracts`
- Incident response → `docs/runbooks/incident.md`
- Ingest runbook → `services/workers/ingest/RUNBOOK.md`
