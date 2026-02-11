# ----------------------------
# Docs quality
# ----------------------------
.PHONY: docs-lint docs-links docs-check

docs-lint:
	pnpm -s markdownlint-cli2 "**/*.md"

docs-links:
	node tools/scripts/docs-link-check.mjs

docs-check: docs-lint docs-links
	@echo "✅ docs-check OK"


# ----------------------------
# Tooling
# ----------------------------
.PHONY: help install install-py install-node lint lint-py lint-node format format-py format-node

help:
	@echo "Targets:"
	@echo "  make install      Install Python + Node deps"
	@echo "  make lint         Run all linters"
	@echo "  make format       Run all formatters"
	@echo "  make migrate      Run DB migrations (services/api)"
	@echo "  make db-up        Start Postgres only (Docker)"
	@echo "  make db-down      Stop Postgres and remove volumes (Docker)"

install: install-py install-node

install-py:
	uv sync

install-node:
	pnpm install

lint: lint-py lint-node

lint-py:
	uv run ruff check .

lint-node:
	pnpm -r lint || true

format: format-py format-node

format-py:
	uv run ruff check . --fix
	uv run black .

format-node:
	pnpm -r format || true


# ----------------------------
# Database (Docker + Alembic)
# ----------------------------
DB_URL ?= postgresql+psycopg://narralytica:narralytica@127.0.0.1:15432/narralytica
COMPOSE ?= docker compose -f infra/docker/docker-compose.yml

.PHONY: db-up db-down db-psql

db-up:
	$(COMPOSE) up -d postgres

db-down:
	$(COMPOSE) down -v

db-psql:
	psql "postgresql://narralytica:narralytica@127.0.0.1:15432/narralytica"

.PHONY: migrate
migrate:
	sh -lc 'uv sync --project services/api && API_DATABASE_URL=$(DB_URL) uv run --project services/api alembic -c services/api/alembic.ini upgrade head'

# ----------------------------
# OpenSearch (bootstrap)
# ----------------------------
.PHONY: opensearch-bootstrap
opensearch-bootstrap:
	OPENSEARCH_URL=$${OPENSEARCH_URL:-http://localhost:9200} \
	bash infra/opensearch/scripts/bootstrap.sh
