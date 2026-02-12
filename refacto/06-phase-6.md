# PHASE 6 — Observability unifiée (API + workers) — Milestone REFACTO

Objectif
Garantir une corrélation stable et exploitable sur tout le système :

request_id (API) → job_id → job_run_id → layer_name → erreurs/retries/latences

Et empêcher le drift d’observabilité (noms d’events divergents, payloads ad-hoc, logs non corrélables) via :

contracts-first (schemas d’events)

façade unique packages/observability (un seul point d’émission)

propagation de contexte (request/worker)

tests (contract + smoke)

Scope exact

Consolider packages/observability/* et l’existant services/api/src/telemetry/*

Standardiser instrumentation dans :

services/api/src/**

services/workers/**/src/**

Introduire des contrats :

correlation ids

event envelope

events principaux (job/job_run/layer/search)

Principe

Baseline = logs JSON structurés (OTEL optionnel)

Aucun service n’émet d’events “libres” : tout passe par obs.emit().

Issue 6.1 — Contracts: correlation ids + event envelope (source of truth)

Title: contracts(observability): define correlation + event envelope schemas (strict)
Labels: contracts, observability, drift, refactor
Priority: P0

Objectif

Figer les champs indispensables pour tracer un flow, indépendamment du sink (logs, OTEL, etc.).

Scope exact

Ajouter/mettre à jour dans packages/contracts/schemas/observability/ :

correlation.schema.json

request_id (uuid)

job_id (uuid, nullable/optional selon contexte)

job_run_id (uuid, nullable/optional)

trace_id (string, optional)

span_id (string, optional)

event_envelope.schema.json

event_name (string, pattern ou enum)

occurred_at (iso datetime)

correlation (ref correlation.schema.json)

actor :

service_name

service_version

env

host (optional)

payload (object, permissif v0)

severity (debug|info|warn|error) (optionnel mais utile)

schema_version (string) (recommandé)

Naming convention (à documenter)

Pattern recommandé :

narralytica.<area>.<action>.<status>
Exemples :

narralytica.search.executed

narralytica.job.created

narralytica.job_run.started

narralytica.layer.completed

Steps

 Créer correlation.schema.json

 Créer event_envelope.schema.json

 Ajouter fixtures :

tests/fixtures/contracts/event_envelope.search_executed.json

tests/fixtures/contracts/event_envelope.layer_failed.json

 Ajouter tests/contract/test_event_envelope_schema.py

DoD

Deux exemples d’events valident le schema

Les champs de corrélation sont normalisés (mêmes noms partout)

Risques & mitigation

Trop strict sur payload
→ v0 permissif sur payload, strict sur envelope/correlation.

Issue 6.2 — Contracts: définir les events “core” (job/job_run/layer/search)

Title: contracts(observability): define core event payload schemas (job/job_run/layer/search)
Labels: contracts, observability, drift
Priority: P1 (mais recommandé avant migration complète)

Objectif

Empêcher les payloads ad-hoc pour les événements critiques.

Scope exact

Ajouter schémas payload (un par event ou regroupés) :

job_created.payload.schema.json

job_started.payload.schema.json

job_failed.payload.schema.json

job_run_started.payload.schema.json

job_run_failed.payload.schema.json

layer_started.payload.schema.json

layer_completed.payload.schema.json

layer_failed.payload.schema.json

search_executed.payload.schema.json

Champs minimaux par famille :

Search executed

mode (lexical|vector|hybrid)

filters (optionnel, mais attention PII)

results_count

latency_ms

backend_latency_ms (optionnel)

index/collection (optionnel)

Layer completed/failed

layer_name

layer_version

status

latency_ms

model_provider, model_id

tokens_in/tokens_out (si dispo, sinon optional)

error_type/error_message (si failed, message court)

Job/JobRun

job_type

status

attempt

latency_ms

error_type (si failed)

Steps

 Écrire schémas payload

 Mettre à jour event_envelope.schema.json pour référencer oneOf (optionnel) :

soit via event_name→payload mapping,

soit validation “payload permissif” + validation forte dans helpers (acceptable v0)

 Ajouter tests contract sur 2–3 payloads clés

DoD

Au moins : search_executed + layer_completed + job_run_failed payloads validables

Risques & mitigation

Trop de schémas
→ commencer par 3 events les plus critiques, étendre ensuite.

Issue 6.3 — Package façade: packages/observability devient l’unique API (obs.emit, ObsContext)

Title: refactor(observability): implement obs.emit facade + ObsContext (logging sink baseline)
Labels: observability, architecture, refactor
Priority: P0

Objectif

Unifier l’émission, la validation, et la propagation de corrélation.

Structure cible
packages/observability/
  README.md
  context.py          # ObsContext + correlation ids
  emit.py             # emit(event_name, payload, ctx)
  events.py           # helpers typed (constructors)
  validate.py         # validate against contracts (toggle strict)
  sinks/
    logging_sink.py   # JSON logs baseline
    otel_sink.py      # optionnel

Comportement attendu

ObsContext contient :

correlation (request_id/job_id/job_run_id/trace_id/span_id)

actor (service_name, version, env)

emit() :

construit envelope

valide (strict en CI, best-effort en prod)

envoie au sink (logging au minimum)

Steps

 Impl ObsContext + helpers with_request_id(), with_job_run()

 Impl emit(event_name, payload, ctx, severity=...)

 Impl logging_sink (stdout JSON)

 Impl validate.py (jsonschema)

 Ajouter tests unitaires :

envelope fields present

validation passes on fixtures

DoD

Un service peut émettre un event en 1 ligne

Les events sortants valident event_envelope.schema.json

Risques & mitigation

Validation runtime coûteuse
→ flag OBS_VALIDATE_STRICT=true en CI, false en prod.

Issue 6.4 — API: propagation request_id + instrumentation des routes clés

Title: refactor(api): add request context middleware + emit search/job events via packages/observability
Labels: api, observability, refactor
Priority: P0

Objectif

Chaque requête HTTP est corrélée, et l’API n’a plus de telemetry “maison”.

Scope exact

services/api/src/middleware/request_context.py

services/api/src/wiring/observability.py

Routes : /search, /jobs, /ingest (au minimum)

Steps

 Middleware :

lit X-Request-Id (si présent) sinon génère UUID

stocke ObsContext sur request state

renvoie X-Request-Id en header response

 Instrumenter /search :

narralytica.search.executed (mode, latency, count)

 Instrumenter /jobs (création/statut) :

job.created, job.status_viewed (optionnel), job.failed (si applicable)

 Remplacer services/api/src/telemetry/* par appels packages/observability

 Supprimer/laisser wiring-only telemetry/* (puis PHASE 7 delete)

DoD

Toute réponse API inclut X-Request-Id

L’API émet au moins search.executed et job.created via obs.emit

Plus de logique telemetry duplicative dans API (enforced via boundaries)

Risques & mitigation

PII leak (query text, transcript)
→ payload doit être minimal, pas de texte brut; hash ou compteurs.

Issue 6.5 — Workers: standardiser job_id/job_run_id + events runtime + layer events enrich

Title: refactor(workers): emit job_run + layer lifecycle events with stable correlation ids
Labels: workers, observability, refactor
Priority: P0

Objectif

Chaque exécution worker est traçable et comparable.

Scope exact

Workers concernés (au minimum) :

ingest, transcribe, diarize, enrich, indexer

Standard lifecycle

Au start :

job_run.started (job_id, job_run_id, attempt)

Pendant :

pour enrich : layer.started / layer.completed / layer.failed

À la fin :

job_run.completed ou job_run.failed

Steps

 Créer un helper runtime côté workers (ou dans packages/observability) :

start_job_run(ctx, job_run_id, job_id, attempt)

end_job_run_success/failure(...)

 Enrich worker :

autour de chaque layer, émettre events avec latency_ms + model_id

 Indexer :

index.sync.started/completed (optionnel mais utile)

 Standardiser “attempt” :

attempt number dans payload partout

DoD

Un même job_id est visible dans logs sur ingest/transcribe/enrich

Chaque layer enrich produit des events corrélés au job_run_id

Risques & mitigation

Workers n’ont pas request_id
→ OK : request_id est optionnel; job_id/job_run_id est le pivot côté workers.

Issue 6.6 — Tests: contract validation + smoke e2e correlation

Title: tests(observability): add contract tests + smoke correlation test across api/workers
Labels: tests, observability, contracts
Priority: P0

Objectif

Empêcher le drift futur : si quelqu’un change un event ou oublie la corrélation, CI casse.

Scope exact

Unit tests (packages/observability)

emit produit envelope conforme

validation strict mode

Contract tests (schemas)

fixtures validées

Smoke test “correlation”

Simuler un flow minimal (sans vrais backends) :

API génère request_id

worker émet job_run.started avec job_id

enrich émet layer.completed

Vérifier présence champs corrélation

Steps

 Ajouter tests/contract/test_event_envelope_schema.py (issue 6.1)

 Ajouter tests/unit/test_observability_emit.py

 Ajouter tests/integration/test_observability_correlation_smoke.py

 Ajouter mode CI OBS_VALIDATE_STRICT=true

DoD

CI casse si event envelope invalide

CI casse si request_id absent dans API responses

CI casse si job_run events manquent job_run_id

Risques & mitigation

Dépendance à OTEL
→ aucun test ne dépend d’OTEL; baseline = logs JSON.

Issue 6.7 — CI boundaries: interdire telemetry locale + imposer packages/observability

Title: ci(architecture): enforce single observability surface (no local telemetry implementations)
Labels: ci, architecture, observability, drift
Priority: P0 (clôture phase)

Objectif

Empêcher que l’API ou un worker réintroduise une instrumentation “maison”.

Steps

 Boundary rule :

interdire nouveaux modules sous services/api/src/telemetry/* (ou les interdire totalement)

interdire imports directs OTEL/logging formatters “custom” (selon choix) hors packages/observability

 Ajouter check “no emit duplicates” :

ex: si un module définit un emit_event() local, CI fail (pattern)

 Retirer allowlist liée à observability (tend vers 0)

DoD

packages/observability est l’unique façade

CI empêche toute duplication future

Risques & mitigation

Cas particuliers (metrics spécifiques)
→ autoriser “sinks” additionnels dans packages/observability seulement.

Définition de Done (PHASE 6)

✅ Contrats observability en place : correlation + envelope (+ core payloads au moins pour search/layer/job_run)

✅ packages/observability fournit ObsContext + emit() + sink logs JSON

✅ API : X-Request-Id propagé + events search.executed / job.created émis via façade

✅ Workers : job_run.started/completed/failed + enrich layer.* émis avec job_run_id

✅ Tests contract + smoke empêchent tout drift

✅ CI boundaries interdisent telemetry locale
