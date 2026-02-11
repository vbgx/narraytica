# Search — Narralytica Retrieval Layer

This package defines the **search infrastructure contracts and configurations** for Narralytica.

Search in Narralytica is **hybrid by design**:
- Semantic search (vector similarity)
- Lexical search (keyword / full-text)
- Optional reranking

Search indexes are **derived from the primary database**, not a source of truth.

---

## 🎯 Purpose

This package exists to:

- Define how segments are indexed for retrieval
- Configure OpenSearch (lexical search)
- Configure Qdrant (vector search)
- Document hybrid retrieval and reranking strategies

It ensures search behavior is **consistent, reproducible, and tunable**.

---

## 📦 What’s Inside

| Folder / File | Purpose |
|---------------|---------|
| `opensearch/` | Lexical index settings, mappings, analyzers |
| `qdrant/` | Vector collection configuration |
| `reranking.md` | Strategy for reranking hybrid results |
| `README.md` | Overview and contracts (this file) |

---

## 🔎 Search Architecture

Narralytica search works in layers:

### 1️⃣ Vector Search (Semantic)
- Uses embeddings of segments
- Powered by Qdrant
- Captures *meaning*, not exact wording

### 2️⃣ Lexical Search (Keyword)
- Uses OpenSearch
- Captures exact terms, names, and phrases
- Language-specific analyzers improve matching

### 3️⃣ Hybrid Retrieval
- Combines semantic and lexical scores
- Improves recall and precision
- Can be reranked with lightweight models

---

## 🧱 Indexing Philosophy

Search indexes are:

- **Derived data**
- Rebuildable at any time
- Not authoritative

If an index is corrupted or outdated, it should be **reindexed**, not patched.

---

## 🔄 Reindexing

Reindexing may be required when:

- Embedding models change
- Mappings or analyzers change
- Data corrections are applied
- Performance tuning is needed

Operational procedures for reindexing are documented in: ```docs/runbooks/backfills.md```


---

## 🌍 Language Support

OpenSearch analyzers may vary by language.  
Vector search is language-agnostic at the embedding level but still tied to language-specific preprocessing.

---

## 🚫 What Does NOT Belong Here

- API endpoints
- Business logic
- Database schema
- Worker pipeline code

This package defines **search configuration and strategy only**.

---

## 📚 Related Documentation

- Search architecture → `docs/architecture/search.md`
- Data model → `docs/architecture/data-model.md`
- API search endpoints → `services/api`
- Contracts → `packages/contracts`

