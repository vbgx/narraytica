# Ingest Worker — Narralytica

The Ingest worker is responsible for **bringing raw video into the platform** and preparing it for downstream processing.

It is the **entry point of the media pipeline**.

---

## 🎯 Purpose

The ingest worker handles:

- Fetching video from external sources (e.g. YouTube)
- Accepting uploaded media files
- Extracting metadata
- Downloading and storing media assets
- Extracting audio tracks for transcription

It transforms an external video reference into **internal, structured ingestion artifacts**.

---

## 📥 Inputs

The worker receives jobs that include:

- Video source (URL or upload reference)
- Basic metadata (title, channel, language if known)
- Job identifiers

Jobs are typically created by the API or Webhooks service.

---

## 📤 Outputs

After processing, the worker produces:

- Stored video file (object storage)
- Extracted audio file
- Normalized metadata in the database
- Ingestion status updates

These outputs are prerequisites for transcription.

---

## 🧱 Responsibilities

| Task | Description |
|------|-------------|
| Source fetch | Download video from supported platforms |
| Media storage | Store original media in object storage |
| Audio extraction | Extract audio track for ASR |
| Metadata normalization | Standardize video metadata |
| Status tracking | Update job and video ingestion state |

---

## ⚙️ Performance Considerations

- Large files must be streamed, not fully loaded into memory
- Retries must handle partial downloads safely
- Duplicate ingestion attempts must be detected and deduplicated

---

## 🔄 Idempotency

If the same ingestion job runs multiple times:

- Existing media files should not be duplicated
- Metadata updates should be safe
- The system should remain in a consistent state

---

## 🚫 Out of Scope

The ingest worker does **not**:

- Transcribe audio
- Run AI enrichment
- Index search data

Those are handled by downstream workers.

---

## 🛠 Runbook

Operational procedures for rerunning or debugging ingestion jobs are documented in: 
- `services/workers/ingest/RUNBOOK.md`

---

## 📚 Related Documentation

- Pipelines overview → `docs/architecture/pipelines.md`
- Data model → `docs/architecture/data-model.md`
- Storage layer → `docs/architecture/overview.md`


