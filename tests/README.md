# Tests

This directory contains all automated tests for the project.
The testing strategy is designed to ensure correctness, stability, and safe evolution of the system.

Testing is a core part of engineering quality and is required for all significant changes.

Testing Layers

The project uses multiple layers of testing, each with a different purpose:

Layer	Purpose
Unit Tests	Validate individual functions or modules in isolation
Contract Tests	Enforce API, schema, and cross-service compatibility
Integration Tests	Verify real interactions between subsystems
Load / Performance Tests	Measure behavior under scale and stress

Each layer catches different classes of issues. Together, they provide confidence in both correctness and system behavior.

Directory Structure
tests/
  contract/      → Interface and schema guarantees
  integration/   → Multi-component system tests
  load/          → Performance and stress scenarios


Additional categories may be added as the system evolves.

Principles
Fast Feedback First

Unit and contract tests should run quickly and provide immediate feedback during development and CI.

Realistic Where It Matters

Integration and load tests simulate real-world conditions using controlled environments and fixtures.

Deterministic

All tests must produce consistent results when run in the same environment. Flaky tests are treated as defects.

Isolated

Tests must not depend on:

production systems

shared external state

non-deterministic data

Running Tests

Tests are typically executed via:

pnpm test


Or by category:

pnpm test:unit
pnpm test:contract
pnpm test:integration
pnpm test:load


(Exact commands depend on project configuration.)

When to Add Tests

Add tests when:

Introducing new features

Fixing bugs

Changing shared schemas or APIs

Modifying system interactions

Improving performance-sensitive areas

A change without appropriate tests increases long-term risk.

What Tests Should Not Be

❌ Manual-only verification
❌ Dependent on production data
❌ Ignored when failing

If a test fails, it is a signal — investigate the root cause rather than bypassing it.

A healthy test suite is a living safety net that allows the project to evolve with confidence.