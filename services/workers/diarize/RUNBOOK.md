# Diarize Worker Runbook — Narralytica

This runbook describes how to **operate, debug, and rerun** the diarization pipeline safely.

Use it when speaker detection or clustering fails, stalls, or produces incorrect results.

---

## 🎯 When to Use This Runbook

Use this guide if:

- A diarization job is stuck in `running`
- Speaker segments are missing
- All speech is assigned to a single speaker incorrectly
- Too many speakers are detected
- A backfill requires re-diarizing videos

---

## 🔍 Step 1 — Identify the Job

Locate the job via:

- Admin Console
- API `/jobs` endpoint
- Logs or alerts

Record:
- `job_id`
- `video_id`
- Transcript reference

---

## 🪵 Step 2 — Inspect Logs

Look for:

| Error Type | Possible Cause |
|-----------|----------------|
| Model load failure | Missing model files or GPU issues |
| Memory errors | Long audio or resource limits |
| Alignment mismatch | Transcript timestamps inconsistent |
| Empty diarization output | Audio quality or silence detection issues |

Logs should include job and video IDs for tracing.

---

## 📦 Step 3 — Verify Inputs

Confirm that:

| Input Artifact | Expected? |
|----------------|-----------|
| Transcript exists | Yes |
| Transcript has valid timestamps | Yes |
| Audio file accessible | Yes |

If timestamps are invalid, diarization will fail downstream.

---

## 🧾 Step 4 — Verify Outputs

Check:

| Artifact | Expected? |
|----------|-----------|
| Speaker segments in DB | Yes |
| Multiple speakers detected (if applicable) | Yes |
| Job marked completed | Yes |

If output exists but is clearly wrong (e.g., one speaker for a panel discussion), model thresholds may need tuning.

---

## 🔁 Step 5 — Retry the Job

Before retrying:

- Confirm transcript and audio are valid
- Ensure previous partial speaker records can be safely replaced

Retry via:
- Admin Console
- API-triggered rerun
- Orchestrator reset (only if documented)

Diarization must be idempotent.

---

## 🧼 Step 6 — Clean Up Incorrect Results

If diarization output is corrupted or invalid:

1. Remove incorrect speaker segments from DB
2. Reset job state
3. Re-run diarization

Never delete downstream enriched data without confirming dependencies.

---

## ⚠️ Common Failure Causes

| Issue | Cause |
|------|------|
| All speech = one speaker | Low audio quality or model threshold |
| Too many speakers | Over-segmentation or noise |
| Memory crash | Very long audio |
| Timestamp drift | Transcript misalignment |

---

## 🛑 When to Escalate

Escalate if:

- Multiple jobs fail in similar ways
- Model produces consistently incorrect clustering
- Worker crashes repeatedly
- GPU resources unavailable

Follow incident procedures in:

- 'docs/runbooks/incident.md'

---

## 📚 Related Docs

- Pipelines → `docs/architecture/pipelines.md`
- Speaker model → `docs/architecture/data-model.md`
- Incident response → `docs/runbooks/incident.md`

---
