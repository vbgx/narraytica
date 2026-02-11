# Staging Deployment — Narralytica

The **staging environment** is the pre-production instance of Narralytica.

It is used to validate changes in a production-like setup before they are promoted to the live system.

---

## 🎯 Purpose

Staging exists to:

- Test new features end-to-end
- Validate database migrations
- Verify ingestion and AI pipelines at realistic scale
- Test search indexing and performance
- Catch integration issues before production

Staging should behave as closely as possible to production, but with **lower risk**.

---

## 🧱 Environment Characteristics

| Aspect | Staging |
|-------|---------|
| Infrastructure | Cloud-managed services (DB, storage, search) |
| Data | Non-critical, test or mirrored datasets |
| Access | Restricted to internal team |
| Monitoring | Enabled, but with relaxed alert thresholds |
| Scale | Smaller than production but realistic |

---

## 🚀 Deployment Flow

Typical deployment path:

```local → staging → production```


1. Merge changes into `main`
2. CI/CD deploys to staging
3. Team validates:
   - API behavior
   - Pipelines
   - Search results
   - Admin operations
4. If stable, promote to production

---

## 🔁 What to Validate in Staging

Before any production deployment:

- [ ] Migrations run without errors  
- [ ] New ingestion jobs complete successfully  
- [ ] Transcription and enrichment produce expected data  
- [ ] Search results are consistent and relevant  
- [ ] No abnormal resource usage  
- [ ] Admin Console operations behave correctly  

---

## 🔐 Secrets & Access

Staging uses **real infrastructure** and must be treated as sensitive.

- Use staging-specific credentials  
- Never reuse production secrets  
- Restrict admin access to the core team  

---

## 🛠 Operational Notes

Staging is the environment where you should:

- Test backfills and reprocessing
- Trial index rebuilds
- Validate performance assumptions
- Rehearse incident procedures

---

## 📚 Related Documentation

- Deployment process → `docs/runbooks/deploy.md`
- Incident handling → `docs/runbooks/incident.md`
- Cost monitoring → `docs/runbooks/cost-control.md`
