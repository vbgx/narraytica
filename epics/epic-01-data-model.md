# EPIC 01 — Core Data Model

## 🎯 Goal

Define and implement the **canonical data model** that represents spoken video as structured, queryable data across Narralytica.

This EPIC establishes the entities and relationships that all pipelines, search systems, and applications depend on.

---

## 📦 Scope

This EPIC includes:

- Canonical entities for video intelligence
- Database schema design (Postgres)
- JSON schemas and OpenAPI contracts
- Storage references for large artifacts (media, transcripts)
- Versioning strategy for AI layers
- ID conventions across the platform

---

## 🚫 Non-Goals

This EPIC does **not** include:

- Media ingestion logic  
- Transcription implementation  
- AI enrichment logic  
- Search indexing  

It defines **structure**, not processing.

---

## 🧱 Core Entities

| Entity | Description |
|--------|-------------|
| **Video** | A single video source and its metadata |
| **Transcript** | Full timecoded text for a video |
| **Segment** | Time-bounded unit of speech |
| **Speaker** | A speaker identity within or across videos |
| **Layer** | AI-generated analytical data attached to segments |
| **Job** | Processing job tracking across pipelines |

---

## 🗂 Deliverables

- Postgres schema for all core entities  
- Migrations for tables and indexes  
- JSON Schemas in `packages/contracts/schemas/`  
- OpenAPI definitions referencing core models  
- ER diagram in documentation  
- ID and foreign key conventions documented  

---

## 🗂 Issues

1. Define canonical entity list and relationships  
2. Design Video table schema  
3. Design Transcript table schema  
4. Design Segment table schema  
5. Design Speaker table schema  
6. Design Layer table schema  
7. Design Job tracking schema  
8. Define object storage reference strategy  
9. Implement DB migrations for all tables  
10. Write JSON schemas for each entity  
11. Update OpenAPI contracts  
12. Document ER model in `docs/architecture/data-model.md`  

---

## ✅ Definition of Done

EPIC 01 is complete when:

- All core entities exist in Postgres  
- Migrations run cleanly from an empty database  
- Schemas are reflected in JSON contracts  
- OpenAPI references canonical types  
- Relationships between entities are enforced  
- Documentation clearly describes the model  
- No pipeline code uses ad-hoc or undefined structures  

---

## ⚠️ Risks / Mitigations

| Risk | Mitigation |
|------|------------|
| Overly rigid schema | Use extensible Layer model for AI outputs |
| Future feature mismatch | Keep entity design modular |
| Inconsistent IDs across services | Centralize ID generation in `packages/shared/ids` |
| Schema drift between code and contracts | Use schema-first approach and CI validation |

---

## 🔗 Links

- Data model documentation → `docs/architecture/data-model.md`  
- Contracts → `packages/contracts/`  
- Database layer → `packages/db/`  
- Shared IDs → `packages/shared/ids/`
