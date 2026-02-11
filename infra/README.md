# Infrastructure — Narralytica

This folder contains the infrastructure configuration required to run Narralytica across environments.

It defines **how the platform is deployed and operated**, not the application logic itself.

---

## 🎯 Purpose

Infrastructure code exists to:

- Provision and configure cloud resources
- Define containerized services
- Manage networking and security boundaries
- Support CI/CD and automated deployments

This folder represents the **operational backbone** of the platform.

---

## 🧱 Infrastructure Areas

| Folder | Purpose |
|--------|---------|
| `docker/` | Local and containerized service definitions |
| `terraform/` | Infrastructure as Code for cloud environments |
| `kubernetes/` | K8s manifests (if using Kubernetes) |
| `helm/` | Helm charts for templated K8s deployments |
| `ci/` | CI/CD workflows and deployment scripts |

---

## 🐳 Docker

The `docker/` directory contains service-level Docker configurations used for:

- Local development
- Testing environments
- Building service images

Services typically include:
- Postgres
- OpenSearch
- Qdrant
- MinIO
- Redis
- Monitoring tools (Grafana, Prometheus)

---

## ☁️ Terraform

The `terraform/` directory defines cloud infrastructure such as:

- Databases
- Object storage
- Networking (VPCs, subnets)
- Load balancers
- Managed search clusters

Terraform ensures infrastructure is:
- Reproducible
- Versioned
- Auditable

---

## ☸️ Kubernetes & Helm

If the platform is deployed to Kubernetes:

- `kubernetes/` contains raw manifests
- `helm/` contains parameterized charts

These enable:
- Scalable deployments
- Rolling updates
- Environment-specific configuration

---

## 🔁 CI/CD

The `ci/` directory contains:

- GitHub workflows
- Build and test pipelines
- Deployment scripts
- Migration and smoke-test automation

CI/CD ensures changes move safely from: ```Development → Staging → Production```

---

## 🔐 Security Principles

Infrastructure must follow:

- Least privilege access
- Encrypted storage and network traffic
- Secrets managed outside the repo
- Isolated staging and production environments

---

## 📚 Related Documentation

- Deployment procedures → `docs/runbooks/deploy.md`
- Incident response → `docs/runbooks/incident.md`
- Environment structure → `deployments/`

