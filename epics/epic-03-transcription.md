# EPIC 03 — Transcription Pipeline

## 🎯 Goal

Build the pipeline that converts **audio into structured, timecoded transcripts**.

This EPIC transforms raw audio extracted during ingestion into machine-readable speech data that can be segmented, analyzed, and indexed.

---

## 📦 Scope

This EPIC includes:

- Transcription job orchestration  
- Integration with ASR (Automatic Speech Recognition) providers  
- Generation of time-aligned transcripts  
- Language detection and metadata storage  
- Persistence of transcript artifacts  
- Job state tracking and error handling  

---

## 🚫 Non-Goals

This EPIC does **not** include:

- Speaker diarization  
- Semantic segmentation  
- AI enrichment layers  
- Search indexing  

It focuses solely on **speech-to-text conversion**.

---

## 🧱 Pipeline Overview

1. Ingestion completes and audio becomes available  
2. API or orchestrator creates a transcription job  
3. Transcribe worker retrieves audio  
4. ASR provider processes audio into text  
5. Transcript is aligned with timestamps  
6. Transcript artifact is stored  
7. Transcript metadata is saved in DB  
8. Job is marked as completed  

---

## 🗂 Deliverables

- Transcription job model and routing  
- Transcribe worker implementation  
- ASR provider integration (pluggable)  
- Timecode alignment logic  
- Transcript storage format  
- Language detection and persistence  
- Logging and telemetry for ASR jobs  

---

## 🗂 Issues

1. Extend job model for transcription stage  
2. Implement transcription job trigger logic  
3. Create transcribe worker skeleton  
4. Integrate first ASR provider  
5. Implement transcript timecode format  
6. Store transcript artifacts in object storage  
7. Persist transcript metadata in DB  
8. Add language detection fallback  
9. Implement retry and timeout logic  
10. Add logging and tracing  
11. Write integration tests for transcription flow  
12. Document transcription runbook  

---

## ✅ Definition of Done

EPIC 03 is complete when:

- Audio files can be transcribed automatically  
- Transcripts include accurate timestamps  
- Language is detected or confirmed  
- Transcript artifact is stored and retrievable  
- Transcript metadata exists in DB  
- Job states update correctly  
- Failed jobs can be retried safely  
- Documentation exists for troubleshooting  

---

## ⚠️ Risks / Mitigations

| Risk | Mitigation |
|------|------------|
| ASR provider outages | Support pluggable providers |
| Long audio causing timeouts | Chunk audio into segments |
| Incorrect language detection | Allow language hints and overrides |
| Cost spikes from long audio | Add duration limits and monitoring |

---

## 🔗 Links

- Pipelines overview → `docs/architecture/pipelines.md`  
- Transcript schema → `packages/contracts/schemas/transcript.schema.json`  
- Transcribe worker → `services/workers/transcribe/README.md`  
- Transcription runbook → `services/workers/transcribe/RUNBOOK.md`
