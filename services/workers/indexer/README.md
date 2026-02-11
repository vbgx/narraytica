# Indexer Worker — Narralytica

The Indexer worker is responsible for **making enriched data searchable**.

It takes structured segments and AI layers and pushes them into:

- OpenSearch (lexical search)
- Qdrant (vector search)

This worker powers the **unified search experience** of Narralytica.

---

## 🎯 Purpose

The indexer worker handles:

- Preparing search documents from segments and layers
- Indexing lexical data into OpenSearch
- Indexing embeddings into Qdrant
- Updating or reindexing data when changes occur

It bridges the gap between **data storage** and **search infrastructure**.

---

## 📥 Inputs

The worker receives jobs containing:

- `video_id`
- Segments with speaker and metadata
- Enrichment layers (topics, sentiment, stance, CEFR)
- Embedding vectors
- Job identifiers

Jobs are triggered after enrichment is complete.

---

## 📤 Outputs

After successful processing, the worker produces:

| Artifact | System | Description |
|---------|--------|-------------|
| Search documents | OpenSearch | Textual index for keyword search |
| Vector points | Qdrant | Embeddings for semantic search |
| Job status update | Database | Marks indexing as completed |

---

## 🧱 Responsibilities

| Task | Description |
|------|-------------|
| Document construction | Build search-ready records |
| Lexical indexing | Push documents to OpenSearch |
| Vector indexing | Push embeddings to Qdrant |
| Upserts | Update existing records safely |
| Status tracking | Update indexing state |

---

## ⚙️ Performance Considerations

- Bulk indexing should be batched
- Vector insertions must handle large volumes efficiently
- Index updates must avoid downtime
- Reindex operations should be throttled

---

## 🔄 Idempotency

If indexing runs multiple times:

- Documents must be upserted, not duplicated
- Vector points must overwrite or version safely
- Index state must remain consistent

---

## 🚫 Out of Scope

The indexer worker does **not**:

- Generate embeddings
- Perform AI analysis
- Fetch raw media
- Serve search requests

It only populates search systems.

---

## 🛠 Runbook

Operational procedures for rerunning or debugging indexing jobs are documented in:

- `services/workers/indexer/RUNBOOK.md`

---

## 📚 Related Documentation

- Search architecture → `docs/architecture/search.md`
- Data model → `docs/architecture/data-model.md`
- Search mappings → `packages/search`
