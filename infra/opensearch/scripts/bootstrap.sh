#!/usr/bin/env bash
set -euo pipefail

OPENSEARCH_URL="${OPENSEARCH_URL:-http://localhost:9200}"

TEMPLATE_NAME="narralytica-videos-v1"
INDEX_NAME="narralytica-videos-v1"
ALIAS_NAME="narralytica-videos"

TEMPLATE_FILE="infra/opensearch/templates/narralytica-videos-v1.template.json"

echo "[opensearch] url=${OPENSEARCH_URL}"

echo "[opensearch] wait for cluster..."
for i in {1..60}; do
  if curl -fsS "${OPENSEARCH_URL}/_cluster/health" >/dev/null; then
    break
  fi
  sleep 1
done

echo "[opensearch] install template: ${TEMPLATE_NAME}"
curl -fsS -X PUT \
  "${OPENSEARCH_URL}/_index_template/${TEMPLATE_NAME}" \
  -H "Content-Type: application/json" \
  --data-binary @"${TEMPLATE_FILE}" \
  >/dev/null
echo "[opensearch] template installed via _index_template"

curl -fsS "${OPENSEARCH_URL}/_index_template/${TEMPLATE_NAME}" >/dev/null
echo "[opensearch] template verify OK"

# Quiet "exists" check: do NOT print curl errors when 404 is expected
if curl -sS -o /dev/null -w "%{http_code}" "${OPENSEARCH_URL}/${INDEX_NAME}" | grep -q "^200$"; then
  echo "[opensearch] index exists: ${INDEX_NAME}"
else
  echo "[opensearch] create index: ${INDEX_NAME}"
  curl -fsS -X PUT "${OPENSEARCH_URL}/${INDEX_NAME}" >/dev/null
fi

echo "[opensearch] ensure alias: ${ALIAS_NAME} -> ${INDEX_NAME}"
curl -fsS -X POST \
  "${OPENSEARCH_URL}/_aliases" \
  -H "Content-Type: application/json" \
  --data-binary @- >/dev/null <<JSON
{
  "actions": [
    { "add": { "index": "${INDEX_NAME}", "alias": "${ALIAS_NAME}" } }
  ]
}
JSON

echo "[opensearch] done ✅"
