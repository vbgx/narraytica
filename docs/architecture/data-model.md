# Data Model Architecture
Purpose

This document describes the core data model of the system: how entities are structured, how they relate to each other, and how canonical and derived data are separated.

The data model is designed to be:

clear in ownership

consistent across services

evolvable without breaking contracts

aligned with system boundaries

Canonical vs Derived Data

The system distinguishes between:

Canonical Data

The source of truth stored in the primary database.

Examples:

Users

Tenants

Domain entities

Configuration objects

Canonical data must be strongly consistent and auditable.

Derived Data

Data computed from canonical sources and optimized for performance or specialized use cases.

Examples:

Search documents

AI-generated enrichments

Aggregations and projections

Derived data can be rebuilt and is eventually consistent.

Core Entity Categories
1. Identity & Access

Entities that control who can access the system.

Entity	Description
User	An authenticated individual
Role	A set of permissions
Permission	Action-resource authorization unit
Membership	Link between user and tenant
2. Tenancy

Entities that define isolation boundaries.

Entity	Description
Tenant	Logical organization boundary
TenantConfig	Tenant-specific configuration

All tenant-scoped entities must include tenant_id.

3. Domain Entities

Core business objects specific to the platform’s purpose.

Examples may include:

Documents

Records

Datasets

Content items

These entities:

live in the primary database

may have relationships to other entities

act as inputs to pipelines and indexing

4. Operational Entities

Used to track system behavior rather than domain meaning.

Entity	Description
Job	Background task execution record
EventLog	Record of emitted/processed events
AuditLog	Security- or compliance-related records
PipelineCheckpoint	Progress marker for long-running processes

These support reliability and observability.

Relationships

Typical relationship patterns:

Tenant → Users (one-to-many)

User ↔ Roles (many-to-many)

Domain Entity → Derived Representations (one-to-many)

Domain Entity → Events (one-to-many, temporal)

Relationships should be explicit and enforceable through foreign keys where appropriate.

Identifiers

Entities use globally unique identifiers.

Guidelines:

Stable across system boundaries

Never reused

Exposed IDs should be safe to share externally

Internal numeric IDs may exist but should not leak into public APIs if avoidable.

Schema Evolution

The data model must support change over time.

Rules:

Additive changes preferred over destructive ones

Avoid renaming fields without migration strategy

Maintain backward compatibility where contracts exist

Use migrations for structural changes

Contract tests should guard cross-service schema expectations.

Denormalization Strategy

For performance reasons:

Some data may be denormalized into derived stores

Canonical storage should remain normalized and authoritative

Derived documents must be rebuildable from canonical entities

Validation and Constraints

The data model enforces integrity through:

Database constraints (foreign keys, uniqueness)

Application-level validation

Schema validation at pipeline boundaries

Validation should occur as early as possible in the data lifecycle.

Multi-Tenancy Considerations

Tenant-scoped entities must:

Include tenant_id

Be indexed by tenant_id for efficient queries

Never be returned across tenant boundaries without explicit authorization

Tenant isolation is a first-class requirement in the data model.

Summary

The data model architecture is built around:

Clear separation of canonical and derived data

Strong identity and tenancy boundaries

Explicit relationships and constraints

Evolvable schemas with migration paths

A well-structured data model enables reliable pipelines, consistent APIs, and scalable system growth.

End of Data Model Architecture Document