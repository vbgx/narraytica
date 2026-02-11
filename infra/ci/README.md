# CI/CD — Narralytica

This folder contains the **Continuous Integration and Continuous Deployment (CI/CD)** configuration for the Narralytica platform.

CI/CD ensures that code changes are **tested, validated, and deployed safely** across environments.

---

## 🎯 Purpose

CI/CD pipelines exist to:

- Automatically test code changes
- Enforce quality and contract checks
- Build and publish service images
- Run database migrations
- Deploy to staging and production
- Perform smoke tests after deployment

CI/CD reduces manual risk and keeps environments consistent.

---

## 🧱 What Lives Here

| Folder | Purpose |
|--------|---------|
| `github/` | GitHub Actions workflows |
| `scripts/` | Supporting scripts for build, migration, and deployment |

---

## 🔄 CI (Continuous Integration)

CI runs on every pull request and main branch update.

Typical checks include:

- Linting and formatting
- Unit tests
- Integration tests (when available)
- Contract validation (OpenAPI / JSON schemas)
- Migration validation

A PR should not be merged unless CI is green.

---

## 🚀 CD (Continuous Deployment)

CD pipelines handle environment deployments:

### Staging
- Triggered on merges to `main`
- Deploys latest version to staging
- Runs smoke tests
- Notifies the team of status

### Production
- Triggered manually or via tagged releases
- Requires passing staging validation
- Applies migrations
- Deploys services
- Runs post-deploy health checks

---

## 🔐 Secrets Handling

Secrets must never be stored in the repository.

CI/CD pipelines should use:

- GitHub encrypted secrets
- Cloud provider secret managers
- Environment-specific credentials

---

## 🧪 Smoke Tests

After deployment, automated smoke tests should verify:

- API health endpoints
- Basic search functionality
- Ingestion job triggering
- Worker connectivity

Smoke tests help detect broken deployments early.

---

## 📚 Related Documentation

- Deployment flow → `deployments/`
- Operational runbooks → `docs/runbooks/deploy.md`
- Testing strategy → `tests/README.md`
