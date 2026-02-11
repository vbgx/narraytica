# Observability — Narralytica

This package defines the **observability standards and assets** for the Narralytica platform.

Observability ensures the system is **measurable, debuggable, and reliable** in production.

It covers:
- Logging
- Metrics
- Tracing
- Dashboards
- Alerts

---

## 🎯 Purpose

Observability exists to help the team:

- Detect failures quickly
- Understand system behavior under load
- Investigate incidents
- Monitor performance and cost drivers
- Validate that pipelines and search infrastructure are healthy

Without observability, Narralytica cannot be safely operated at scale.

---

## 📦 What’s Inside

| Folder | Purpose |
|--------|---------|
| `logging/` | Log format and logging conventions |
| `dashboards/` | Grafana dashboard definitions |
| `alerts/` | Prometheus alerting rules |
| `otel/` | OpenTelemetry configuration |
| `README.md` | Overview and standards (this file) |

---

## 🧱 Observability Pillars

### 🪵 Logging
Structured logs from:
- API
- Workers
- Orchestrator

Logs must:
- Be machine-parseable (JSON)
- Include request IDs / job IDs
- Avoid sensitive data

---

### 📊 Metrics
Metrics track system health and performance, such as:

- API request rate and latency
- Job processing time
- Queue backlogs
- Search query latency
- Index size and growth

Metrics are used for dashboards and alerts.

---

### 🧭 Tracing
Distributed tracing helps follow a request or job across:

- API
- Workers
- External services

Tracing is especially useful for:
- Debugging slow pipelines
- Identifying bottlenecks
- Understanding cross-service dependencies

---

## 🚨 Alerts

Alerts should focus on:

- System outages
- Processing failures
- Growing backlogs
- Resource saturation
- Error rate spikes

Alerts must be actionable and linked to a runbook.

---

## 🔁 Operational Flow

When an issue occurs:

1. Alert triggers
2. Dashboards provide context
3. Logs and traces are inspected
4. Runbook is followed
5. Incident is resolved and documented

Observability tools support every step.

---

## 🔐 Data Sensitivity

Observability data must:

- Avoid storing PII or sensitive transcript data
- Redact tokens and secrets
- Follow data retention policies

---

## 📚 Related Documentation

- Incident response → `docs/runbooks/incident.md`
- Cost monitoring → `docs/runbooks/cost-control.md`
- Architecture overview → `docs/architecture/overview.md`
