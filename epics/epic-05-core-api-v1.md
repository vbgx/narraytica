# EPIC 05 — Core API V1

## 🎯 Goal

Deliver the first stable version of the **Narralytica public API**, enabling external applications and internal tools to interact with the platform’s core capabilities.

This EPIC defines how clients can:
- Submit videos
- Retrieve structured data
- Search segments
- Inspect processing status

---

## 📦 Scope

This EPIC includes:

- REST API structure and conventions  
- Authentication and API key system  
- Endpoints for videos, transcripts, segments, speakers  
- Search endpoint integration  
- Job status and monitoring endpoints  
- Rate limiting and error handling  

---

## 🚫 Non-Goals

This EPIC does **not** include:

- Advanced analytics endpoints  
- Trend aggregation endpoints  
- Multi-tenant billing features  
- Public SDK refinements  

It focuses on a **functional, stable API surface**.

---

## 🧱 API Domains (V1)

| Domain | Purpose |
|-------|---------|
| Ingest | Submit videos for processing |
| Videos | Retrieve video metadata |
| Transcripts | Access transcript artifacts |
| Segments | Retrieve timecoded speech segments |
| Speakers | Access speaker information |
| Search | Query segments via lexical/semantic search |
| Jobs | Monitor pipeline job status |

---

## 🗂 Deliverables

- OpenAPI specification aligned with contracts  
- API key authentication system  
- Middleware for auth and rate limiting  
- Implemented route handlers for all V1 domains  
- Unified error response model  
- Pagination and filtering conventions  
- API documentation updated  

---

## 🗂 Issues

1. Define API versioning strategy  
2. Implement API key authentication  
3. Add rate limiting middleware  
4. Implement `/ingest` endpoint  
5. Implement `/videos` endpoints  
6. Implement `/transcripts` endpoints  
7. Implement `/segments` endpoints  
8. Implement `/speakers` endpoints  
9. Integrate `/search` endpoint  
10. Implement `/jobs` monitoring endpoints  
11. Standardize error response format  
12. Add OpenAPI docs generation  

---

## ✅ Definition of Done

EPIC 05 is complete when:

- All core endpoints respond correctly  
- Authentication and rate limits work  
- Responses conform to OpenAPI contracts  
- Errors are standardized and documented  
- API is usable by at least one internal app  
- API performance is acceptable at small scale  

---

## ⚠️ Risks / Mitigations

| Risk | Mitigation |
|------|------------|
| API surface instability | Version API early |
| Inconsistent data formats | Enforce schema validation |
| Unauthorized access | Strict API key checks |
| Performance bottlenecks | Add caching later if needed |

---

## 🔗 Links

- API architecture → `docs/architecture/api.md`  
- Contracts → `packages/contracts/openapi.yaml`  
- Permissions spec → `docs/specs/permissions.md`  
- Rate limits → `docs/specs/rate-limits.md`
