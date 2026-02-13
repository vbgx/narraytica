# Commands Runbook (Local Dev + CI Gates)

This document is the single source of truth for the commands you can run
in this repo. No improvisation: use these deterministic gates.

------------------------------------------------------------------------

## 0) Standard Workflow (Mandatory)

### Create a branch

git checkout -b feature/`<short-name>`{=html} \# or git checkout -b
refacto/pX

### Run architecture gate before committing

make ci-architecture

If it fails: fix first, then commit.

### Stage explicitly

git status git add path/to/file1 path/to/file2 git diff --cached

### Commit format

git commit -m "scope(type): short summary

Why: - ...

What: - ...

Impact: - ..."

Allowed scopes: - architecture - contracts - search - persistence -
workers - tests - ci - docs - refacto

### Push

git push -u origin feature/`<short-name>`{=html}

------------------------------------------------------------------------

## 1) Primary Gate

make ci-architecture

Checks: - schema duplication - OpenAPI validity - allowlist policy -
contract tests - dependency boundaries

------------------------------------------------------------------------

## 2) Fast Diagnostics

### Allowlist policy

make ci-exceptions

### Contract tests

make test-contracts

### Dependency boundaries

make check-boundaries

Explicit form: uv run python tools/ci/check_dependency_boundaries.py
--root . --config tools/ci/dependency_boundaries.yaml --allowlist
tools/ci/dependency_boundaries_allowlist.yaml

------------------------------------------------------------------------

## 3) Individual Checks

Schema duplication: uv run python
tools/ci/check_no_schema_duplication.py

OpenAPI validation: uv run python tools/scripts/openapi_validate.py

Allowlist policy: uv run python tools/ci/check_allowlist_policy.py

------------------------------------------------------------------------

## 4) Python Commands

Lint: ruff check .

Format: ruff format .

Tests: pytest -q

Contract tests only: pytest -q tests/contract

------------------------------------------------------------------------

## 5) Node Commands

Workspace lint: pnpm -r lint

------------------------------------------------------------------------

## 6) Pre-commit

Install hooks: pre-commit install

Run manually: pre-commit run --all-files

------------------------------------------------------------------------

## Non-Negotiable Rules

-   No schema change without updating contract fixtures + tests.
-   No allowlist without expiry + drift-map entry + owner.
-   No infra imports inside packages/.
-   No CI quick fixes.
-   CI must fail on violations.
