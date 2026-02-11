# Transcribe Worker Runbook — Narralytica

This runbook explains how to **operate, debug, and rerun** the transcription pipeline safely.

Use it when transcription jobs fail, stall, or produce unexpected results.

---

## 🎯 When to Use This Runbook

Use this guide if:

- A transcription job is stuck in `running`
- A job failed with an ASR error
- Transcripts are missing or incomplete
- Language detection is incorrect
- A backfill requires re-transcribing audio

---

## 🔍 Step 1 — Identify the Job

Find the job via:

- Admin Console
- API `/jobs` endpoint
- Logs or alerts

Record:
- `job_id`
- `video_id`
- Audio file reference

---

## 🪵 Step 2 — Inspect Logs

Check worker logs for:

| Error Type | Possible Cause |
|-----------|----------------|
| ASR timeout | Provider delay or long audio |
| Authentication error | Invalid API key or quota exceeded |
| Unsupported format | Corrupt or unsupported audio codec |
| Partial transcript | Job interrupted or memory issue |

Logs should include job and video IDs.

---

## 📦 Step 3 — Verify Audio Artifact

Confirm the audio file:

- Exists in object storage
- Is not corrupted
- Has expected duration

If audio is invalid, ingestion may have failed earlier.

---

## 🧾 Step 4 — Verify Transcript Output

Check:

| Artifact | Expected? |
|----------|-----------|
| Transcript file in storage | Yes |
| Transcript record in DB | Yes |
| Language metadata | Yes |

If transcript exists but DB record is missing, indexing may be incomplete.

---

## 🔁 Step 5 — Retry the Job

Before retrying:

- Confirm no valid transcript already exists
- Ensure provider quotas are available

Retry options:

- Admin Console “Retry Job”
- Re-trigger via API
- Reset job state (only if documented and safe)

Transcription must be idempotent.

---

## 🧼 Step 6 — Clean Up Partial Results

If the transcript file is corrupted or incomplete:

1. Remove broken transcript artifact
2. Reset job status
3. Retry transcription

Never overwrite a valid transcript without verification.

---

## ⚠️ Common Failure Causes

| Issue | Cause |
|------|------|
| Long audio timeout | Provider limit reached |
| API rate limit | Too many concurrent jobs |
| Unsupported language | Model limitation |
| Memory errors | Local resource limits |

---

## 🛑 When to Escalate

Escalate if:

- Multiple jobs fail across different videos
- ASR provider outage suspected
- Worker repeatedly crashes
- Corrupted transcripts appear systemic

Follow:
- `docs/runbooks/incident.md`

---

## 📚 Related Docs

- Pipeline overview → `docs/architecture/pipelines.md`
- Contracts → `packages/contracts`
- Incident response → `docs/runbooks/incident.md`

