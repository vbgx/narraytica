# Contracts — Narralytica

This package defines the **canonical contracts** used across the Narralytica platform.

Contracts ensure that all services, workers, and external consumers share a **consistent understanding of data structures and APIs**.

They are the backbone of interoperability.

---

## 🎯 Purpose

This package exists to:

- Define API schemas (OpenAPI)
- Define canonical JSON schemas for core entities
- Ensure data compatibility across services
- Prevent drift between producers and consumers

If two components exchange structured data, the contract must live here.

---

## 📦 What’s Inside

| File / Folder | Purpose |
|--------------|---------|
| `openapi.yaml` | Main API contract |
| `schemas/` | JSON Schemas for platform entities |
| `conventions.md` | Naming and API design rules |
| `changelog.md` | Version history of contract changes |

---

## 🧱 Core Entities Covered

Contracts exist for:

- Videos
- Transcripts
- Segments
- Speakers
- AI enrichment layers
- Search requests and responses

These represent the **platform’s shared language**.

---

## 🔄 Versioning Rules

When changing a contract:

1. Update the relevant schema or OpenAPI spec  
2. Add an entry to `changelog.md`  
3. Ensure all affected services are updated  
4. Maintain backward compatibility when possible  

Breaking changes must be clearly documented.

---

## 🚫 What Does NOT Belong Here

- Database migration SQL
- Internal service DTOs
- Worker-specific payload formats
- Operational runbooks

This package defines **external and cross-service contracts only**.

---

## 🔗 Relationship with Code

All services should:

- Validate inputs and outputs against these schemas
- Generate client/server types when possible
- Treat these contracts as the single source of truth

---

## 📚 Related Documentation

- API architecture → `docs/architecture/api.md`
- System specifications → `docs/specs/`
- Delivery planning → `/epics`
