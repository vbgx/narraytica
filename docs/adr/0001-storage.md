# ADR 0001 — Storage Strategy

Status: Accepted
Date: 2026-02-11
Decision Makers: Engineering Team

Context

The platform must store and manage multiple categories of data:

Core application data (entities, metadata, relationships)

Search indexes and derived representations

Event logs and processing state

AI-related artifacts (embeddings, enrichment outputs)

Operational and audit information

The storage strategy must support scalability, reliability, and maintainability while keeping the system operable by a small engineering team.

Problem

We need to define:

What types of storage systems are used

What data belongs in each system

How data durability and consistency are handled

How storage choices affect scalability and operations

A single storage technology cannot optimally serve all use cases.

Decision

We adopt a polyglot storage strategy, where each storage system is selected based on its strengths and the nature of the data.

1. Primary Relational Database

Used for:

Core application entities

Structured metadata

Relationships and transactional data

Workflow and system state

Rationale:
Relational databases provide strong consistency, integrity constraints, and mature operational tooling.

2. Search Index

Used for:

Full-text search

Filtering and faceting

Relevance scoring

Derived searchable representations

Rationale:
Search engines are optimized for retrieval performance and ranking, not transactional integrity.

3. Object Storage

Used for:

Large raw inputs

Processed artifacts

Exported datasets

Logs or archival data

Rationale:
Object storage is cost-effective and scalable for large, unstructured or semi-structured data.

4. Event and Queue Storage

Used for:

Background task coordination

Event-driven workflows

Retry and failure handling

Rationale:
Queues and event streams enable decoupled, resilient processing.

Data Ownership Rules

Source of truth for structured entities lives in the relational database

Search indexes contain derived data only and can be rebuilt

Object storage contains non-transactional artifacts

Event systems carry transient processing state, not long-term business truth

Consequences
Positive

Each system is used for what it does best

Improved scalability and performance

Clear data ownership boundaries

Reduced risk of overloading a single storage layer

Negative

Increased operational complexity

Need for data synchronization between systems

Eventual consistency between source data and derived indexes

Alternatives Considered
Single Database for Everything

Using one storage system for all data.

Rejected because:

No single system optimizes for transactions, search, large objects, and event streaming simultaneously

Would create performance and scaling bottlenecks

Search Engine as Primary Store

Using a search index as the main system of record.

Rejected because:

Weak transactional guarantees

Poor fit for relational integrity

Implementation Notes

Clearly define which service owns each data type

Ensure rebuild processes exist for derived stores (search, projections)

Backups and recovery procedures must be defined per storage system

Monitor cost and performance characteristics of each layer

Future Revisions

This storage strategy may evolve as scale and use cases grow. Future changes might include:

Dedicated analytics storage

Cold archival tiers

Data warehousing solutions

For now, a polyglot storage model provides the best balance between flexibility, performance, and operational clarity.

End of ADR 0001

---

## EPIC01-08 — Canonical storage_ref

Narralytica stores large artifacts (media files, full transcript artifacts, embeddings blobs) outside Postgres.
Postgres stores only references using a single canonical shape: `storage_ref`.

### Canonical shape

`storage_ref` minimal fields:
- provider
- bucket
- key

Optional fields:
- content_type
- size_bytes
- checksum
- created_at
- metadata

Contract source of truth:
- packages/contracts/schemas/storage_ref.schema.json

### DB policy

Entities that reference large artifacts include a `storage_ref` JSONB column.
Legacy columns may exist temporarily but are considered deprecated in favor of `storage_ref`.

### Retention / lifecycle (baseline)

- Artifacts may be subject to lifecycle rules (expiry, tiering, archival) at the bucket level.
- Deleting canonical entities does not imply immediate blob deletion unless explicitly implemented by a cleanup job.
- Checksums (when available) should be stored to support integrity verification and reproducibility.
