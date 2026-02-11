# EPIC 09 — Observability & Operations

## 🎯 Goal

Establish full operational visibility and reliability for Narralytica by implementing **monitoring, logging, tracing, and operational tooling**.

This EPIC ensures the platform can be **operated safely in production**.

---

## 📦 Scope

This EPIC includes:

- Centralized logging across services and workers
- Metrics collection (pipeline, API, search, AI usage)
- Distributed tracing for pipeline flows
- Health checks and readiness probes
- Alerts for failures and performance issues
- Operational runbooks for common incidents

---

## 🚫 Non-Goals

This EPIC does **not** include:

- Cost optimization automation
- Full business analytics dashboards
- End-user usage analytics

It focuses on **system health and operability**.

---

## 🧱 Observability Stack

| Component | Role |
|-----------|------|
| OpenTelemetry | Traces and metrics instrumentation |
| Prometheus | Metrics collection |
| Grafana | Dashboards and visualization |
| Centralized logs | Structured logs across services |
| Alerts | Automated incident detection |

---

## 🗂 Deliverables

- Logging conventions implemented across services
- Metrics emitted for jobs, API calls, and search
- Tracing integrated into pipelines
- Grafana dashboards for system health
- Alert rules for failure scenarios
- Health endpoints for all services
- Operational runbooks updated

---

## 🗂 Issues

1. Define logging format and standards
2. Integrate OpenTelemetry in API
3. Integrate OpenTelemetry in workers
4. Expose Prometheus metrics endpoints
5. Build Grafana dashboards
6. Add alert rules for job failures
7. Add alert rules for search latency
8. Add alert rules for API error rates
9. Implement health and readiness endpoints
10. Add tracing for pipeline job lifecycle
11. Write operational runbooks
12. Test alert triggering and recovery

---

## ✅ Definition of Done

EPIC 09 is complete when:

- Logs are structured and centralized
- Key system metrics are visible in dashboards
- Traces show end-to-end pipeline flows
- Alerts trigger on failures and anomalies
- Operators can diagnose issues using dashboards and logs
- Runbooks exist for top operational scenarios

---

## ⚠️ Risks / Mitigations

| Risk | Mitigation |
|------|------------|
| Too much noisy logging | Define log levels and sampling |
| Missing critical metrics | Start from pipeline SLOs |
| Alert fatigue | Tune thresholds and use severity levels |
| Complex tracing setup | Start with minimal spans |

---

## 🔗 Links

- Observability package → `packages/observability/`
- Runbooks → `docs/runbooks/`
- Architecture overview → `docs/architecture/overview.md`
