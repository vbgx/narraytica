# PHASE 8 — Application Layer Deployment (10 produits, 1 cerveau)

Milestone : PRODUCT-LAYER

🎯 Objectif de la phase

Construire 10 applications métier comme interfaces spécialisées au-dessus du même cerveau Narralytica.

⚠️ Important :

Aucune duplication de logique

Aucun fork de search / ai_layers / persistence

Chaque application = composition de use-cases existants

Toute nouvelle logique métier = packages/application/products/*

🧱 Principe architectural

Structure cible :

packages/
  application/
    products/
      video_research/
      linguatube/
      insight_monitor/
      creator_intelligence/
      speaker_dna/
      clip_quote/
      lecture_finder/
      debate_map/
      trend_pulse/
      idea_mining_api/


Chaque produit :

Compose use_cases/search

Compose use_cases/enrich

Compose use_cases/jobs

Ajoute une orchestration métier spécifique

Ne touche jamais aux adapters infra

🔵 ISSUE 8.1 — Introduire la couche products/ (fondation multi-app)

Title: feat(products): introduce product-level application layer

Objectif

Créer une couche “product orchestration” séparée des use-cases génériques.

Structure
packages/application/products/
  base.py
  types.py
  registry.py

Règles

Aucun produit ne parle directement aux adapters infra.

Tous passent par :

SearchEngine

AI layers registry

Repos via ports

Observability

DoD

Product layer importable

Aucun import HTTP/DB

Registry des produits possible

🎓 ISSUE 8.2 — VideoResearch Pro
Objectif produit

Recherche académique & journalistique.

Fonctionnalités cœur

Recherche sémantique citations

Récupération contexte (± N secondes)

Export structuré (APA/MLA/JSON)

Collections (dossiers)

Dépendances

SearchEngine

SegmentsRepo

TranscriptsRepo

Observability

Implémentation
products/video_research/
  use_cases.py
  exporters.py
  citation_formatter.py

Use-cases

search_citations(query, filters)

get_context(segment_id, window_seconds)

export_reference(segment_id, format)

create_research_folder(user_id)

Tests

Golden test citation format

Context window correctness

Export JSON stable

DoD

Produit n’introduit aucune nouvelle logique search

Exports validables

Observability : videoresearch.search.executed

🌍 ISSUE 8.3 — LinguaTube Studio
Objectif produit

Apprentissage langue sur vidéo réelle.

Dépendances

Segmentation existante

CEFR layer

Embeddings multi-langue

Alignement segment ↔ traduction

Implémentation
products/linguatube/
  bilingual_alignment.py
  exercise_generator.py
  difficulty_filter.py

Use-cases

get_bilingual_segments(video_id)

filter_by_cefr(level)

generate_exercises(segment_ids)

extract_vocabulary(segment_ids)

Tests

CEFR filter stable

Alignment deterministic

Exercise generation schema stable

DoD

Aucun calcul CEFR hors ai_layers

No duplication embeddings logic

🧠 ISSUE 8.4 — InsightMonitor
Objectif produit

Veille stratégique.

Dépendances

Topics layer

Sentiment layer

Speakers repo

Time-series aggregation

Implémentation
products/insight_monitor/
  trend_analyzer.py
  alert_engine.py
  speaker_tracker.py

Use-cases

track_topic_over_time(topic, date_range)

detect_emerging_signals()

list_speakers_on_topic(topic)

create_alert(user_id, rule)

Tests

Trend slope detection

Alert trigger threshold

Sentiment aggregation stable

DoD

Aucun calcul topics dans produit

Pure orchestration sur layers existants

🎤 ISSUE 8.5 — Creator Intelligence
Objectif produit

Outil pour créateurs.

Dépendances

Key moments layer

Clustering

Search

Summary layer

Use-cases

get_best_moments(video_id)

suggest_short_clips(video_id)

analyze_video_theme(video_id)

search_in_own_content(user_id, query)

Tests

Deterministic ranking

Clip suggestion stable

No direct LLM calls in product

🧬 ISSUE 8.6 — SpeakerDNA
Objectif produit

Profil analytique d’un orateur.

Dépendances

Topics

Stance layer

Sentiment

Historical aggregation

Use-cases

get_speaker_profile(speaker_id)

detect_position_evolution(speaker_id)

find_potential_contradictions(speaker_id)

Tests

Position evolution time-order correct

Contradiction detection stable

Aggregation deterministic

📰 ISSUE 8.7 — ClipQuote
Objectif produit

Citation prête à publier.

Dépendances

Search fine

Context retrieval

Export formatting

Use-cases

find_exact_quote(text)

format_for_social(segment_id)

verify_context(segment_id)

Tests

Exact match precision

Export format stable

Context integrity preserved

📚 ISSUE 8.8 — LectureFinder
Objectif produit

Segments pédagogiques courts.

Dépendances

Summaries

CEFR

Clustering

Use-cases

find_explanations(topic, difficulty)

compare_explanations(topic)

create_learning_collection(user_id)

Tests

CEFR filter correct

Cluster grouping stable

🧩 ISSUE 8.9 — DebateMap
Objectif produit

Cartographie d’arguments.

Dépendances

Stance layer

Topics

Historical linking

Use-cases

map_positions(topic)

build_argument_tree(topic)

compare_opposing_speakers(topic)

Tests

Position clustering deterministic

Tree structure valid (no cycles)

🔍 ISSUE 8.10 — TrendPulse Video
Objectif produit

Tendances émergentes.

Dépendances

Topics

Time aggregation

Volume metrics

Use-cases

detect_rising_concepts()

compare_timeframes(topic)

identify_thought_leaders(topic)

Tests

Trend delta stable

Time window comparisons correct

🧠 ISSUE 8.11 — Idea Mining API (exposition développeurs)
Objectif produit

Exposer le cerveau brut aux développeurs.

Dépendances

Search

Topics

Profiles

Layers

Implémentation

API endpoints spécialisés

No new logic

Versioned API

Tests

Contract tests strict

Backward compatibility stable

🔐 ISSUE 8.12 — Multi-product isolation & config
Objectif

Permettre config par produit sans duplication logique.

Scope

Feature flags

Default search mode

Allowed layers

Rate limits

Implémentation
products/config/
  product_config.yaml

DoD

Un produit peut être activé/désactivé

Aucun fork de logique nécessaire

📊 ISSUE 8.13 — Observability par produit
Objectif

Chaque produit émet ses events distincts.

Exemple

videoresearch.search.executed

linguatube.exercise.generated

insightmonitor.alert.triggered

DoD

Tous les produits ont namespace event propre

Pas de duplication schema envelope

🧪 ISSUE 8.14 — Tests & CI produit
Objectif

Empêcher drift entre produits.

Scope

Tests unitaires par produit

Contract tests payload

Golden tests UX-level responses

Load tests minimal (search heavy)

DoD

Aucun produit ne bypass packages/search

CI casse si produit importe infra directement

🎯 Définition de Done PHASE 8

Chaque produit vit dans packages/application/products/*

Aucun produit n’implémente search/ai/persistence

Tous utilisent les ports existants

Observability unifiée

CI interdit duplication logique

Chaque produit a au moins 3 tests critiques
