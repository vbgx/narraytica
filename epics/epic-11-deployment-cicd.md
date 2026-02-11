# EPIC 11 — Deployment & CI/CD

## 🎯 Goal

Establish a reliable and repeatable system to **build, deploy, and operate Narralytica environments** across local, staging, and production.

This EPIC ensures the platform can move from development to real-world usage safely.

---

## 📦 Scope

This EPIC includes:

- CI pipelines for build, test, and lint  
- Docker image builds for services and workers  
- Automated database migrations  
- Environment configuration management  
- Deployment workflows for staging and production  
- Release and versioning strategy  

---

## 🚫 Non-Goals

This EPIC does **not** include:

- Blue/green or canary deployments  
- Auto-scaling infrastructure  
- Multi-region failover  

It focuses on **stable, controlled deployment pipelines**.

---

## 🧱 Deployment Layers

| Layer | Role |
|------|------|
| CI (GitHub Actions) | Validate code and build artifacts |
| Docker | Containerized services and workers |
| Infrastructure | Provisioning via Terraform |
| Orchestration | Kubernetes or managed container runtime |
| Migrations | Database schema management |

---

## 🗂 Deliverables

- CI workflows for tests and linting  
- Dockerfiles for all services and workers  
- Automated image publishing  
- Migration workflow integrated into deployments  
- Environment variable and secret management  
- Staging and production deployment scripts  
- Release tagging and versioning process  

---

## 🗂 Issues

1. Create CI workflow for tests and lint  
2. Create CI workflow for Docker builds  
3. Implement container registry publishing  
4. Add migration step to deployment pipeline  
5. Define environment variable strategy  
6. Implement staging deployment workflow  
7. Implement production deployment workflow  
8. Add rollback procedure  
9. Add version tagging strategy  
10. Document deployment architecture  
11. Create runbook for failed deployments  
12. Validate full deployment cycle end-to-end  

---

## ✅ Definition of Done

EPIC 11 is complete when:

- Code merges trigger automated CI checks  
- Docker images are built and versioned  
- Deployments to staging are automated  
- Production deployments follow documented workflow  
- Database migrations run safely  
- Rollback procedure is documented and tested  

---

## ⚠️ Risks / Mitigations

| Risk | Mitigation |
|------|------------|
| Broken deployments | Enforce CI before deploy |
| Schema mismatches | Run migrations as part of deploy |
| Secret leakage | Use environment secret management |
| Hard-to-debug failures | Add detailed deployment logs |

---

## 🔗 Links

- Infrastructure → `infra/`  
- Deployments → `deployments/`  
- CI workflows → `.github/workflows/`  
- Runbooks → `docs/runbooks/deploy.md`
