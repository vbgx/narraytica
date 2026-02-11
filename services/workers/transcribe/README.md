# Transcribe Worker — Narralytica

The Transcribe worker converts **audio into structured, time-coded text**.

It is responsible for turning raw speech into a **machine-usable transcript** that can be segmented, enriched, and indexed.

This worker is the foundation of all downstream intelligence.

---

## 🎯 Purpose

The transcribe worker handles:

- Speech-to-text (ASR)
- Time-aligned transcript generation
- Language detection (if not provided)
- Basic text normalization
- Preparation for segmentation

It transforms an audio file into a **structured transcript artifact**.

---

## 📥 Inputs

The worker receives jobs containing:

- `video_id`
- `audio_object_key` (location of extracted audio)
- Optional language hint
- Job metadata and identifiers

Jobs are triggered after ingestion is complete.

---

## 📤 Outputs

After successful processing, the worker produces:

| Artifact | Location | Description |
|---------|----------|-------------|
| Transcript file | Object storage | Full transcript with timestamps |
| Transcript metadata | Database | Language, duration, provider info |
| Job status update | Database | Marks transcription as completed |

This output is consumed by the **segmentation and enrichment steps**.

---

## 🧱 Responsibilities

| Task | Description |
|------|-------------|
| ASR processing | Convert audio to text using a provider |
| Timestamp alignment | Align text with timecodes |
| Language detection | Detect spoken language when unknown |
| Transcript storage | Store transcript artifact |
| Status tracking | Update job and transcript state |

---

## ⚙️ Performance Considerations

- Audio may be long (hours)
- Streaming or chunked transcription may be required
- Providers may impose rate or duration limits
- Transcription must be resumable or restartable

---

## 🔄 Idempotency

If a transcription job is retried:

- Existing transcripts should be reused or safely overwritten
- Duplicate transcript records must not be created
- State must remain consistent

---

## 🚫 Out of Scope

The transcribe worker does **not**:

- Split transcript into segments
- Run AI enrichment
- Generate embeddings
- Index search data

Those tasks occur in later pipeline stages.

---

## 🛠 Runbook

Operational procedures for rerunning or debugging transcription jobs are documented in:

- `services/workers/transcribe/RUNBOOK.md`

---

## 📚 Related Documentation

- Pipeline overview → `docs/architecture/pipelines.md`
- Data model → `docs/architecture/data-model.md`
- Contracts → `packages/contracts`
