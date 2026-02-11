# EPIC 08 — Advanced Search

## 🎯 Goal

Evolve Narralytica’s search system from basic retrieval into a **rich, structured exploration engine** capable of handling filters, cross-lingual search, and improved ranking.

This EPIC upgrades search from “find segments” to **“explore spoken knowledge.”**

---

## 📦 Scope

This EPIC includes:

- Hybrid search improvements (weighted lexical + semantic)
- Metadata faceting (topics, speakers, sources)
- Cross-lingual semantic search
- Query expansion (synonyms, related concepts)
- Result reranking (lightweight ML or heuristics)
- Highlighting matched terms in transcripts

---

## 🚫 Non-Goals

This EPIC does **not** include:

- LLM-based full generative answers
- Long-form summarization across many videos
- Personalization or user history ranking

It focuses on **structured retrieval and ranking improvements**.

---

## 🧱 Search Enhancements

| Feature | Description |
|--------|-------------|
| Weighted hybrid search | Combine lexical and semantic signals |
| Facets | Filter by topic, speaker, date, language |
| Cross-lingual | Search in one language, retrieve others |
| Query expansion | Broaden user queries intelligently |
| Reranking | Improve result relevance post-retrieval |
| Highlighting | Emphasize matched terms in responses |

---

## 🗂 Deliverables

- Updated search API with advanced filters
- Faceted aggregation support
- Query expansion module
- Cross-lingual embedding alignment
- Basic reranking logic
- Highlight generation in search responses

---

## 🗂 Issues

1. Implement hybrid score weighting strategy
2. Add facet support in OpenSearch
3. Expose filter parameters in API
4. Implement query expansion logic
5. Integrate cross-lingual embeddings
6. Add reranking layer after retrieval
7. Implement text highlighting
8. Optimize search performance
9. Add search analytics and telemetry
10. Write integration tests for advanced queries
11. Update API documentation
12. Document search architecture evolution

---

## ✅ Definition of Done

EPIC 08 is complete when:

- Users can filter search results by multiple attributes
- Cross-lingual search returns meaningful results
- Hybrid ranking improves result relevance
- Highlights appear correctly in transcripts
- Search performance remains acceptable
- Documentation explains advanced search behavior

---

## ⚠️ Risks / Mitigations

| Risk | Mitigation |
|------|------------|
| Ranking complexity | Start with simple weighting |
| Cross-lingual noise | Use high-quality multilingual embeddings |
| Performance degradation | Cache frequent queries |
| Overfitting to test cases | Use diverse evaluation queries |

---

## 🔗 Links

- Search architecture → `docs/architecture/search.md`
- Search contracts → `packages/contracts/schemas/search.schema.json`
- Indexer worker → `services/workers/indexer/README.md`
