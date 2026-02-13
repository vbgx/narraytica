# packages/search — Canonical Search (Single Source of Behavior)

## Purpose

This package is the **only** place where search product semantics live:

- Query normalization & filter semantics
- Hybrid merge / ranking / tie-breaking
- Core domain errors (non-HTTP)
- Canonical core types aligned with JSON Schemas

Everything else (API, workers) is **wiring + adapters**.

## Where logic lives

- `filters.py` — **single source of truth** for filter meaning + defaults + normalization
- `ranking.py` — hybrid merge, scoring rules, deterministic tie-break
- `engine.py` — orchestration using ports (backend-agnostic)
- `types.py` — canonical types aligned with contracts
- `errors.py` — canonical error surface (no HTTP)

## Contracts-first rule

`SearchQuery` and `SearchResult` must stay aligned with JSON Schemas in `packages/contracts/schemas/`.

If a schema changes:
1) update schema
2) update `types.py` + `filters.py` (normalization)
3) update golden tests
4) only then update adapters

## Forbidden imports (anti-drift)

This package MUST NOT import:
- `fastapi` / `starlette` / any HTTP framework
- `services.api` / `services.workers`
- OpenSearch / Qdrant clients (adapters live outside, injected through ports)

## How to add a filter (safe path)

1) Update `packages/contracts/schemas/search_query.schema.json`
2) Add field to `FilterSpec` (types.py)
3) Implement normalization + validation in `filters.py`
4) Add golden tests covering:
   - normalization determinism
   - unsupported values / bad ranges
5) Update adapters to translate FilterSpec -> backend query

If you skip any step, you are creating drift.

## Determinism & drift prevention

- normalization sorts lists and strips empties
- ranking tie-breaks deterministically on `(combined desc, id asc)`
- pagination is expressed as `page.limit` + `page.offset` only
