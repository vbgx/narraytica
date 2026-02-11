# Contributing

Thanks for contributing to this project. This document explains how we work, how to propose changes, and what “good contributions” look like.

The project values: clarity, correctness, safety, and operational discipline.

Ground Rules

Be respectful and professional (see CODE_OF_CONDUCT.md)

Prefer small, reviewable changes over large rewrites

Make changes in a way that preserves backward compatibility unless explicitly agreed

Never introduce secrets or sensitive data into the repository

Getting Started
1) Fork / Clone

Clone the repository and install dependencies:

pnpm install

2) Environment

Create a local env file:

cp .env.example .env


Fill required variables using local/test credentials only.

3) Run the project
pnpm dev


(Exact commands may vary depending on workspace setup.)

How to Contribute
Issues First

For non-trivial work, open an issue (or comment on an existing one) describing:

the problem

the proposed approach

expected impact (API, data, ops, cost)

any risks

This avoids duplicate effort and aligns expectations early.

Branching

Use short, descriptive branch names:

feat/<topic>

fix/<topic>

docs/<topic>

chore/<topic>

Examples:

feat/search-reranking

fix/api-error-model

docs/pipelines-runbook

Commit Messages

Prefer conventional-style messages:

feat(scope): ...

fix(scope): ...

docs(scope): ...

chore(scope): ...

test(scope): ...

Examples:

feat(api): add idempotency key support

fix(search): handle empty query safely

docs(runbooks): add incident response

Quality Bar
Tests

All contributions must keep the test suite green.

Run at minimum:

pnpm typecheck
pnpm lint
pnpm test


If you touched cross-component contracts, also run:

pnpm test:contract


If you touched multi-system wiring, also run:

pnpm test:integration

Documentation

Update docs when you change:

API shapes or error models

schemas/contracts

operational behavior (jobs, workers, limits)

runbooks (deploy, backfills, incident response)

Relevant docs live under docs/, services/, and packages/.

Architectural Boundaries

Please respect these boundaries:

The primary database is the source of truth for canonical data

Search is a derived system and must remain rebuildable

Long-running work must be delegated to workers (not request/response paths)

Events are facts (past tense) and must follow the event spec in docs/specs/events.md

Tenant isolation is a first-class security boundary (docs/architecture/multi-tenancy.md)

Security

Do not commit secrets (tokens, API keys, credentials)

Avoid logging sensitive data

Follow least-privilege access patterns

Report security concerns privately (see SECURITY.md)

Security-related changes should include tests and clear documentation.

Pull Request Checklist

Before opening a PR:

 Issue exists (or PR explains why it doesn’t need one)

 Changes are small and focused

 Tests pass locally (typecheck, lint, test)

 Docs updated (if behavior/contracts changed)

 No secrets added

 Observability considered (logs/metrics where relevant)

 Backward compatibility preserved (or clearly documented)

In the PR description, include:

What changed

Why it changed

How to test it

Risks / rollout notes (if any)

Reviews

Reviewers will look for:

correctness and safety

consistency with architecture and specs

test coverage and determinism

operational impact (latency, cost, retries, limits)

documentation completeness

Be responsive to review feedback; treat it as collaboration, not confrontation.

Code Style

Keep code readable and explicit

Prefer small functions/modules over monoliths

Validate inputs at boundaries

Handle errors intentionally (don’t swallow failures)

Keep logs useful and structured

Thanks again — good contributions keep this project fast to build and safe to run.
