# Local Deployment — Narralytica

This environment is used for **local development and testing**.

It allows developers to run the full Narralytica stack on their own machine, including databases, search infrastructure, and background workers.

---

## 🎯 Purpose

The local environment is designed to:

- Develop and test features safely
- Run ingestion and processing pipelines
- Experiment with search and AI enrichment
- Debug API and worker behavior
- Validate migrations and schema changes

It is **not performance-optimized** and does not reflect production scale.

---

## 🧱 Local Stack

The local environment runs using **Docker Compose**.

Services typically included:

| Service | Role |
|--------|------|
| Postgres | Primary database (source of truth) |
| MinIO | Local S3-compatible object storage |
| Qdrant | Vector search database |
| OpenSearch | Lexical search engine |
| Redis | Queue / caching layer (if enabled) |

All data is local to your machine.

---

## 🚀 Starting the Environment

From the project root:

```bash
docker compose up
```

To run in detached mode:

```bash
docker compose up -d
```

To stop:
```bash
docker compose down
```

---

## 🔧 Environment Variables

Configuration is managed via .env files.

See:

.env.example for available variables

Service-specific configs under /infra/docker

Never commit real secrets.

## 🧪 Typical Local Workflow

Start infrastructure with Docker Compose

Run API and workers locally (outside Docker if desired)

Ingest a sample video

Monitor logs and DB state

Test search and API responses

## 📦 Data Persistence

Docker volumes are used for:

Database data

Search indexes

Object storage

To fully reset local state:

bash```
docker compose down -v
```
⚠️ This deletes all local data.

---

## 🛠 Related Docs

Development setup → docs/runbooks/local-dev.md

Database model → docs/architecture/data-model.md

Pipelines → docs/architecture/pipelines.md


---
