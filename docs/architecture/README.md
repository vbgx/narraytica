# Architecture — Narralytica

This section describes the **technical architecture** of the Narralytica platform.

Narralytica is a distributed system that ingests video, processes speech, enriches it with AI, and exposes the resulting intelligence through search and APIs.

The documents here explain **how the system is structured and why**.

---

## 🧱 Architectural Principles

Narralytica follows a few core principles:

### 1️⃣ Separation of Concerns
- Ingestion, processing, indexing, and serving are separate layers
- Workers perform heavy processing
- The API layer is read/write orchestration, not compute-heavy

### 2️⃣ Data is the Source of Truth
- Postgres stores canonical structured data
- Object storage stores large artifacts (audio, transcripts, embeddings)
- Search indexes are **derived views**, not primary storage

### 3️⃣ Pipelines are Idempotent
All processing steps must be safely re-runnable:
- Re-transcription
- Re-enrichment
- Re-indexing

This is essential for backfills and model improvements.

### 4️⃣ Apps Depend on the API, Not Internals
End-user apps and internal tools (Admin Console) must use the API, not direct database access.

---

## 📦 What You’ll Find in This Folder

| File | Purpose |
|------|---------|
| `overview.md` | System-wide architecture diagram and component map |
| `data-model.md` | Canonical entities and relationships |
| `pipelines.md` | Step-by-step processing flows |
| `search.md` | Vector, lexical, and hybrid search design |
| `api.md` | API architecture and layering |
| `multi-tenancy.md` | Future design for tenant isolation |

---

## 🔄 System Layers (High-Level)

1. **Storage Layer**
   - Postgres (structured data)
   - Object storage (media & artifacts)

2. **Processing Layer**
   - Ingestion workers
   - Transcription workers
   - Enrichment workers
   - Indexing workers

3. **Search Layer**
   - Qdrant (semantic vectors)
   - OpenSearch (lexical index)
   - Hybrid retrieval and reranking

4. **API Layer**
   - Exposes data and search
   - Manages authentication and rate limits
   - Triggers processing jobs

5. **Client Layer**
   - End-user apps
   - Admin Console
   - External API consumers

---

## 🧠 How to Read These Docs

If you are:

- **New to the system** → start with `overview.md`
- **Working on data schemas** → read `data-model.md`
- **Building or modifying pipelines** → read `pipelines.md`
- **Working on search** → read `search.md`
- **Working on the API** → read `api.md`

---

## 🔗 Related Documentation

- Operational procedures → `docs/runbooks/`
- System specifications → `docs/specs/`
- Architecture decisions → `docs/adr/`
- Planning & delivery → `/epics`
