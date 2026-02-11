# EPIC 07 — Speaker System

## 🎯 Goal

Build the system that enables Narralytica to understand **who is speaking**, not just what is being said.

This EPIC establishes speaker-aware intelligence across videos and lays the groundwork for speaker-level analysis products like SpeakerDNA.

---

## 📦 Scope

This EPIC includes:

- Speaker diarization pipeline (per video)
- Speaker entity model in the database
- Linking segments to speaker IDs
- Basic cross-video speaker clustering (voice similarity)
- Speaker metadata storage (when known)
- API endpoints for speaker retrieval

---

## 🚫 Non-Goals

This EPIC does **not** include:

- Real-world identity verification
- Biographical research on speakers
- Reputation scoring or ranking
- Social graph analysis

It focuses on **technical speaker identification and clustering**.

---

## 🧱 Speaker Architecture

| Component | Role |
|-----------|------|
| Diarization | Detect speaker turns within a video |
| Voice embeddings | Represent speaker voice characteristics |
| Clustering | Group similar voices across segments |
| Speaker entity | Canonical representation in the DB |

Each segment must be linked to **one speaker ID**.

---

## 🗂 Deliverables

- Diarize worker implementation
- Speaker table and relationships
- Voice embedding storage strategy
- Basic clustering pipeline
- Segment-to-speaker linking
- API endpoints for speakers
- Documentation of speaker model

---

## 🗂 Issues

1. Implement diarization job orchestration
2. Add speaker table schema
3. Store speaker IDs per segment
4. Generate voice embeddings for segments
5. Implement per-video speaker clustering
6. Explore cross-video clustering strategy (basic)
7. Add speaker metadata fields
8. Expose `/speakers` API endpoints
9. Add logging and performance monitoring
10. Write integration tests for speaker linking
11. Document speaker system architecture
12. Create runbook for diarization and clustering

---

## ✅ Definition of Done

EPIC 07 is complete when:

- Each segment has a speaker ID
- Speakers are distinguishable within a video
- Basic clustering works across segments
- Speaker data can be retrieved via API
- Diarization jobs are retryable
- Documentation explains speaker lifecycle

---

## ⚠️ Risks / Mitigations

| Risk | Mitigation |
|------|------------|
| Poor diarization quality | Allow model tuning and upgrades |
| Over-merging speakers | Use conservative clustering thresholds |
| False identity assumptions | Clearly separate technical ID from real identity |
| High compute cost | Batch processing and caching |

---

## 🔗 Links

- Speaker schema → `packages/contracts/schemas/speaker.schema.json`
- Diarize worker → `services/workers/diarize/README.md`
- Data model → `docs/architecture/data-model.md`
