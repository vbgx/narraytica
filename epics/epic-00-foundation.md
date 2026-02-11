# EPIC 00 — Foundation & Platform Setup

## 🎯 Goal

Establish the technical and organizational foundation required to build Narralytica in a scalable, maintainable, and production-ready way.

This EPIC focuses on infrastructure, repository structure, development workflow, and core platform conventions — not on feature development.

---

## 📦 Scope

This EPIC includes:

- Final repository structure
- Local development environment
- Core infrastructure services (DB, search, storage, queue)
- CI/CD baseline
- Coding and documentation standards
- Observability foundations
- Security baseline for internal services

---

## 🚫 Non-Goals

This EPIC does **not** include:

- Video ingestion
- Transcription
- AI enrichment
- Search implementation
- End-user applications

Those belong to later EPICs.

---

## 🧱 Deliverables

- Working local environment via Docker Compose
- Base infrastructure services reachable from local dev
- API service skeleton running
- Worker service skeletons bootstrapped
- Database initialized with base schema
- Search clusters running (OpenSearch + Qdrant)
- Object storage available (MinIO/S3)
- Basic CI pipeline (lint, tests, build)
- Core documentation structure in place

---

## 🗂 Issues

1. Initialize monorepo structure  
2. Configure Python and Node workspace tooling  
3. Create Docker Compose stack (Postgres, OpenSearch, Qdrant, MinIO, Redis)  
4. Bootstrap API service skeleton  
5. Bootstrap worker service templates  
6. Set up database migration system  
7. Configure OpenSearch index templates  
8. Configure Qdrant collections  
9. Implement shared logging and telemetry baseline  
10. Add basic healthcheck endpoints  
11. Set up GitHub Actions CI (lint + tests)  
12. Add pre-commit hooks and code style tooling  

---

## ✅ Definition of Done

EPIC 00 is complete when:

- `docker-compose up` starts all core services
- API service runs locally and responds to health checks
- Workers can start and connect to infra services
- Database migrations run successfully
- Search and vector DBs are reachable
- CI runs automatically on PRs
- All services follow shared logging and config patterns
- Documentation for local setup exists and is usable

---

## ⚠️ Risks / Mitigations

| Risk | Mitigation |
|------|------------|
| Overengineering infra too early | Keep configs minimal and evolvable |
| Tooling fragmentation | Standardize on shared tooling early |
| Hidden local/prod differences | Use environment parity via containers |
| Slow onboarding | Provide clear runbooks and README files |

---

## 🔗 Links

- Architecture overview → `docs/architecture/overview.md`  
- Local dev runbook → `docs/runbooks/local-dev.md`  
- Infra definitions → `infra/`  
- API skeleton → `services/api/`  
- Worker templates → `services/workers/`
