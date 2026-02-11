# CI/CD Scripts — Narralytica

This folder contains helper scripts used by the CI/CD pipelines.

These scripts support automation tasks that are too complex or repetitive to express directly in CI configuration files.

---

## 🎯 Purpose

Scripts in this directory are used to:

- Prepare build environments
- Validate database migrations
- Run smoke tests after deployment
- Bootstrap or verify search indexes
- Execute environment-specific setup steps

They ensure CI/CD workflows remain **modular, readable, and maintainable**.

---

## 🧱 Design Principles

Scripts must be:

- **Idempotent** — safe to run multiple times
- **Environment-aware** — configurable via environment variables
- **Non-interactive** — suitable for automated pipelines
- **Fail-fast** — exit immediately on error

---

## 🔁 Typical Script Categories

| Category | Purpose |
|----------|---------|
| Build scripts | Prepare images or artifacts |
| Migration scripts | Validate and apply DB migrations |
| Deployment helpers | Assist environment provisioning |
| Smoke test scripts | Validate system health post-deploy |

---

## 🔐 Security Considerations

Scripts must never:

- Contain hard-coded secrets
- Log sensitive information
- Assume production credentials by default

All credentials should come from CI environment variables.

---

## 📚 Related Documentation

- CI/CD overview → `infra/ci/README.md`
- Deployment procedures → `docs/runbooks/deploy.md`
- Environment structure → `deployments/`
