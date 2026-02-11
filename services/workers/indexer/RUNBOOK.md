# Indexer Worker Runbook — Narralytica

This runbook explains how to **operate, debug, and rerun** indexing jobs safely.

Use it when search results are missing, outdated, or inconsistent.

---

## 🎯 When to Use This Runbook

Use this guide if:

- A search query returns no results for known data
- Segments exist in DB but not in search
- Embeddings are missing in the vector store
- An indexing job failed or is stuck
- A full or partial reindex is required

---

## 🔍 Step 1 — Identify the Job

Find the job via:

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
| OpenSearch connection error | Cluster unavailable or credentials invalid |
| Qdrant timeout | Vector DB overloaded or unreachable |
| Mapping conflict | Schema mismatch |
| Bulk index failure | Batch too large or malformed document |

Logs should clearly indicate whether failure occurred in lexical or vector indexing.

---

## 📦 Step 3 — Verify Inputs

Confirm that enrichment completed:

| Input Artifact | Expected? |
|----------------|-----------|
| Segments exist in DB | Yes |
| Layer data exists | Yes |
| Embeddings exist | Yes |

If embeddings are missing, the issue is upstream (enrich worker).

---

## 📊 Step 4 — Verify Search Systems

### OpenSearch
- Check document count for the index
- Search for the `video_id` manually
- Verify index health

### Qdrant
- Check collection exists
- Confirm vector count increased
- Query by ID if supported

If data exists in one system but not the other, indexing was partially successful.

---

## 🔁 Step 5 — Retry the Job

Before retrying:

- Confirm partial documents can be safely overwritten
- Ensure index mappings are correct

Retry methods:

- Admin Console “Retry Job”
- CLI reindex command
- Orchestrator-triggered rerun

Indexing must be idempotent.

---

## 🧼 Step 6 — Reindex Strategy

If many documents are missing or mappings changed:

1. Pause indexing jobs
2. Recreate index or collection (if required)
3. Run bulk reindex
4. Resume normal indexing

This should be done during low-traffic windows.

---

## ⚠️ Common Failure Causes

| Issue | Cause |
|------|------|
| Zero results | Index not updated |
| Partial results | Only lexical or vector index updated |
| Query errors | Mapping mismatch |
| Slow indexing | Batch size too large |

---

## 🛑 When to Escalate

Escalate if:

- OpenSearch cluster is red/unhealthy
- Qdrant becomes unreachable
- Reindex repeatedly fails
- Data corruption suspected

Follow:
- `docs/runbooks/incident.md`

---

## 📚 Related Docs

- Search architecture → `docs/architecture/search.md`
- Search config → `packages/search`
- Incident response → `docs/runbooks/incident.md`
