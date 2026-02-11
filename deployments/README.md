# Deployments — Narralytica Environments

This directory contains configuration and environment-specific settings used to deploy Narralytica across different stages of its lifecycle.

Narralytica is designed to run consistently across **local, staging, and production** environments, with differences isolated in this folder.

---

## 🌍 Environments

### 🧪 `local/`
Used for development and testing on a developer’s machine.

Typical characteristics:
- Runs via `docker-compose`
- Uses local object storage (MinIO)
- Uses local Postgres, Qdrant, OpenSearch
- Lower resource limits
- No external integrations required

See: `docs/runbooks/local-dev.md`

---

### 🧩 `staging/`
Pre-production environment for validation before release.

Typical characteristics:
- Mirrors production architecture
- Uses real cloud services (managed DB, storage, etc.)
- Used for integration testing and QA
- Safe place to test migrations, reindexing, and pipeline changes

Staging should always be:
- Deployable from the main branch
- Stable enough to demo
- Used to validate performance and cost assumptions

---

### 🚀 `production/`
Live environment serving real users and applications.

Typical characteristics:
- Managed infrastructure (cloud DB, storage, search clusters)
- Full monitoring and alerting enabled
- Strict access control
- Backups and disaster recovery enabled

Production changes must:
- Go through staging first
- Follow migration and rollback procedures
- Be documented in runbooks

---

## 🔁 Deployment Flow

Typical flow: ```local → staging → production````


1. Develop and test locally  
2. Deploy to staging  
3. Validate pipelines, search, and API  
4. Promote to production  

---

## 📦 What Lives Here

Each environment folder may contain:

- Environment-specific `.env` files or templates
- Docker Compose overrides (local)
- Helm values files (Kubernetes)
- Terraform variable files
- Secrets references (never actual secrets)

---

## 🔐 Secrets & Configuration

Sensitive values **must never be committed**.

Use:
- Secret managers (cloud provider)
- `.env.example` as documentation
- CI/CD environment variables

---

## 🛠 Related Documentation

- Deployment procedures → `docs/runbooks/deploy.md`
- Incident handling → `docs/runbooks/incident.md`
- Cost management → `docs/runbooks/cost-control.md`


