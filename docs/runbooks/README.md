# Runbooks — Narralytica Operations

This folder contains **operational runbooks** for running, maintaining, and troubleshooting the Narralytica platform.

Runbooks are **practical, step-by-step guides** for real-world situations.
They are not design documents — they are **action guides**.

---

## 🛠 Purpose of Runbooks

Runbooks help the team:

- Operate the platform safely
- Recover from failures
- Re-run pipelines and backfills
- Deploy changes
- Control infrastructure and AI costs

If something is broken or needs to be rerun, the answer should be in a runbook.

---

## 📚 Available Runbooks

| File | Purpose |
|------|---------|
| `local-dev.md` | Setting up and running the system locally |
| `deploy.md` | Deployment procedures (staging & production) |
| `backfills.md` | Reprocessing and rerunning pipelines |
| `incident.md` | Incident response and escalation process |
| `cost-control.md` | Monitoring and reducing infrastructure/AI costs |

---

## 🔁 When to Update a Runbook

You must update or create a runbook when:

- A new pipeline or worker is added
- A recovery or rerun process changes
- Deployment steps change
- Operational risks are identified
- A production incident reveals missing procedures

Operational knowledge should **never live only in Slack or memory**.

---

## 🧠 Relationship with EPICs

If an EPIC changes operational behavior, its **Definition of Done** must include:

- Updating the relevant runbook(s)
- Adding a new runbook if needed

No EPIC affecting operations is complete without updated runbooks.

---

## ⚠️ Production Safety

Runbooks should always:

- Specify which environment they apply to (local/staging/prod)
- Highlight risky or irreversible actions
- Include rollback or recovery instructions when applicable
