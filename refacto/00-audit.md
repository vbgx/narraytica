# 🧠 Narralytica — Architecture Refactor Plan

---

# 🟢 Executive Summary (≤10 lignes)

Narralytica possède déjà une base solide : JSON Schemas (contracts), API FastAPI, workers, tests et infrastructure.

Cependant, l’architecture risque de diverger car les responsabilités **domain / application / adapters** ne sont pas strictement encodées dans les dépendances et l’organisation des dossiers.

Les symptômes apparaissent déjà :
- Domain partiellement implémenté dans l’API
- Logique search répartie entre `packages/search` et `services/api/src/search`
- Accès DB/infra répliqués dans plusieurs workers

La cible recommandée est une architecture **Clean / Hexagonale** :
- `packages/contracts` comme source de vérité
- `packages/domain` minimal et stable
- `packages/application` (use-cases)
- `packages/adapters/*` (persistence / search / ai / observability)

Le refactor doit être progressif via un milestone **“REFACTO”** :
1. Règles de dépendances + tests anti-drift
2. Extraction des use-cases
3. Consolidation des adapters
Sans “big bang”.

---

# 🔎 Audit Findings

## Zones typiques de drift

### 1️⃣ Logique métier dans les routes
- Validation / autorisation
- Orchestration
- Mapping DB
- Règles de tri / filtres
- Ranking

### 2️⃣ Duplication de contracts
- Modèles Pydantic proches mais divergents des JSON Schemas
- Schémas copiés dans plusieurs services

### 3️⃣ Adapters infra dans le Domain
- Imports OpenSearch / Qdrant / Postgres
- Dépendances runtime dans le domain

### 4️⃣ Workers qui réinventent l’application
- Mini-domain propre à chaque worker
- Logique retry locale
- Règles spécifiques non mutualisées

### 5️⃣ Search éclaté
Logique lexical/vector/hybrid répartie entre :
- API
- Packages
- Workers

---

# ⚠️ Risques

## 🔴 R1 — Drift de contrats (Critique)
**Symptômes**
- Champs divergents tolérés
- Changements non détectés en CI

## 🔴 R2 — API devient le cœur applicatif (Critique)
**Symptômes**
- Orchestration métier dans routes
- Accès DB direct
- Logique scoring/ranking embarquée

## 🟠 R3 — Duplication persistence/search (Élevée)
- Clients OpenSearch/Qdrant multiples
- Ranking divergent
- Config dispersée

## 🟠 R4 — Couplage runtime ↔ logique (Élevée)
- Tests nécessitent infra réelle
- CI fragile

## 🟠 R5 — Incohérence Search (Élevée)
- Filtres interprétés différemment
- Hybrid merge non unifié

## 🟡 R6 — Observabilité non standardisée (Moyenne)
- Logs non corrélables
- Request IDs incohérents

---

# 🏗 Target Architecture

## Flux cible

contracts
↓
domain
↓
application
↓
adapters
↓
api / workers

---

# 🛠 Refactor Plan — Milestone “REFACTO”

## PHASE 1 — Guardrails
- Dependency boundary check
- Tests contract étendus
- Détection duplication schema

## PHASE 2 — Extraction Use-cases
- Sortir orchestration hors routes
- Routes = glue uniquement

## PHASE 3 — Consolidation Search
- Implémentation unique lexical/vector/hybrid

## PHASE 4 — Persistence adapters
- Repos Postgres partagés

## PHASE 5 — AI layers standardisation
- Layer contract-first
- Tests unitaires + contract

## PHASE 6 — Observability unifiée
- Corrélation request → job → layer

## PHASE 7 — Cleanup final
- Suppression doublons
- Zéro exception dépendance

---

Fin du document.
