# API Architecture
Purpose

This document describes the architecture of the API layer: its responsibilities, boundaries, and how it interacts with storage, workers, and downstream subsystems.

The API is designed to be:

stateless

secure

observable

backward compatible

safe under load

Responsibilities

The API layer is responsible for:

Authentication (who are you?)

Authorization (what can you do?)

Input validation and normalization

Request routing and orchestration of downstream calls

Returning consistent responses and errors

Emitting events for asynchronous processing

Enforcing rate limits and abuse protections

The API should not contain heavy background logic; long-running operations are delegated to workers.

Non-Responsibilities

The API layer must not:

Run backfills or long processing in request/response paths

Depend on search as a source of truth

Embed business logic that belongs in domain services/libraries

Store secrets in logs or return internal errors to clients

High-Level Components
1. Request Handling

HTTP server receives the request

Middleware chain applies:

auth

permission checks

rate limiting

request validation

Requests are rejected early when invalid or unauthorized.

2. Domain Layer

The API calls domain modules that encapsulate business rules and invariants.

This keeps controllers thin and avoids drifting logic across endpoints.

3. Data Access

The API reads and writes to the primary database for canonical entities.

Rules:

No direct writes to derived systems from request paths unless explicitly intended

Prefer transactional writes for multi-entity changes

Use idempotency keys for write endpoints where duplicates are likely

4. Event Emission

For operations that require asynchronous processing (indexing, enrichment, long jobs), the API emits events.

Example pattern:

API writes canonical record

API emits domain.entity_created event

Workers consume and process

This avoids long request latency and improves reliability.

Request Lifecycle

Typical flow:

Parse request

Authenticate principal

Authorize action (permissions)

Enforce rate limits

Validate payload

Execute domain operation

Commit storage changes

Emit events (if needed)

Return response

Each step must be observable and have clear error handling.

Error Model

Errors must be:

consistent across endpoints

safe (no secret leakage)

actionable (clear code + message)

The canonical error model is documented in:

services/api/ERROR_MODEL.md

The API should return:

structured error responses

stable error codes for clients

correlation IDs for debugging

Rate Limiting

Rate limiting protects the API and expensive downstream operations.

Rules:

Enforce globally (edge or middleware) when possible

Apply stricter limits to expensive endpoints

Return 429 with retry headers when limit exceeded

Rate limiting policy is specified in:

docs/specs/rate-limits.md

services/api/RATE_LIMITS.md

Permissions

Authorization must be enforced at the API boundary for all protected operations.

Principles:

deny-by-default

explicit allow via roles/permissions

tenant-aware scoping where applicable

See:

docs/specs/permissions.md

Observability

Each request must produce:

structured logs

metrics (latency, error rate, throughput)

correlation identifiers

Recommended identifiers:

request_id per request

correlation_id per workflow spanning multiple services

Backward Compatibility

API changes must be managed carefully:

avoid breaking response shapes without versioning

additive changes preferred

deprecations must be documented

Contract tests should protect compatibility:

tests/contract/

Scaling and Performance

The API is designed to scale horizontally:

stateless instances

shared storage dependencies

async processing for heavy tasks

Performance principles:

avoid N+1 queries

constrain payload sizes

paginate list endpoints

enforce timeouts on downstream calls

Security Considerations

Strict input validation and sanitization

Secrets never logged

Safe error responses

Abuse prevention (rate limiting, IP throttling, quotas)

See also:

SECURITY.md

Summary

The API layer is the system’s controlled entrypoint:

validates and protects the platform

persists canonical data

emits events for asynchronous work

returns stable, consistent responses

It should remain thin, predictable, and safe under load.

End of API Architecture Document
