# API Service — Narralytica

The API service is the **primary interface** to the Narralytica platform.

It exposes endpoints for:
- Ingestion
- Data retrieval
- Search
- Speaker analysis
- Job orchestration

All external applications and internal tools interact with Narralytica **exclusively through this API**.

---

## 🎯 Responsibilities

The API service is responsible for:

- Authenticating and authorizing requests
- Validating input/output against platform contracts
- Reading and writing structured data in Postgres
- Querying search infrastructure (vector + lexical)
- Triggering background processing jobs
- Enforcing rate limits and access scopes

It is **not responsible** for heavy AI processing or indexing work — those tasks are handled by workers.

---

## 🧱 Internal Structure

| Folder | Purpose |
|--------|---------|
| `routes/` | HTTP endpoints grouped by domain |
| `domain/` | Business logic and use cases |
| `db/` | Database access layer |
| `storage/` | Object storage client |
| `search/` | Search adapters (Qdrant, OpenSearch) |
| `auth/` | Authentication and authorization logic |
| `telemetry/` | Logging, metrics, tracing integration |
| `settings.py` | Service configuration |
| `main.py` | Application entrypoint |

---

## 🔌 Main Endpoint Categories

| Route Group | Purpose |
|-------------|---------|
| `/ingest` | Submit new videos for processing |
| `/videos` | Retrieve video metadata |
| `/transcripts` | Access transcript data |
| `/segments` | Query timecoded segments |
| `/speakers` | Access speaker information |
| `/search` | Perform semantic or hybrid search |
| `/jobs` | Monitor and manage processing jobs |

---

## 🔐 Security Model

The API enforces:

- API key authentication
- Scope-based authorization
- Rate limits
- Input validation against contracts

See:
- `docs/specs/permissions.md`
- `docs/specs/rate-limits.md`

---

## 🔄 Relationship with Workers

The API does **not** process media or run AI models directly.

Instead, it:
1. Creates job records
2. Publishes tasks to the job queue
3. Returns job status to clients

Workers consume those jobs and update the database when processing is complete.

---

## 🧪 Local Development

The API can run locally alongside Docker infrastructure.

Typical flow:
1. Start infra via Docker Compose
2. Run API service locally
3. Test endpoints with sample requests

See:
`docs/runbooks/local-dev.md`

---

## 📚 Related Documentation

- API design → `docs/architecture/api.md`
- Data model → `docs/architecture/data-model.md`
- Search architecture → `docs/architecture/search.md`
- Contracts → `packages/contracts`
