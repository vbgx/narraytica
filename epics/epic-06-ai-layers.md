# EPIC 06 — AI Enrichment Layers

## 🎯 Goal

Implement the AI-powered enrichment pipeline that transforms raw transcript segments into **structured analytical intelligence**.

This EPIC adds the semantic layers that make Narralytica more than a transcription system.

---

## 📦 Scope

This EPIC includes the first version of the following segment-level layers:

- Embeddings (semantic vectors)
- Summaries
- Topic detection
- Sentiment analysis
- Stance detection (for/against/neutral where applicable)
- CEFR language level classification

Each layer must be stored in a structured, versionable format.

---

## 🚫 Non-Goals

This EPIC does **not** include:

- Trend aggregation across time  
- Advanced multi-modal analysis  
- LLM-based reranking for search  
- Cross-video speaker identity resolution  

It focuses on **segment-level intelligence**.

---

## 🧱 Layer Architecture

Each segment may have multiple **layers**, each:

- Independently computed  
- Versioned  
- Stored in a structured schema  
- Usable for filtering and ranking  

Layers must not overwrite core transcript data.

---

## 🗂 Deliverables

- Enrich worker implementation  
- Embedding model integration  
- LLM or classifier integration for summaries and topics  
- Sentiment and stance detection pipeline  
- CEFR estimation model  
- Storage schema for layers  
- Versioning mechanism for model outputs  

---

## 🗂 Issues

1. Design layer storage schema  
2. Implement enrich worker job orchestration  
3. Integrate embedding model  
4. Store vectors in vector DB  
5. Implement summary generation  
6. Implement topic classification  
7. Implement sentiment detection  
8. Implement stance detection  
9. Implement CEFR level detection  
10. Add model configuration and versioning  
11. Add logging and monitoring for model calls  
12. Write integration tests for enrichment flow  

---

## ✅ Definition of Done

EPIC 06 is complete when:

- Each segment receives embeddings  
- Each segment has at least one topic label  
- Sentiment is stored for segments  
- Stance is stored where relevant  
- CEFR level is assigned  
- All outputs are versioned  
- Enrichment jobs can be retried safely  
- Layers are usable in search filters  

---

## ⚠️ Risks / Mitigations

| Risk | Mitigation |
|------|------------|
| Model drift | Version layer outputs |
| High inference costs | Batch processing and caching |
| Low quality topics | Allow model iteration |
| Inconsistent outputs | Validate schema and ranges |

---

## 🔗 Links

- Layer schema → `packages/contracts/schemas/layer.schema.json`  
- Enrich worker → `services/workers/enrich/README.md`  
- Pipelines overview → `docs/architecture/pipelines.md`
