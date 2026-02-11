# EPIC 04 — Search V1 (Minimal)

## 🎯 Goal

Deliver the first working version of Narralytica’s **search engine**, allowing users and applications to find relevant video segments using both keyword and semantic search.

This EPIC establishes the foundation of **retrieval over spoken content**.

---

## 📦 Scope

This EPIC includes:

- Lexical search via OpenSearch
- Vector search via Qdrant
- Basic hybrid search (lexical + semantic)
- Segment-level search results
- Filtering by metadata (language, date, source)
- API endpoint for search queries

---

## 🚫 Non-Goals

This EPIC does **not** include:

- Advanced ranking models
- Reranking with LLMs
- Cross-lingual semantic alignment
- Complex faceting or aggregations

It focuses on a **reliable, minimal retrieval layer**.

---

## 🧱 Search Architecture (V1)

| Layer | Role |
|------|------|
| OpenSearch | Keyword and metadata filtering |
| Qdrant | Semantic vector similarity |
| API Search Layer | Combines and returns ranked results |

---

## 🗂 Deliverables

- OpenSearch index mappings for segments
- Qdrant collection setup for embeddings
- Indexer worker able to push documents and vectors
- `/search` API endpoint
- Query model supporting text + filters
- Result format including segment, video, speaker, and timestamps

---

## 🗂 Issues

1. Design segment search document structure
2. Create OpenSearch index template
3. Create Qdrant collection schema
4. Extend indexer worker to support search indexing
5. Implement lexical search query builder
6. Implement vector search query logic
7. Combine lexical and vector results (basic merge)
8. Add metadata filters (language, date, source)
9. Implement `/search` API endpoint
10. Define search response schema
11. Add logging and query telemetry
12. Write integration tests for search queries

---

## ✅ Definition of Done

EPIC 04 is complete when:

- Segments are searchable via keywords
- Semantic search returns relevant segments
- Results include correct timestamps and metadata
- Filters narrow results correctly
- Search API is stable and documented
- Indexing and search run reliably at small scale

---

## ⚠️ Risks / Mitigations

| Risk | Mitigation |
|------|------------|
| Poor initial relevance | Combine lexical + semantic signals |
| Index mapping mistakes | Version index templates |
| Large result latency | Limit results and paginate |
| Vector DB scaling issues | Start with minimal collections and tune later |

---

## 🔗 Links

- Search architecture → `docs/architecture/search.md`
- Indexer worker → `services/workers/indexer/README.md`
- Search contracts → `packages/contracts/schemas/search.schema.json`
- Pipelines overview → `docs/architecture/pipelines.md`
