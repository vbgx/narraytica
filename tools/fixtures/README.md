# Fixtures

This directory contains test fixtures and mock datasets used across development, testing, benchmarking, and local experimentation.

Fixtures provide controlled, reproducible inputs that allow engineers to test system behavior without relying on production data.

## Purpose

Fixtures exist to:

Provide sample datasets for local development

Support unit, integration, and load testing

Enable benchmark reproducibility

Simulate realistic scenarios without using sensitive data

Help validate data pipelines and search behavior

All fixtures must be safe to share and contain no real user data.

## Types of Fixtures
| Type        | Description                                                |
| ----------- | ---------------------------------------------------------- |
| `datasets/` | Small but representative data samples                      |
| `api/`      | Mock API responses                                         |
| `search/`   | Example indexed documents and queries                      |
| `events/`   | Sample event streams or logs                               |
| `ai/`       | Example prompts, responses, or embeddings (synthetic only) |


Subdirectories may be added as the system evolves.

## Design Principles
Synthetic or Anonymized Only

Fixtures must never contain:

real user data

confidential business data

API keys or secrets

All data should be synthetic, anonymized, or explicitly safe.

Small but Representative

Fixtures should be:

small enough to load quickly

realistic enough to reflect real system behavior

Deterministic

Using the same fixture should always produce the same expected results in tests and benchmarks.

## Naming Conventions

Use descriptive names that reflect the purpose of the fixture:

transcripts-small.json
search-index-basic.ndjson
events-sample-batch-01.json


Avoid generic names like test.json.

## Usage

Fixtures may be used in:

Automated tests

Benchmark scripts

Local debugging sessions

Data pipeline validation

Example usage:

pnpm test --fixture=transcripts-small


or loaded directly by scripts and test runners.

## Adding a New Fixture

When adding a fixture:

- Ensure the data is synthetic or fully anonymized

- Keep file size minimal while preserving realism

- Document its purpose in this README if non-obvious

Link it to the tests or benchmarks that depend on it

Fixtures are part of the project’s engineering infrastructure — treat them like stable test inputs, not throwaway data dumps.