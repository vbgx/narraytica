# ADR 0002 — Search Stack Strategy

Status: Accepted
Date: 2026-02-11
Decision Makers: Engineering Team

Context

Search is a core capability of the platform. Users need to retrieve relevant information quickly across large and growing datasets. The search system must support:

Full-text search

Filtering and faceting

Ranking and relevance tuning

Fast response times at scale

Future extensibility (semantic search, reranking, AI enhancements)

A clear search stack strategy is required to avoid fragmented approaches and ensure consistent relevance behavior.

Problem

We must define:

What search technology is used

How search data is modeled and indexed

How ranking and relevance are handled

How search integrates with the rest of the system

Search is a derived system, not the primary data store, and must be designed accordingly.

Decision

We adopt a dedicated search engine as a derived index layer, separate from the primary database.

1. Search as a Projection Layer

Search indexes contain derived representations of primary data optimized for retrieval, not transactional integrity.

The relational database remains the source of truth.

2. Structured + Full-Text Indexing

Search documents combine:

Full-text indexed fields

Structured fields for filtering and faceting

Precomputed signals to support ranking

This hybrid approach enables both relevance and precise filtering.

3. Ranking Strategy

Ranking is based on a layered model:

Baseline retrieval (text matching and filters)

Field weighting (importance of titles, keywords, etc.)

Optional reranking (AI or heuristic-based, applied after initial retrieval)

This keeps the system flexible and allows future relevance improvements without re-architecting the stack.

4. Rebuildable Indexes

Search indexes must always be rebuildable from primary data sources.
No critical business logic should rely exclusively on search storage.

Consequences
Positive

High-performance search tailored to retrieval needs

Clear separation between source-of-truth data and derived indexes

Flexible ranking improvements over time

Scalability for large datasets

Negative

Eventual consistency between database updates and search index

Additional operational overhead for index management

Need for monitoring indexing pipelines

Alternatives Considered
Database-Only Search

Using database full-text search features exclusively.

Rejected because:

Limited relevance tuning

Poor scalability for complex search use cases

Harder to support advanced ranking and future AI enhancements

AI-Only Semantic Search

Relying entirely on embeddings and vector similarity.

Rejected because:

High cost and latency

Weak performance for structured filtering

Not sufficient for keyword-driven search alone

Implementation Notes

Indexing pipelines must be observable and retry-safe

Schema changes require versioned index migrations

Relevance tuning should be configuration-driven where possible

Reranking layers should be optional and cost-aware

Future Revisions

As search needs evolve, future updates may include:

Hybrid lexical + semantic retrieval

Personalized ranking signals

Query understanding enhancements

This ADR establishes the foundation: a dedicated, derived search stack with layered ranking and rebuildable indexes.

End of ADR 0002
