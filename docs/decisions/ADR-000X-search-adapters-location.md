# ADR-000X — Search adapters location (OpenSearch/Qdrant)

Status: Accepted
Date: 2026-02-13

## Context

We have a monorepo with strict layering:
- packages/ = pure domain / contracts / pure functions
- services/api = HTTP glue + wiring
- services/workers = orchestration + execution

Search ports live in `packages/search` (LexicalSearchPort, VectorSearchPort, HybridMergePort).
We need concrete backend implementations for OpenSearch and Qdrant.

## Decision

Do NOT implement backend IO adapters inside `packages/search`.

Implement IO adapters in infra layer outside packages:
- `services/api/src/infra/search_adapters/opensearch.py`
- `services/api/src/infra/search_adapters/qdrant.py`

Optionally shared between API + workers via:
- `services/infra/search_adapters/` (shared module), OR
- a dedicated infra package `packages/search_infra/` that depends on network clients,
  while `packages/search` never depends on it.

`packages/search` remains pure:
- ports
- types/contracts shaping
- normalization
- ranking/merge (pure)

## Consequences

- Domain purity preserved; no network deps in packages/
- Deterministic CI: unit tests for ranking/normalization remain pure
- IO tests are isolated to services/infra (can be optional/integration)
- Wiring stays explicit in services/api and services/workers

## Non-goals

- No direct OpenSearch/Qdrant clients imported from routes or domain packages
