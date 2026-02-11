# Integration Tests

This directory contains integration tests that verify multiple parts of the system work together correctly.

Unlike unit tests (which test isolated components), integration tests validate real interactions between subsystems such as the API, database, search, pipelines, and AI layers.

## Purpose

Integration tests help us:

Ensure subsystems communicate correctly

Detect issues caused by configuration, wiring, or environment mismatches

Validate real data flows across boundaries

Catch regressions that unit tests cannot detect

They provide confidence that the system works as a whole, not just in isolated pieces.

What Integration Tests Cover

Typical integration scenarios include:

Area	Example
API ↔ Database	Creating a record via API and verifying persistence
API ↔ Search	Ingesting data and verifying it becomes searchable
Pipelines ↔ Storage	Running ingestion and checking stored outputs
Events ↔ Workers	Emitting events and verifying downstream processing
AI Layers ↔ API	End-to-end inference request and response validation
Characteristics
Real Components, Controlled Environment

Integration tests use real implementations (DB, search, services) but in:

local environments

test containers

ephemeral databases

They should never rely on production systems.

Slower Than Unit Tests

Because they involve multiple systems, integration tests are expected to be slower and more resource-intensive than unit tests.

Deterministic

Even though multiple systems are involved, results must be predictable and reproducible.

Test Environment

Integration tests typically require:

A running test database

Search index or mock equivalent

Local or test configuration

Seed or fixture data

Setup and teardown should be automated to avoid state leakage between tests.

When to Add an Integration Test

Add an integration test when:

A feature spans multiple services or layers

A bug was caused by system interaction (not local logic)

A data pipeline or ingestion flow is introduced

Search indexing and retrieval must be validated end-to-end

If a failure would only appear when systems are connected, it belongs here.

What Integration Tests Should Not Do

❌ Depend on production services
❌ Use real user data
❌ Be flaky or environment-dependent

If a test is unstable, fix the setup — don’t ignore the failure.

Goal

The goal of integration tests is system-level confidence.
They ensure that when all pieces are wired together, the platform behaves as expected in realistic conditions.