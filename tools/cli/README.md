CLI Tools

This directory contains command-line utilities used to operate, maintain, and support the platform locally and in controlled environments.

These tools are internal engineering utilities and are not part of the public API surface.

Purpose

The CLI layer exists to:

Run operational and maintenance tasks

Trigger data pipelines and backfills

Execute administrative workflows

Support local development and debugging

Provide repeatable scripts for CI and internal operations

All commands should be deterministic, scriptable, and environment-aware.

Design Principles

CLI tools in this project should follow these principles:

1. Safety First

Commands must avoid destructive actions by default.
Potentially dangerous operations should require:

explicit flags (e.g. --force)

confirmation prompts (unless running in CI)

2. Idempotency

Running a command multiple times should not corrupt state or produce inconsistent results.

3. Observability

Each command should:

log meaningful progress

output structured logs when possible

exit with proper exit codes

4. Environment Awareness

Commands must respect environment configuration:

.env files

environment variables

local vs staging vs production safeguards

Typical Command Categories
Category	Description
data	Backfills, migrations, re-indexing, dataset validation
search	Index rebuilds, shard maintenance, reranking experiments
db	Schema checks, seed data, integrity verification
ops	Maintenance tasks, cleanup jobs, cost control utilities
debug	Local inspection tools and diagnostics
Usage Pattern

CLI tools are typically run through the package manager:

pnpm cli <command> [options]


Or directly via node:

node tools/cli/src/index.ts <command>


(Exact entrypoints depend on project configuration.)

Output Conventions

All CLI tools should:

Use clear, human-readable logs for local runs

Support a --json flag for machine-readable output

Exit with:

0 on success

non-zero on failure

Adding a New CLI Command

When introducing a new command:

Place logic in a dedicated module (avoid monolithic scripts)

Add input validation

Add logging and error handling

Document the command in this README (or a subpage if complex)

Ensure it can run safely in local and CI environments

Not for End Users

These tools are intended for engineers and operators, not end users.
User-facing automation should be exposed through the API or application interfaces instead of the CLI.

This CLI layer is part of the operational backbone of the project — keep it reliable, predictable, and safe.
