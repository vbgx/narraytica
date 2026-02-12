# PHASE 5 — AI layers standardisation (enrich worker) — Milestone REFACTO

Objectif
Centraliser et standardiser les “couches IA” (embeddings/topics/sentiment/stance/cefr/summaries/key_moments/…) pour que :

la logique vive dans packages/ai_layers (cerveau),

les workers soient uniquement des moteurs (runtime, retries, orchestration, persistance),

chaque layer soit plug-in, pure, testable, contract-first,

la production de layer soit traçable (provenance, versions, hashes) et donc anti-drift.

Scope exact

Migrer services/workers/enrich/src/layers/* → packages/ai_layers/layers/*

Introduire LayerComputer + registry

Extraire les providers (LLM/embeddings) derrière des ports

Standardiser LayerResult (enveloppe + provenance) via JSON Schemas

Ajouter tests unitaires + contract + 1 integration “enrich flow” minimal

Principe

packages/ai_layers ne connaît ni HTTP, ni DB, ni worker runtime

les providers = adapters (IO) injectés depuis services/workers/enrich/wiring.py

LayerResult = contrat immuable (source of truth)

Issue 5.1 — Contracts: définir le LayerResult canonique + provenance (contract-first)

Title: contracts(ai_layers): define canonical LayerResult envelope + provenance (layer.schema.json)
Labels: contracts, ai_layers, drift, refactor
Priority: P0

Objectif

Supprimer le drift de format : tous les layers doivent produire une enveloppe standard validable.

Scope exact

Créer/mettre à jour : packages/contracts/schemas/layers/layer_result.schema.json (ou layer.schema.json)

Ajouter schémas payload par layer (optionnel v0) ou oneOf (progressif)

Champs minimaux (v0, stricts)

layer_name (string, idéalement enum)

layer_version (string)

status (success|skipped|failed)

input_ref :

video_id / transcript_id (selon ton modèle)

segment_ids (optionnel)

input_hash (string, obligatoire)

provenance :

computed_at (iso datetime)

model_provider (string)

model_id (string)

params_hash (string)

worker_name (string)

worker_version (string)

payload (object, permissif v0, strictifié layer-by-layer)

errors (liste structurée si failed)

Steps

 Écrire/mettre à jour le schema layer_result

 Ajouter 2 fixtures :

tests/fixtures/contracts/layer_result.success.json

tests/fixtures/contracts/layer_result.failed.json

 Ajouter tests/contract/test_layer_result_schema.py

 Ajouter règle CI “no layer payloads ad-hoc” (au moins : tout résultat persistant doit valider le schema)

DoD

Tous les résultats de layer (au moins ceux testés) valident layer_result.schema.json

Le schema impose provenance + hashes (pas optionnels)

Risques & mitigation

Payload trop libre au début
→ OK en v0, mais l’enveloppe est strictement stable (c’est ce qui empêche le drift).

Issue 5.2 — Introduire LayerComputer (interface) + registry (plugin system)

Title: refactor(ai_layers): add LayerComputer interface + registry (plugin execution)
Labels: ai_layers, architecture, refactor
Priority: P0

Objectif

Standardiser l’exécution : le worker enrich ne connaît pas l’impl, il appelle un registry.

Scope exact (structure)
packages/ai_layers/
  README.md
  base.py          # LayerComputer (Protocol / ABC)
  registry.py      # register/list/resolve
  types.py         # LayerName, LayerInput, LayerContext, LayerResult
  common/
    hashing.py     # input_hash / params_hash
    normalize.py   # helpers texte (si nécessaire)
  layers/          # impls layer-by-layer

Règles

LayerComputer.compute() est pure (elle peut appeler des ports, mais pas DB/HTTP)

LayerContext contient :

ports (LLMPort/EmbeddingsPort)

clock

correlation (ids)

params (layer config)

Aucune persistance ici. Persistance = worker.

Steps

 Implémenter LayerComputer + LayerResult (types)

 Implémenter registry :

register(layer_name, computer)

get(layer_name)

list()

 Ajouter tests unitaires :

registry resolves

compute returns LayerResult shape (sans provider)

 Documenter “How to add a layer” dans README

DoD

Registry fonctionne et est testable

Interface stable (utilisée au moins par 1 layer stub)

Risques & mitigation

Over-engineering
→ registry minimal (un dict), pas de discovery magique.

Issue 5.3 — Définir les ports IA (LLM / Embeddings) + mocks déterministes

Title: refactor(ai_layers): define ai ports (LLMPort/EmbeddingsPort) + deterministic mocks for tests
Labels: ai_layers, ports, tests, refactor
Priority: P0

Objectif

Rendre les layers testables sans provider réel, et empêcher les imports SDK dans packages/ai_layers.

Scope exact

Définir dans packages/application/ports/ai_ports.py (ou dans packages/ai_layers/types.py si tu préfères localiser) :

LLMPort.complete(prompt, params) -> LLMResponse

EmbeddingsPort.embed(texts, params) -> vectors

Fournir FakeLLMPort / FakeEmbeddingsPort pour unit tests

Steps

 Définir ports + types réponses

 Créer mocks déterministes (seed fixed)

 Ajouter règle CI boundary :

interdire imports openai, google, anthropic, etc. dans packages/ai_layers/**

 Ajouter unit tests qui valident que layers tournent avec fakes

DoD

Un layer peut être exécuté en unit test avec Fake ports, output stable

packages/ai_layers ne dépend d’aucun SDK provider

Risques & mitigation

Différences async/sync
→ décider style d’appel (souvent async en enrich) et fournir wrapper explicite si nécessaire.

Issue 5.4 — Migrer 2 layers “faibles dépendances” vers packages/ai_layers (proof)

Title: refactor(ai_layers): migrate summaries + sentiment to packages/ai_layers (contract + unit tests)
Labels: ai_layers, refactor, tests
Priority: P0

Objectif

Faire la preuve du modèle (registry + ports + envelope) sur des layers simples.

Scope exact

Migrer summaries et sentiment (ordre conseillé) depuis services/workers/enrich/src/layers/*

Steps (pour chaque layer)

 Créer packages/ai_layers/layers/<layer>.py impl LayerComputer

 Ajouter normalisation d’input (si nécessaire) + input_hash

 Produire LayerResult conforme schema (provenance + params_hash)

 Ajouter unit tests (avec FakeLLMPort)

 Ajouter contract test fixture “layer_result + payload minimal” (si payload schema existe)

 Dans worker enrich : remplacer ancienne exécution par appel registry

DoD

summaries et sentiment :

sont exécutés via registry

produisent un LayerResult validable

ont unit tests + contract tests

Le worker enrich ne contient plus de logique cœur pour ces layers

Risques & mitigation

Divergence output (format texte, scores)
→ golden test “payload stable shape”, pas forcément le texte exact au début.

Issue 5.5 — Migrer le reste layer-by-layer (topics, cefr, key_moments, stance, embeddings)

Title: refactor(ai_layers): migrate remaining layers to packages/ai_layers (topics/cefr/key_moments/stance/embeddings)
Labels: ai_layers, refactor
Priority: P1 (après proof)

Objectif

Finir la centralisation sans big bang.

Ordre recommandé

topics

cefr

key_moments

stance

embeddings (souvent plus couplé à l’infra)

Steps (pattern identique)

 Impl layer computer dans packages/ai_layers/layers/

 Ajouter unit tests fakes + golden minimal

 Ajouter contract fixtures

 Remplacer worker impl par registry

 Déprécier puis supprimer legacy modules dans worker

DoD

Tous les layers existants sont exécutables via registry

Legacy services/workers/enrich/src/layers/* n’est plus qu’un wrapper (ou supprimé)

Risques & mitigation

Explosion combinatoire params/providers
→ “default provider” unique par type + params hash. Le multi-provider viendra plus tard.

Issue 5.6 — Standardiser le wrapper d’exécution côté worker (idempotence + retries + persistence)

Title: refactor(workers): standardize enrich execution wrapper (idempotence/retries/persist LayerResult)
Labels: workers, reliability, ai_layers, refactor
Priority: P0 (sinon drift runtime)

Objectif

Le worker enrich devient un runtime propre :

calcule hashes (input/params)

check existence (idempotence)

exécute via registry

persiste résultat (DB)

gère retry/backoff selon erreur “retryable”

Scope exact

services/workers/enrich/src/worker.py (ou équivalent) :

run_layer(layer_name, input_ref, ctx) wrapper unique

Stockage des LayerResults via repos persistence (PHASE 4)

Steps

 Définir règle d’idempotence :

clé = (layer_name, layer_version, input_hash, params_hash)

 Vérifier existence avant compute (skip si déjà présent)

 Taxonomie d’erreurs :

RetryableProviderError, FatalProviderError, BadInputError

 Persister LayerResult même en failure (status failed + errors)

 Ajouter integration test “re-run idempotent” (même input → pas de duplication)

DoD

Re-run sur même input ne recalcul pas (ou le fait explicitement via version bump)

Un failure produit un LayerResult failed conforme schema

Logs/obs incluent correlation ids + layer_name + status (PHASE 6 friendly)

Risques & mitigation

Input hash mal défini
→ normalisation stricte (tri segments, normalise texte) + tests.

Issue 5.7 — Tests: contract + unit + 1 integration “enrich flow”

Title: tests(ai_layers): add unit + contract coverage and enrich-flow integration test
Labels: tests, ai_layers, contracts
Priority: P0

Objectif

Empêcher la réintroduction du drift.

Couverture minimale exigée

Unit tests pour chaque layer (avec Fake ports)

Contract tests LayerResult + au moins 1 payload par layer

1 test d’intégration enrich-flow :

simule 1 transcript + run 1–2 layers + persiste LayerResult

Steps

 Ajouter tests/unit/ai_layers/* (par layer)

 Ajouter tests/contract/test_layer_result_schema.py (déjà issue 5.1) + fixtures

 Ajouter tests/integration/test_enrich_flow_minimal.py

 Ajouter un “golden payload” minimal pour 1–2 layers

DoD

Toute modification de format casse un test contract

Toute modification sémantique importante casse golden/unit

Risques & mitigation

Tests fragiles (texte généré)
→ tester la structure + champs sémantiques, pas le contenu exact de phrases.

Issue 5.8 — CI boundaries: interdiction SDK providers dans packages/ai_layers + suppression legacy

Title: ci(ai_layers): forbid provider SDK imports in packages/ai_layers and remove legacy worker layer code
Labels: ci, ai_layers, drift
Priority: P0 (clôture phase)

Objectif

Verrouiller : aucune fuite provider dans le cerveau, et le worker ne redevient pas “le cerveau”.

Steps

 Ajouter règles dependency-boundaries :

denylist openai|anthropic|google|vertex|qdrant_client|opensearch dans packages/ai_layers/**

 Interdire création de nouveaux fichiers services/workers/enrich/src/layers/*

 Supprimer legacy modules migrés

DoD

CI échoue si un SDK provider est importé dans ai_layers

services/workers/enrich/src/layers/* est vide/supprimé (ou strictement wrappers transitoires, puis PHASE 7)

Définition de Done (PHASE 5)

✅ packages/ai_layers contient LayerComputer + registry + layers

✅ Chaque layer produit un LayerResult contract-first (schema + provenance + hashes)

✅ Providers extraits derrière ports + fakes pour tests

✅ Worker enrich = runtime (idempotence/retries/persist), plus de logique IA cœur

✅ Unit + contract + integration test minimal couvrent le système

✅ CI boundaries empêchent tout retour du drift
