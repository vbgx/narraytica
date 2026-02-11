# Diarize Worker — Narralytica

The Diarize worker identifies **who is speaking and when** in a video.

It assigns speaker labels to transcript segments and clusters speech by speaker identity, enabling speaker-level analysis across the platform.

---

## 🎯 Purpose

The diarize worker handles:

- Speaker diarization (detecting speaker turns)
- Aligning speakers with transcript timestamps
- Clustering speech segments by voice similarity
- Producing structured speaker timelines

It transforms a raw transcript into **speaker-aware segments**.

---

## 📥 Inputs

The worker receives jobs containing:

- `video_id`
- Transcript artifact (timecoded text)
- Audio reference (for voice features if needed)
- Job identifiers

Jobs are triggered after transcription is complete.

---

## 📤 Outputs

After successful processing, the worker produces:

| Artifact | Location | Description |
|---------|----------|-------------|
| Speaker segments | Database | Segments labeled with speaker IDs |
| Speaker profiles (initial) | Database | Temporary per-video speaker identities |
| Job status update | Database | Marks diarization as completed |

These outputs allow downstream enrichment and cross-video speaker clustering.

---

## 🧱 Responsibilities

| Task | Description |
|------|-------------|
| Speaker turn detection | Identify changes in speaker voice |
| Voice embedding extraction | Create speaker voice representations |
| Clustering | Group segments by speaker |
| Alignment | Match speakers to transcript timecodes |
| Status tracking | Update job and diarization state |

---

## ⚙️ Performance Considerations

- Long audio files increase computational cost
- Models may require GPU or optimized CPU inference
- Diarization must remain robust to noise and overlap
- Voice clustering must be scalable across many segments

---

## 🔄 Idempotency

If a diarization job is retried:

- Existing speaker segments should be reused or safely replaced
- Speaker IDs must remain consistent within a video
- No duplicate speaker records should be created

---

## 🚫 Out of Scope

The diarize worker does **not**:

- Perform semantic enrichment
- Determine speaker real-world identity
- Generate embeddings for search
- Index data

Those steps are handled later in the pipeline.

---

## 🛠 Runbook

Operational procedures for rerunning or debugging diarization jobs are documented in:

- `services/workers/diarize/RUNBOOK.md`

---

## 📚 Related Documentation

- Pipeline overview → `docs/architecture/pipelines.md`
- Data model → `docs/architecture/data-model.md`
- Speaker schema → `packages/contracts/schemas/speaker.schema.json`