# Production Deployment — Narralytica

The **production environment** is the live, user-facing instance of Narralytica.

It powers real applications and must meet strict standards for **stability, security, and performance**.

---

## 🎯 Purpose

Production exists to:

- Serve end-user applications
- Provide reliable API access
- Run ingestion and AI pipelines on real data
- Maintain search indexes and speaker profiles
- Support long-term analytics and trends

Any change here has real-world impact.

---

## 🧱 Environment Characteristics

| Aspect | Production |
|-------|------------|
| Infrastructure | Fully managed cloud services |
| Data | Real user and system data |
| Monitoring | Full observability + alerts |
| Access | Strictly controlled |
| Backups | Automated and verified |
| Recovery | Disaster recovery plan in place |

---

## 🚀 Deployment Policy

Production deployments must:

1. Be validated in **staging**
2. Have passing CI checks
3. Include migration and rollback plans
4. Be documented in relevant runbooks
5. Be announced internally before release

Direct manual changes in production are prohibited.

---

## 🔁 Change Management

Before deploying to production:

- [ ] Migrations tested in staging  
- [ ] API changes reviewed and versioned  
- [ ] Search index updates validated  
- [ ] Pipelines tested with real-scale loads  
- [ ] Observability dashboards reviewed  
- [ ] Rollback plan defined  

---

## 🔐 Security Requirements

Production must enforce:

- Least-privilege access
- Encrypted storage and traffic (TLS)
- Secret management via a secure provider
- API authentication and rate limiting
- Regular dependency updates

Never store secrets in the repository.

---

## 🛠 Operational Responsibilities

The team must ensure:

- Pipelines run within expected cost limits
- Index sizes and performance remain healthy
- Failed jobs are investigated promptly
- Alerts are monitored and acknowledged

The **Admin Console** is the primary operational interface.

---

## 📚 Related Documentation

- Deployment procedures → `docs/runbooks/deploy.md`
- Incident response → `docs/runbooks/incident.md`
- Cost control → `docs/runbooks/cost-control.md`
- Observability → `packages/observability`
