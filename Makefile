
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

.PHONY: help install install-py install-node lint lint-py lint-node format format-py format-node

help:
	@echo "Targets:"
	@echo "  make install      Install Python + Node deps"
	@echo "  make lint         Run all linters"
	@echo "  make format       Run all formatters"

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
