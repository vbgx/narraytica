# Narralytica Contracts — Job model (runtime)

This document explains the *runtime contract model* for Jobs.

Contracts are the canonical source of truth for:
- API payload shapes (request/response)
- Worker runtime payloads (events, run state)
- Stored representations (DB documents or records)

**Rule:** code must conform to contracts; contracts must be explicit, versionable, and testable.

---

## Why do we have 3 schemas: `job`, `job_run`, `job_event`?

Because they represent **three different kinds of truth** in a distributed / asynchronous system:

1. **Job = intent (what should happen)**
2. **JobRun = attempt (a concrete execution of that job)**
3. **JobEvent = log (append-only facts emitted during execution)**

Separating these prevents drift, preserves auditability, and makes retries safe.

---

## `Job` — the durable intent

A `Job` is a durable command that represents **an intent to perform work**.

Examples:
- Ingest a video
- Transcribe audio
- Diarize speakers
- Compute AI layers
- Index segments

### What `Job` is for
- A stable reference for API and product views.
- A single identifier to attach status and lifecycle to.
- A **business-level** representation of “work requested”.

### What `Job` is NOT
- It is not a “run”.
- It is not a stream of logs.
- It should not encode transient execution details (worker hostname, attempt counters, etc.).

### Typical `Job` fields (conceptually)
- `id` — stable identifier
- `kind` — the type of work (`ingest`, `transcribe`, `enrich`, `index`, …)
- `status` — current state (`queued`, `running`, `succeeded`, `failed`, `canceled`, …)
- `created_at`, `updated_at`
- (optional) `input` / `params` — stable, deterministic job inputs

### Invariants (v0)
- `id` must be stable and unique.
- `kind` is a controlled vocabulary (enum).
- `status` is a controlled vocabulary (enum).
- `status` reflects the *latest known truth* (not every intermediate step).
- A `Job` can exist without any `JobRun` yet (queued / scheduled).

---

## `JobRun` — an execution attempt

A `JobRun` represents a **single attempt** to execute a job.

Why it exists:
- retries are normal (timeouts, worker crashes, rate limiting, infra hiccups)
- reprocessing can happen (manual rerun, backfill, replay)
- “job intent” must not be overwritten by attempt data

### What `JobRun` is for
- Capturing attempt-level metadata and timing.
- Distinguishing multiple attempts from the same job.
- Supporting correct “retry semantics”.

### Typical `JobRun` fields (conceptually)
- `id` — run identifier
- `job_id` — foreign key / reference to `Job`
- `status` — run-level state (`running`, `succeeded`, `failed`, …)
- `started_at`, (optional) `finished_at`
- (optional) `attempt` number or ordering key
- (optional) execution metadata (worker id, region, etc.) — avoid leaking into `Job`

### Invariants (v0)
- `JobRun.job_id` must reference an existing `Job`.
- A `Job` may have **multiple** runs over time.
- At most one run is “active” (running) at a time (recommended invariant).

---

## `JobEvent` — append-only runtime facts

A `JobEvent` is an **append-only fact** emitted during runtime.

It is the canonical replacement for:
- ad-hoc log lines
- unstructured status blobs
- hidden side channels (print statements, random JSON in DB)

### What `JobEvent` is for
- Observability: stable, queryable runtime events.
- Auditability: what happened, when, and why.
- Replay / debugging: reconstruct job progression from facts.

### Typical `JobEvent` fields (conceptually)
- `id` — event identifier
- `job_id` — always present
- `run_id` — present when event is tied to a specific attempt
- `type` — event name (`job.status_changed`, `progress`, `artifact.created`, `error`, …)
- `ts` — timestamp
- `payload` — event-specific details (structured, contract-first)

### Invariants (v0)
- Events are **append-only** (never mutated).
- `type` is controlled vocabulary (enum) or a namespaced string set.
- `job_id` is required.
- `run_id` is required for attempt-scoped events (recommended).
- `payload` should remain backward compatible when extended (additive changes).

---

## Recommended lifecycle (conceptual)

1) API creates a `Job`:
- status = `queued`

2) Worker picks job and starts an attempt:
- create `JobRun` (status = `running`)
- emit `JobEvent` ("job.status_changed": queued → running)

3) Worker produces intermediate events:
- "progress", "layer.completed", "artifact.created", etc.

4) Worker completes:
- set `JobRun` status = succeeded/failed
- update `Job` status accordingly
- emit terminal `JobEvent` (with final status + summary)

---

## Drift prevention rules (the point of contracts)

- API should not invent new job fields without updating schemas + contract tests.
- Workers should not emit ad-hoc event shapes: add them in `job_event.schema.json`.
- Runtime metadata belongs in `JobRun` or `JobEvent`, not in `Job`.
- Prefer adding fields (backward compatible) over renaming/breaking.
