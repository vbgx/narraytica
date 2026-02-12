# PHASE 3 — Consolidation Search (single source of behavior) — Milestone REFACTO

Objectif
Avoir une seule implémentation de search (lexical + vector + hybrid + filtres + ranking), consommée par :

services/api (exposition HTTP)

services/workers/indexer (indexation)

et plus tard d’autres workers / produits

À la fin de PHASE 3 : packages/search est le cerveau, services/api n’a plus de “moteur search” interne, et indexer n’a plus de clients OpenSearch/Qdrant maison.

Scope exact

Unifier :

packages/search/* (s’il existe déjà partiellement)

services/api/src/search/* (impl actuelle dispersée)

services/workers/indexer/src/* (clients/opérations d’index)

Verrouiller sémantique (filtres + merge hybrid + ranking) via tests unitaires + golden + e2e.

Issue 3.1 — Définir l’API canonique : SearchEngine.search(SearchQuery) -> SearchResult

Title: refactor(search): define canonical SearchEngine API + core types (contracts-first)
Labels: refactor, search, architecture, contracts
Priority: P0

Objectif

Fixer une signature unique, indépendante FastAPI, indépendante workers, indépendante DB.

Scope exact

Créer/mettre à jour dans packages/search/ :

packages/search/
  engine.py        # SearchEngine
  types.py         # SearchQuery, SearchResult, SearchHit, Facets, etc.
  filters.py       # sémantique filtres + normalisation
  ranking.py       # hybrid merge + rerank + scoring
  errors.py        # erreurs search (pas HTTP)
  README.md        # invariants + règles anti-drift

Décisions structurantes (à écrire noir sur blanc)

SearchQuery et SearchResult doivent être alignés sur JSON Schemas (contracts).

SearchEngine ne lève jamais HTTPException. Il lève des erreurs SearchError (domain/app).

La sémantique des filtres vit uniquement dans packages/search/filters.py.

Steps (checklist)

 Définir SearchQuery / SearchResult (types Python) alignés sur schemas

 Implémenter SearchEngine en mode “ports” (ne connaît pas OpenSearch/Qdrant directement)

 Ajouter packages/search/errors.py (BadQuery, UnsupportedFilter, BackendUnavailable)

 Ajouter tests unitaires “type invariants” (ex: query normalisation stable)

 Ajouter un doc packages/search/README.md :

“Where logic lives”

“Forbidden imports”

“How to add a filter”

DoD

SearchEngine.search() existe, testable sans HTTP

filters.py + ranking.py contiennent le cœur sémantique

Le package n’importe pas de clients OpenSearch/Qdrant (ça vient plus tard via adapters)

Risques & mitigation

Trop de refacto d’un coup
→ commencer par “façade” + délégation temporaire à l’impl existante via ports.

Issue 3.2 — Définir les ports : Lexical / Vector / HybridMerge (contrats d’infrastructure)

Title: refactor(search): define ports for lexical/vector backends + hybrid merge contract
Labels: refactor, search, ports
Priority: P0

Objectif

Isoler le moteur du détail OpenSearch/Qdrant. Le moteur ne voit que des interfaces.

Scope exact

Créer packages/search/ports.py :

LexicalSearchPort.search_lexical(q_normalized) -> LexicalResult

VectorSearchPort.search_vector(q_normalized) -> VectorResult

HybridMergePort.merge(lexical, vector, params) -> SearchResult

(ou merge dans ranking.py direct, mais l’interface reste stable)

Steps

 Définir types intermédiaires (LexicalHit, VectorHit) avec champs minimaux

 Définir limites : top_k, score ranges, pagination semantics

 Documenter les invariants attendus par le merge (ex: ids stables, score monotonic)

 Ajouter tests unitaires sur merge prenant des résultats factices (purs)

DoD

Ports définis + utilisés par SearchEngine

Le merge est testable sans backends

Risques & mitigation

Interfaces trop proches des backends
→ types intermédiaires simples, pas de DSL OpenSearch/Qdrant dans les ports.

Issue 3.3 — Migrer la sémantique des filtres vers packages/search/filters.py (single truth)

Title: refactor(search): migrate filter semantics into packages/search (single source of truth)
Labels: refactor, search, drift
Priority: P0

Objectif

Supprimer le drift “invisible” : un filtre doit avoir un seul sens, partout.

Scope exact

Déplacer depuis services/api/src/domain/search_filters.py (ou équivalent) vers packages/search/filters.py

Normalisation :

ranges (time, duration)

language

speaker filters

topic filters

pagination

multi-lang behavior (si applicable)

Steps

 Déplacer code + tests (golden) de PHASE 2 vers packages/search

 Remplacer dans API : route ou use-case appelle filters.normalize()

 Ajouter validations strictes : filter unknown → BadQuery (pas HTTP)

 Ajouter fixtures query normalisées

DoD

Aucun autre module ne définit l’interprétation des filtres

Golden tests passent et couvrent cas multi-lang + speaker + time window

Risques & mitigation

Breaking change masqué
→ golden tests = “contrat produit”, update snapshot = décision explicite.

Issue 3.4 — Migrer hybrid merge / ranking vers packages/search/ranking.py

Title: refactor(search): migrate hybrid merge + ranking into packages/search/ranking.py
Labels: refactor, search, ranking
Priority: P0

Objectif

Éliminer la duplication services/api/src/search/hybrid/merge.py vs ailleurs.
Le ranking/merge doit être unique, versionné, testable.

Scope exact

Déplacer merge + dedup + tie-breaking + scoring vers packages/search/ranking.py

Steps

 Déplacer l’impl actuelle (si existante) en conservant comportement

 Ajouter tests unitaires + golden sur outputs merge

 Ajouter “stable sort” & “deterministic output” :

mêmes inputs → mêmes outputs (ordre stable)

 Documenter les règles de merge (2–5 bullets) dans README

DoD

packages/search/ranking.py est la seule impl

services/api/src/search/hybrid/merge.py devient wrapper (temp) ou supprimé en fin de phase

Risques & mitigation

Scores non comparables lexical vs vector
→ normaliser/scale + tests de non-régression.

Issue 3.5 — Créer les adapters backends dans packages/search/adapters/* (OpenSearch/Qdrant)

Title: refactor(search): implement opensearch + qdrant adapters in packages/search/adapters
Labels: refactor, search, adapters
Priority: P1 (après 3.1–3.4)

Objectif

Déplacer l’IO backend hors API et hors worker indexer.

Scope exact
packages/search/adapters/
  opensearch.py    # implements LexicalSearchPort
  qdrant.py        # implements VectorSearchPort
  templates/       # index templates/mappings/settings (si applicable)

Steps

 Implémenter OpenSearchAdapter qui respecte LexicalSearchPort

 Implémenter QdrantAdapter qui respecte VectorSearchPort

 Centraliser config (index name, collection, timeouts) via injection (wiring)

 Ajouter tests unitaires sur “query building” (sans appeler un vrai backend)

 Ajouter tests d’intégration optionnels (si CI a OpenSearch/Qdrant)

DoD

L’API et indexer peuvent importer ces adapters

Plus de clients OpenSearch/Qdrant “en direct” dans routes

Risques & mitigation

Config mismatch (index mappings, analyzers)
→ templates versionnés + test “bootstrap idempotent” (voir issue 3.8).

Issue 3.6 — API wiring: services/api consomme uniquement packages/search (plus de moteur interne)

Title: refactor(api): route/search uses packages/search engine via wiring (no api search impl)
Labels: api, search, refactor
Priority: P0

Objectif

services/api ne contient plus aucune logique search métier. Seulement :

validation input

call use-case/engine

mapping output

Steps

 Ajouter services/api/src/wiring/search.py :

instancie adapters OpenSearch/Qdrant

instancie SearchEngine

 Mettre à jour routes/search.py (ou use-case) pour appeler engine injecté

 Supprimer/réduire services/api/src/search/** :

garder seulement wiring transitoire si nécessaire, mais idéalement 0

 Mettre à jour boundaries (PHASE 1) pour interdire services/api/src/search/** métier

DoD

services/api/src/search/** n’existe plus ou ne contient que wiring (temp)

Aucun import de client backend dans routes

Risques & mitigation

Imports résiduels dans tests
→ refactor tests à la fin + CI boundaries.

Issue 3.7 — Worker indexer: consommer les adapters communs (plus de clients locaux)

Title: refactor(workers): indexer uses packages/search adapters (no local opensearch/qdrant clients)
Labels: workers, search, refactor
Priority: P0

Objectif

Le worker indexer ne doit pas posséder son propre accès aux backends search.

Scope exact

Remplacer tout services/workers/indexer/src/opensearch/* / qdrant/* par imports depuis packages/search/adapters/*

Steps

 Identifier fonctions indexation (bulk index, upsert, delete)

 Ajouter au besoin une API “IndexWriter” dans packages/search/adapters/opensearch.py (ou sous-module)

 Remplacer imports dans indexer

 Supprimer code local indexer (à la fin)

 Ajouter boundary CI : worker indexer interdit d’importer clients backend directement

DoD

Indexer n’a plus de code client OpenSearch/Qdrant local

Tests indexer (si présents) passent

Risques & mitigation

Indexing ≠ searching (APIs différentes)
→ autoriser un sous-module adapters/opensearch_index.py dédié, mais toujours dans packages.

Issue 3.8 — Tests: E2E search + bootstrap idempotent + unit tests merge/filters

Title: tests(search): add e2e + idempotent bootstrap + unit coverage (filters/merge/query build)
Labels: tests, search, drift
Priority: P0

Objectif

Verrouiller le comportement et prévenir le drift futur.

Couverture attendue

Unit (purs)

filtres normalisation (golden)

merge/ranking (golden)

query building (sans backend)

Integration/E2E (si CI peut)

/search e2e (déjà existant) doit passer inchangé

bootstrap idempotent :

appliquer templates/mappings deux fois → pas d’erreur, pas de drift

Steps

 Conserver/renforcer test_search_e2e existant

 Ajouter test_search_bootstrap_idempotent (si bootstrap existe)

 Ajouter tests unitaires query builder pour OpenSearch/Qdrant adapters

 Ajouter test “deterministic order” sur merge

DoD

Tous les tests passent en CI

Les golden tests rendent toute évolution de sémantique explicite

Risques & mitigation

CI sans OpenSearch/Qdrant
→ rendre les tests backend “optional” via marker, mais garder unit tests forts.

Définition de Done (PHASE 3)

✅ packages/search contient toute la sémantique (filters + ranking + engine)

✅ services/api consomme SearchEngine via wiring, sans impl search interne

✅ workers/indexer consomme adapters partagés, sans clients backend locaux

✅ tests unit/golden protègent filtres + merge + query building

✅ e2e /search passe inchangé
