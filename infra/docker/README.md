# Local Infrastructure (Docker Compose) — Narralytica

This Docker Compose stack provides the full local infrastructure required to run Narralytica during development.

It allows engineers to start all core services with a single command, without relying on any external systems.

---

## 🚀 Start the Stack

From the repository root:

```bash
docker compose -f infra/docker/docker-compose.yml up -d
docker compose -f infra/docker/docker-compose.yml ps
```

All containers should start and become healthy (or ready) within 1–2 minutes.

## 🛑 Stop the Stack

```bash
docker compose -f infra/docker/docker-compose.yml down
```

## ♻️ Full Reset (Deletes All Local Data)

⚠️ This removes all volumes and stored data (databases, indexes, object storage).

```bash
docker compose -f infra/docker/docker-compose.yml down -v --remove-orphans
docker system prune -a --volumes -f
```

Then start again with:

```bash
docker compose -f infra/docker/docker-compose.yml up -d
```

## 📦 Services Included

| Service    | Purpose                             | URL / Port              |
| ---------- | ----------------------------------- | ----------------------- |
| Postgres   | Primary relational database         | `localhost:5432`        |
| Redis      | Cache / queue backend               | `localhost:6379`        |
| OpenSearch | Full-text and analytics search      | `http://localhost:9200` |
| Qdrant     | Vector database (embeddings search) | `http://localhost:6333` |
| MinIO      | S3-compatible object storage        | `http://localhost:9000` |


## 🔐 Local Credentials

These are development-only credentials.

Postgres

Database: narralytica

User: narralytica

Password: narralytica

Connection string:

```bash
postgresql://narralytica:narralytica@localhost:5432/narralytica
```

## Redis

```bash
redis://localhost:6379
```

## OpenSearch

```bash
http://localhost:9200
```

## Qdrant

```bash
curl -fsS http://localhost:6333/readyz
```

## 🧪 Manual Connectivity Tests

```bash
pg_isready -h localhost -p 5432 -U narralytica
docker exec narralytica-redis redis-cli ping
curl -fsS http://localhost:9200
curl -fsS http://localhost:6333/readyz
curl -fsS http://localhost:9000/minio/health/live
```

## 🧠 Notes for Developers

This stack is for local development only — security settings are relaxed.

Data in volumes is persistent between restarts unless -v is used.

OpenSearch may take longer to boot than other services.

If Docker Desktop has low memory allocation, OpenSearch may fail to start. Increase Docker memory if needed.

---

## 📚 Related Documentation

Architecture Overview → `docs/architecture/overview.md`

Local Dev Runbook → `docs/runbooks/local-dev.md`
