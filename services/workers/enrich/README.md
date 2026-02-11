# Enrich Worker — Narralytica

The Enrich worker adds **AI-powered analytical layers** to transcript segments.

It transforms raw, speaker-aware text into **structured intelligence** that powers search, analytics, and end-user products.

---

## 🎯 Purpose

The enrich worker is responsible for generating semantic and analytical layers such as:

- Embeddings
- Summaries
- Topic detection
- Sentiment analysis
- Stance detection (for/against/neutral)
- CEFR language level classification

Each of these outputs is stored as a **layer** attached to transcript segments.

---

## 📥 Inputs

The worker receives jobs containing:

- `video_id`
- Segmented transcript (with speaker labels)
- Job metadata
- Optional model or layer configuration

Jobs are triggered after diarization and segmentation.

---

## 📤 Outputs

After successful processing, the worker produces:

| Artifact | Location | Description |
|---------|----------|-------------|
| Segment embeddings | Vector store | Semantic vectors for search |
| Layer data | Database | Topics, sentiment, stance, CEFR, summaries |
| Job status update | Database | Marks enrichment as completed |

These layers power **search, filtering, and analytics**.

---

## 🧱 Responsibilities

| Layer | Purpose |
|------|---------|
| Embeddings | Semantic search and clustering |
| Summaries | Condensed meaning of segments |
| Topics | Subject classification |
| Sentiment | Emotional tone detection |
| Stance | Position toward a subject |
| CEFR | Language complexity level |

Each layer is computed independently and can evolve over time.

---

## ⚙️ Performance Considerations

- Embeddings may be computed in batches
- Model calls should be cached when possible
- Large transcripts must be processed in chunks
- Rate limits of external AI providers must be respected

---

## 🔄 Idempotency

If enrichment runs multiple times:

- Layers should be overwritten safely or versioned
- Duplicate vectors must not be created
- Segment-to-layer relationships must remain consistent

---

## 🚫 Out of Scope

The enrich worker does **not**:

- Fetch or store raw media
- Perform transcription or diarization
- Directly expose data to users
- Manage search indexing

Indexing happens in the **indexer worker**.

---

## 🛠 Runbook

Operational procedures for rerunning or debugging enrichment jobs are documented in:

- `services/workers/enrich/RUNBOOK.md`

---

## 📚 Related Documentation

- Data model → `docs/architecture/data-model.md`
- Pipelines → `docs/architecture/pipelines.md`
- Layer schema → `packages/contracts/schemas/layer.schema.json`

