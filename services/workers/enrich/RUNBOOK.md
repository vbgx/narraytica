# Enrich Worker Runbook — Narralytica

This runbook explains how to **operate, debug, and rerun** AI enrichment jobs safely.

Use it when embeddings or analytical layers (topics, sentiment, stance, CEFR, summaries) fail, stall, or look incorrect.

---

## 🎯 When to Use This Runbook

Use this guide if:

- An enrichment job is stuck in `running`
- Embeddings are missing from the vector store
- Topics or sentiment fields are empty or clearly wrong
- A model provider returned errors
- A backfill requires reprocessing layers

---

## 🔍 Step 1 — Identify the Job

Locate the job via:

- Admin Console
- API `/jobs` endpoint
- Logs or alerts

Record:
- `job_id`
- `video_id`
- Number of segments expected

---

## 🪵 Step 2 — Inspect Logs

Check for:

| Error Type | Possible Cause |
|-----------|----------------|
| Model timeout | Provider latency or long batch |
| Rate limit error | Too many concurrent requests |
| Invalid input | Segment text too long or malformed |
| Memory issue | Batch size too large |

Ensure logs include job ID and layer type.

---

## 📦 Step 3 — Verify Inputs

Confirm:

| Input Artifact | Expected? |
|----------------|-----------|
| Segmented transcript exists | Yes |
| Speaker labels exist | Yes |
| Segments have valid timestamps | Yes |

If segments are missing, enrichment cannot proceed.

---

## 📊 Step 4 — Verify Outputs

Check:

| Layer | Where to Check |
|------|----------------|
| Embeddings | Vector DB (Qdrant) |
| Topics | Database layer table |
| Sentiment | Database layer table |
| Stance | Database layer table |
| CEFR | Database layer table |
| Summaries | Database layer table |

If some layers exist and others don’t, the job may have partially failed.

---

## 🔁 Step 5 — Retry the Job

Before retrying:

- Confirm partial layers can be overwritten safely
- Ensure model provider quota is available

Retry methods:

- Admin Console “Retry Job”
- API-triggered rerun
- Orchestrator reset (if documented)

Enrichment must be idempotent.

---

## 🧼 Step 6 — Clean Up Partial or Corrupt Layers

If outputs are corrupted or inconsistent:

1. Remove invalid layer records
2. Delete associated vectors from the vector store (if needed)
3. Reset job status
4. Re-run enrichment

Never delete valid data without confirming dependencies.

---

## ⚠️ Common Failure Causes

| Issue | Cause |
|------|------|
| Missing embeddings | Vector DB connection failure |
| All segments same topic | Model misconfiguration |
| Sentiment always neutral | Provider fallback model |
| CEFR incorrect | Wrong language detection upstream |

---

## 🛑 When to Escalate

Escalate if:

- Multiple jobs fail across different videos
- Vector database becomes unreachable
- Model provider outage suspected
- Worker crashes repeatedly

Follow -> `docs/runbooks/incident.md`

---

## 📚 Related Docs

- Pipelines → `docs/architecture/pipelines.md`
- Layer schema → `packages/contracts/schemas/layer.schema.json`
- Incident response → `docs/runbooks/incident.md`
