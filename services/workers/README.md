# Workers — Narralytica

This directory contains the **pipeline workers** that process videos into structured, searchable intelligence.

Workers are designed to be:
- **idempotent** (safe to retry)
- **observable** (logs/metrics/traces)
- **contract-driven** (payloads and artifacts are documented)

Each worker folder contains:
- `README.md` — what the worker does
- `RUNBOOK.md` — how to operate and debug it
- `CONTRACT.md` — formal job payload and outputs
- `src/` — implementation
- `tests/` — worker tests

---

## Pipeline Order (V1)

1. **ingest/** — download/upload media, extract audio, store artifacts  
2. **transcribe/** — ASR to timecoded transcript  
3. **diarize/** — speaker diarization and clustering (per video)  
4. **enrich/** — AI layers (embeddings, topics, sentiment, stance, CEFR, summaries)  
5. **indexer/** — populate OpenSearch + Qdrant for search  
6. **trend/** — aggregate analytics over time (V1.1+)

---

## Worker Index

- Ingest → `./ingest/README.md`
- Transcribe → `./transcribe/README.md`
- Diarize → `./diarize/README.md`
- Enrich → `./enrich/README.md`
- Indexer → `./indexer/README.md`
- Trend → `./trend/README.md`

---

## Operational Rules

- Workers must update job state transitions via the canonical job system.
- Outputs must conform to `packages/contracts/` schemas.
- Retries must not create duplicate artifacts (use upserts and stable IDs).
- Each worker must emit:
  - structured logs with job_id + video_id
  - metrics (success/failure/latency)
  - traces (span per major step)

---

## Where to Go Next

- Pipelines overview → `../../docs/architecture/pipelines.md`
- Data model → `../../docs/architecture/data-model.md`
- Contracts → `../../packages/contracts/README.md`

---
Back: `../README.md` · Up: `../../README.md`
