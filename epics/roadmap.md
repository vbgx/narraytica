# Roadmap — Narralytica (Execution Order)

This roadmap lists EPICs in the **recommended execution order** to reach a usable V1 quickly
while keeping the architecture scalable.

## Milestones

### V1.0 — “Searchable segments”
- Ingest a video (YouTube / upload)
- Transcribe + segment with timestamps
- Generate embeddings
- Index vectors
- Search via API (semantic search + filters v0)
- Basic ops: job status, logs, rerun

### V1.1 — “Richer understanding”
- Add summaries, topics, sentiment/tone
- Add diarization + speaker clusters (if required)
- Add backfill tooling + cost controls

### V1.2 — “Hybrid retrieval”
- Add lexical index (OpenSearch)
- Hybrid scoring + reranking
- Strong filters + performance hardening

### V1.3 — “Production posture”
- Observability dashboards + alerts
- Load tests
- CI/CD + staging/prod deployment

## EPIC sequence

1. **EPIC 00 — Foundation & Repo Setup**
2. **EPIC 01 — Core Data Model (Postgres)**
3. **EPIC 02 — Ingestion Pipeline**
4. **EPIC 03 — Transcription & Segmentation**
5. **EPIC 04 — Search Infrastructure (V1 Minimal)**
6. **EPIC 05 — Core API (V1)**
7. **EPIC 06 — AI Enrichment Layers**
8. **EPIC 07 — Speaker Diarization & Profiles**
9. **EPIC 08 — Advanced Search & Indexing**
10. **EPIC 09 — Observability & Operations**
11. **EPIC 10 — Testing & Quality**
12. **EPIC 11 — Deployment & CI/CD**

## Rules of engagement

- Don’t start an EPIC if the previous one’s DoD isn’t met.
- Prefer shipping a thin vertical slice end-to-end early.
- Keep data contracts stable; version when needed.
- Every pipeline step must be idempotent and re-runnable.
