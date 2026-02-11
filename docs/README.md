# Documentation — Narralytica

This folder contains all **technical and operational documentation** for the Narralytica platform.

Narralytica is an infrastructure system with multiple services, pipelines, and data flows.  
This documentation ensures the system remains **understandable, operable, and scalable**.

---

## 🧭 Documentation Map

### 🏗 Architecture
📁 `docs/architecture/`

High-level and system design documentation:

- `overview.md` — Global system architecture
- `data-model.md` — Canonical entities (video, transcript, segment, speaker, layers)
- `pipelines.md` — Processing pipelines and data flow
- `search.md` — Lexical, vector, and hybrid search
- `api.md` — API structure and conventions
- `multi-tenancy.md` — Future multi-tenant model

---

### 🛠 Runbooks
📁 `docs/runbooks/`

Operational procedures for maintaining and running the system:

- `local-dev.md` — Local development setup
- `deploy.md` — Deployment procedures
- `backfills.md` — Reprocessing and backfill jobs
- `incident.md` — Incident response guide
- `cost-control.md` — Cost monitoring and reduction strategies

Runbooks are **operational playbooks**, not design documents.

---

### 📜 Specifications
📁 `docs/specs/`

System-wide technical rules and contracts:

- `events.md` — Event bus and job events
- `permissions.md` — Roles and access control
- `rate-limits.md` — API rate limiting strategy

Specs define **how the system must behave**, not how it is implemented internally.

---

### 🧾 ADR — Architecture Decision Records
📁 `docs/adr/`

Architecture Decision Records capture **important technical decisions** and their rationale.

Examples:
- Storage choices
- Search stack decisions
- Orchestration approach

ADRs prevent loss of context as the system evolves.

---

## 📌 How to Use This Documentation

| You want to… | Read this |
|-------------|-----------|
| Understand the system design | `architecture/` |
| Operate or debug the system | `runbooks/` |
| Check platform-wide rules | `specs/` |
| Understand past decisions | `adr/` |

---

## 🧠 Relationship with EPICs

Project planning lives in `/epics`.

Every EPIC should link to relevant documentation:
- Architecture docs for design
- Specs for contracts
- Runbooks for operations
- ADRs for major decisions

Documentation and EPICs must evolve together.

---

## ✍️ Contribution Guidelines

When adding or changing documentation:

- Keep files concise and structured
- Prefer diagrams and tables over long prose
- Link related docs rather than duplicating content
- Update affected runbooks when operational behavior changes
