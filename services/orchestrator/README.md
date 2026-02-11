# Orchestrator — Narralytica Workflow Engine

The Orchestrator coordinates **multi-step processing workflows** across Narralytica workers.

While workers perform individual tasks (ingestion, transcription, enrichment, indexing), the orchestrator ensures those tasks happen in the **correct order**, with proper retries and state tracking.

---

## 🎯 Purpose

The orchestrator exists to:

- Manage end-to-end processing pipelines
- Handle dependencies between processing steps
- Retry failed steps safely
- Track workflow state across services
- Ensure pipelines are observable and recoverable

It is the **control layer** for long-running, distributed jobs.

---

## 🧱 What It Orchestrates

A typical video processing workflow may look like:

1. Ingest video metadata and media
2. Extract audio
3. Transcribe speech
4. Segment transcript with timestamps
5. Run AI enrichment layers
6. Generate embeddings
7. Index into search systems

The orchestrator ensures each step runs **only when prerequisites are satisfied**.

---

## 🔄 Workflow Responsibilities

The orchestrator:

- Schedules tasks for workers
- Listens for completion or failure events
- Applies retry policies
- Marks workflows as complete or failed
- Maintains job lineage and state transitions

Workers do not call each other directly — all coordination flows through the orchestrator.

---

## 🧠 Design Principles

### 1️⃣ Resilient by Default
Workflows must survive:
- Worker crashes
- Temporary service outages
- Partial failures

### 2️⃣ Idempotent Tasks
Each task must be safe to retry without corrupting data.

### 3️⃣ Observable
All workflow steps should emit events and logs for debugging and monitoring.

---

## 🛠 Possible Technologies

Depending on platform evolution, the orchestrator may be built with:

- Temporal
- Celery
- Custom job queues

The specific tool may change, but the orchestration role remains constant.

---

## 🔐 Separation of Concerns

The orchestrator:
- Does not perform heavy AI or media processing
- Does not expose public APIs
- Does not store primary data

It only coordinates and tracks workflows.

---

## 📚 Related Documentation

- Pipelines → `docs/architecture/pipelines.md`
- Event model → `docs/specs/events.md`
- Workers → `services/workers/`
- Runbooks → `docs/runbooks/backfills.md`
