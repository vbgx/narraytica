# API Service Architecture
Purpose

This document describes the internal architecture of the API service.
It complements the global API architecture document in docs/architecture/api.md by focusing on this service’s structure and responsibilities.

Responsibilities

The API service is responsible for:

Handling HTTP requests

Authentication and authorization

Input validation

Calling domain services

Persisting canonical data

Emitting events for asynchronous processing

Returning structured responses and errors

It must remain stateless and horizontally scalable.

Internal Layers
Routing Layer

Defines HTTP routes and maps them to handlers.

Middleware Layer

Handles cross-cutting concerns:

auth

permissions

rate limiting

logging

request validation

Controller Layer

Thin handlers that:

validate inputs

call domain logic

shape responses

Domain Layer

Encapsulates business rules and invariants.
Must not depend on HTTP concerns.

Infrastructure Layer

Handles:

database access

event publishing

external service calls

Async Boundaries

Long-running tasks must not execute inside request handlers.
Instead:

Persist canonical state

Emit an event

Let workers process asynchronously

Observability

Each request must produce:

structured logs

latency metrics

error tracking

correlation IDs

Scaling

The service scales horizontally.
No local state must be required for correctness.

End of API Service Architecture
