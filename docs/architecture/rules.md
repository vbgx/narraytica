# Architecture rules (anti-drift)

These rules are enforced by CI via `make ci-architecture`.

## R1 — No HTTP in packages/**
- Forbidden imports: `fastapi`, `starlette`, `uvicorn`
- Rationale: packages are the brain (pure), HTTP is an adapter concern.

## R2 — Routes are glue
- In `services/api/src/routes/**`, forbidden infra clients:
  - Postgres: `psycopg`, `asyncpg`, `sqlalchemy`
  - Search: `opensearch`, `opensearchpy`, `elasticsearch`, `qdrant_client`
- Rationale: routes validate input, call use-cases, map to JSON. No infra.

## R3 — Workers don’t own clients (progressive)
- In `services/workers/**/src/**`, same infra clients are forbidden.
- Temporary exceptions are allowed ONLY via allowlist with expiration.

## R4 — Single source of behavior
- Routes must not import `services.api.src.search.*`
- Rationale: search behavior must converge into `packages/search`.

## Allowlist policy
Allowlist is timeboxed and MUST include:
- `rule_id`, `file`, `import`, `reason`, `expires_on` (YYYY-MM-DD)
CI fails if an allowlist entry is expired.
