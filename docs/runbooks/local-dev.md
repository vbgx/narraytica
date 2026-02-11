# Runbook — Local Development

Purpose

This runbook explains how to set up and run the system in a local development environment.

The goal is to ensure every engineer can:

run the system locally

test features safely

debug issues effectively

work without depending on production systems

Requirements

Before starting, ensure you have:

A supported version of Node.js

The project package manager (e.g., pnpm)

Access to required environment variables

Docker (if the project uses containerized dependencies)

Refer to the root README for version specifics.

Environment Setup

Clone the repository

Install dependencies:

pnpm install


Create a local environment file:

cp .env.example .env


Fill in required environment variables using local or test credentials.

Never use production secrets in local environments.

Running Services

Start the development environment:

pnpm dev


This typically launches:

API server

Background workers (if configured)

Local development tooling (hot reload, etc.)

Some subsystems may require separate commands depending on configuration.

Databases and Search

Local development may require:

A local database instance

A local or containerized search service

If Docker is used:

docker-compose up


Ensure services are healthy before starting the app.

Using Test Data

Use fixtures or seed scripts to populate local data:

pnpm seed


Never import production data into local environments unless fully anonymized.

Running Tests Locally

Before pushing changes, run tests:

pnpm test


For targeted testing:

pnpm test:unit
pnpm test:integration
pnpm test:contract

Debugging Tips

Check service logs in the terminal

Enable debug logging via environment variables

Use local mock services when external dependencies are unavailable

Avoid debugging directly in shared environments.

Common Issues
Issue	Possible Cause
Service won’t start	Missing environment variables
Connection errors	Database/search service not running
Test failures	Out-of-date fixtures or schema changes

Restart services and re-run setup steps when in doubt.

Good Practices

Keep your .env file out of version control

Re-run dependency installation after major changes

Use local feature flags to test incomplete work

Regularly pull the latest changes from main

Goal

A reliable local setup allows engineers to build and test quickly without risk.
If local development is painful, it slows down the entire team — keep this workflow smooth and documented.

End of Local Development Runbook
