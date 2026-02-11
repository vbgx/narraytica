# Qdrant — Narralytica

This folder defines **local bootstrap** for Qdrant collections used by Narralytica.

## Naming conventions

- Collections are versioned: `narralytica-<domain>-v<NN>`
  - Example: `narralytica-segments-v1`

## Files

- `collections/*.collection.json` — collection creation payloads (source of truth)
- `scripts/bootstrap.sh` — idempotent bootstrap (create if missing)
- `scripts/healthcheck.sh` — readiness + collection existence check

## Local usage

Start Qdrant (via docker compose):

```bash
docker compose -f infra/docker/docker-compose.yml up -d qdrant
```

Bootstrap collections:

```bash
QDRANT_URL=http://localhost:6333 bash infra/qdrant/scripts/bootstrap.sh
```

Healthcheck:

```bash
QDRANT_URL=http://localhost:6333 bash infra/qdrant/scripts/healthcheck.sh
```

---

## Makefile target

Ajoute ce bloc **une seule fois** dans ton Makefile (section “Search bootstrap” ou “Infra bootstrap” comme tu veux) :

```bash
cat >> Makefile << 'EOF'

# ----------------------------
# Qdrant bootstrap
# ----------------------------
.PHONY: qdrant-bootstrap
qdrant-bootstrap:
	QDRANT_URL=$${QDRANT_URL:-http://localhost:6333} \
		bash infra/qdrant/scripts/bootstrap.sh
