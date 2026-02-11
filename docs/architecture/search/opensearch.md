# OpenSearch — Index Naming & Templates (Local Dev)

## Naming convention

We version indexes explicitly:

- Physical index: `narralytica-<domain>-v<version>`
  - Example: `narralytica-videos-v1`

We keep a stable alias for reads/writes:

- Alias: `narralytica-<domain>`
  - Example: `narralytica-videos`

This allows safe reindex + cutover:
- create `...-v2`
- backfill
- switch alias to `...-v2`

## Templates

Templates live in:
- `infra/opensearch/templates/*.template.json`

They are applied via `_index_template`.

## Bootstrap (local)

Start OpenSearch via Docker Compose, then:

- `make opensearch-bootstrap`

This will:
- PUT the template
- create the index if missing
- ensure the alias exists

## Verify

- `curl -fsS http://localhost:9200/_cat/indices?v`
- `curl -fsS http://localhost:9200/_index_template/narralytica-videos-v1 | jq .`
- `curl -fsS http://localhost:9200/_alias/narralytica-videos | jq .`
