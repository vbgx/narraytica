# Drift Map — Baseline Hotspots & Tracking (Phase 1)

Purpose: make drift visible, localize hotspots, and track reduction over time.

This document is the single place where:
- hotspots are listed (with file/folder links),
- exceptions are justified (with expiry),
- baseline metrics are tracked (allowlist count, violations, contract coverage).

---

## Hotspots (baseline)

| Hotspot | Why risk | Symptoms | Plan (phase) | Owner |
|---|---|---|---|---|
| `services/api/src/routes/search.py` | Route tends to become “god module” (query parsing + scoring + persistence + search clients) | Growing file size, many imports, mixed responsibilities, hard-to-test | Split into (1) HTTP layer (FastAPI) (2) domain query contract (packages/contracts) (3) search adapter (packages/search) (Phase 2) | TBD |
| `services/api/src/search/**` | High drift surface: templates, mappings, client wiring, index naming | Dup templates, inconsistent index patterns, mapping mismatch | Canonical templates live under `infra/opensearch/templates/`; services load templates from there only (Phase 1–2) | TBD |
| `services/workers/indexer/src/**` | Worker tends to duplicate search client logic | Dup client config, index naming drift, inconsistent retry/backoff | Move search client creation/config into `packages/search/*`; worker uses adapter contracts only (Phase 3) | TBD |
| `services/workers/ingest/src/db/**` | Persistence glue often leaks infra libs into domain boundaries | Direct `psycopg/asyncpg/sqlalchemy` imports outside infra layer | Introduce `packages/persistence` port + service-level adapter; tests use fakes (Phase 3–4) | TBD |
| `services/workers/transcribe/src/db/**` | Same as ingest: DB client drift + test coupling | Infra clients in tests, brittle integration setup | Same plan as ingest; isolate DB access behind adapter (Phase 3–4) | TBD |
| `services/workers/enrich/src/layers/**` | AI output evolves fast; schema drift likely | Unversioned payloads, ad-hoc JSON, no envelope | Enforce “Layer Envelope” schema in `packages/contracts`; every layer output must validate (Phase 2–4) | TBD |
| `packages/search/opensearch/**` | Mapping/settings look like schema; risk of parallel contracts | `properties/required` keys trigger false positives; shape drift vs templates | Strict whitelist + doc: these are templates, NOT contracts; keep minimal + versioned (Phase 2) | TBD |
| `infra/opensearch/templates/**` | Critical infra contract: changes impact ingestion + query | Mapping mismatch, reindex required, unknown ownership | Add `_meta.owner`, `version`, and CHANGELOG discipline; require PR note when changed (Phase 2) | TBD |

---

## Temporary exceptions (must expire)

Every exception used to keep CI green MUST be listed here and referenced by allowlist via `drift_map`.

| Exception ID | Rule | Location | Justification | Expiry (YYYY-MM-DD) | Removal plan | Owner |
|---|---|---|---|---|---|---|
| EXC-001 | R3_WORKERS_NO_LOCAL_CLIENTS | `services/workers/ingest/src/db/postgres.py` imports `psycopg` | Legacy worker DB access; will be replaced by `packages/persistence` repos | 2026-03-01 | Move DB access behind `packages/persistence` adapter and delete local client | victor |
| EXC-002 | R3_WORKERS_NO_LOCAL_CLIENTS | `services/workers/transcribe/src/db/postgres.py` imports `psycopg` | Legacy worker DB access; will be replaced by `packages/persistence` repos | 2026-03-01 | Move DB access behind `packages/persistence` adapter and delete local client | victor |

Policy:
- No exception without expiry + owner + removal plan.
- Any allowlist entry without a drift-map reference is invalid.

---

## Metrics (baseline & tracking)

Record these values at least once per phase (or weekly).

### Allowlist / exceptions
- Dependency boundaries allowlist entries: ___
- Active exceptions in this doc: ___
- Goal: allowlist count ↓, exceptions ↓

### Violations
- Boundary violations (fail mode): 0
- Boundary warnings (report mode): ___
- Goal: warnings ↓ to 0 or moved into explicit, expiring exceptions.

### Contract coverage
- Schemas under `packages/contracts/schemas/`: ___
- Contract fixtures/examples under `tests/fixtures/contracts/`: ___
- Contract tests count (e.g. `tests/contract/*`): ___
- Goal: coverage ↑; minimum includes search + jobs + entities + layer envelope.

---

## Rule (anti-staleness)

Any CI exception (allowlist entry, ignore rule, warning downgrade) MUST:
1) reference this document (Exception ID),
2) include an expiry date,
3) include an owner,
4) have a removal plan.

If an exception is added without updating this doc, the PR is invalid.

---

## Phase roadmap (drift reduction)

### Phase 1 (baseline — current)
- ✅ dependency boundaries check in CI (allowlist with expiry + drift-map enforced)
- ✅ no schema duplication check in CI
- ✅ tests/contract validate fixtures against canonical schemas (search + jobs + entities + layer envelope)
- ✅ drift-map initial documented (hotspots + plan)
- ✅ CI fails on violations (not just warnings)

### Phase 2 (unbundle hotspots)
- Split heavy routes into thin HTTP + adapters
- Enforce “Layer Envelope” schema everywhere in enrich pipeline
- Collapse search templates/mappings under single canonical location

### Phase 3 (ports/adapters hardening)
- Introduce persistence/search adapters in `packages/*`
- Workers use adapters; infra clients contained

### Phase 4+ (stabilize evolution)
- Version layer outputs & migration policy
- Reduce allowlist toward 0
- Enforce doc update for every new exception

---

## Appendix — Commands to refresh metrics

### Count allowlist entries
- `rg -n "^- rule_id:" tools/ci/dependency_boundaries_allowlist.yaml | wc -l`

### Count schemas
- `ls -1 packages/contracts/schemas/*.schema.json | wc -l`

### Count contract fixtures
- `ls -1 tests/fixtures/contracts/*.json | wc -l'
