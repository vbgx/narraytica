# OpenSearch Indexing — Naming & Bootstrap (EPIC 00 / 00.07)

## Goals
- Versioned, reproducible index templates
- Predictable index naming for future reindexing
- Bootstrap on API startup for local/dev parity

## Naming conventions

### Templates
- `narralytica-videos-template`
- Pattern: `narralytica-videos-*`

### Indices
- Current: `narralytica-videos-v1`
- Future reindex: `narralytica-videos-v2`, then aliasing will be introduced in a later EPIC.

## Bootstrap behavior
On API startup:
1. `PUT /_index_template/{template_name}` from repo JSON
2. `PUT /{index}` if missing

Bootstrap is controlled by:
- `OPENSEARCH_BOOTSTRAP_ENABLED=true|false`

## Verify
- Template:
  - `curl -fsS http://localhost:9200/_index_template/narralytica-videos-template | jq`
- Index exists:
  - `curl -fsS http://localhost:9200/_cat/indices?v | grep narralytica-videos-v1`
- Mapping:
  - `curl -fsS http://localhost:9200/narralytica-videos-v1/_mapping | jq`
