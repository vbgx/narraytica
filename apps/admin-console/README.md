# Admin Console — Narralytica

The Admin Console is the **internal control panel** for operating the Narralytica platform.

It provides visibility and control over:
- Processing jobs
- System health
- Data backfills
- Reindexing operations
- Cost and usage signals

This tool is intended for **operators, engineers, and analysts**, not end users.

---

## 🎯 Purpose

The Admin Console exists to:

- Monitor ingestion and processing pipelines
- Inspect job states and failures
- Trigger retries and backfills
- Manage indexing and search health
- Provide operational insight into system activity

It is the **human interface to platform operations**.

---

## 🧭 Key Features

| Area | Functionality |
|------|---------------|
| Jobs | View, filter, retry, and inspect pipeline jobs |
| Videos | Inspect ingestion and processing status per video |
| Workers | Monitor worker health and activity |
| Search | Trigger reindex operations and view index stats |
| Costs | Track usage signals (model calls, storage, indexing) |

---

## 🔄 Interaction with Platform

The Admin Console communicates only with the **central API**.

It does not access databases or infrastructure directly.

All actions (retry job, reindex, backfill) are executed via API endpoints and follow the same security and audit rules as external requests.

---

## 🔐 Access Control

The Admin Console is restricted to authorized internal users.

Access should be protected by:
- Strong authentication
- Role-based permissions
- Audit logging

Sensitive operations must be traceable.

---

## ⚙️ Typical Workflows

### Retry a Failed Job
1. Search job by video or job ID  
2. Inspect error details  
3. Trigger retry  

### Reindex a Video
1. Locate video  
2. Confirm enrichment completed  
3. Trigger reindex  

### Investigate a Pipeline Issue
1. Filter jobs by status = failed  
2. Group by worker type  
3. Use logs and runbooks to diagnose  

---

## 🚫 Out of Scope

The Admin Console does **not**:

- Expose end-user search features  
- Provide analytics dashboards (separate products handle this)  
- Run processing logic itself  

It is strictly an **operations interface**.

---

## 📚 Related Documentation

- API service → `services/api/README.md`  
- Worker runbooks → `services/workers/*/RUNBOOK.md`  
- Incident response → `docs/runbooks/incident.md`
