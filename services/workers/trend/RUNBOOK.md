# Trend Worker Runbook — Narralytica

This runbook explains how to **operate, debug, and rerun** trend aggregation jobs safely.

Use it when analytics dashboards, trend APIs, or reporting datasets appear incorrect, incomplete, or outdated.

---

## 🎯 When to Use This Runbook

Use this guide if:

- Topic or sentiment trends stop updating
- Trend dashboards show gaps in time
- Aggregated counts look inconsistent with segment data
- A scheduled trend job failed
- A historical backfill requires recomputation

---

## 🔍 Step 1 — Identify the Job

Find the job via:

- Admin Console
- API `/jobs` endpoint
- Scheduler logs or alerts

Record:
- `job_id`
- Time range being processed
- Aggregation granularity (daily/weekly/etc.)

---

## 🪵 Step 2 — Inspect Logs

Check worker logs for:

| Error Type | Possible Cause |
|-----------|----------------|
| DB timeout | Large aggregation query |
| Memory error | Dataset too large for batch |
| Missing data | Upstream enrichment incomplete |
| Time bucket mismatch | Timestamp parsing issue |

Ensure logs include job ID and aggregation window.

---

## 📦 Step 3 — Verify Upstream Data

Before blaming the trend worker, confirm:

| Upstream Data | Expected? |
|---------------|-----------|
| Segments exist for time range | Yes |
| Topics layer populated | Yes |
| Sentiment / stance layers present | Yes |

If upstream enrichment is missing, trend results will be incomplete.

---

## 📊 Step 4 — Validate Aggregates

Compare:

- Raw segment counts for a sample period
- Aggregated trend values for the same period

If numbers differ significantly, investigate grouping logic or filters.

---

## 🔁 Step 5 — Retry the Job

Trend jobs are safe to rerun.

Retry via:

- Admin Console
- Scheduler rerun
- CLI backfill command

Confirm that recomputation replaces or updates previous aggregates.

---

## 🧼 Step 6 — Backfill Strategy

For large historical recomputations:

1. Split by time windows (e.g., month-by-month)
2. Run jobs in sequence
3. Monitor DB load
4. Validate partial results before continuing

Avoid full-dataset recomputes during peak system usage.

---

## ⚠️ Common Failure Causes

| Issue | Cause |
|------|------|
| Gaps in charts | Missing time buckets |
| Flat trends | Topics not detected upstream |
| Sudden spikes | Duplicate segment indexing |
| Slow jobs | Large dataset without partitioning |

---

## 🛑 When to Escalate

Escalate if:

- Aggregation queries consistently timeout
- Database performance degrades
- Trend data corruption is suspected
- Multiple trend jobs fail in sequence

Follow:
`docs/runbooks/incident.md`


---

## 📚 Related Docs

- Data model → `docs/architecture/data-model.md`
- Pipelines → `docs/architecture/pipelines.md`
- Incident response → `docs/runbooks/incident.md`
