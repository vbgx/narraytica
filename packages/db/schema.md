# Database Schema Overview
Purpose

This document provides a high-level overview of the primary relational database schema.

The database is the source of truth for canonical, transactional data.
Derived systems (search, projections, enrichments) must be rebuildable from this data.

Schema Design Principles
Source of Truth

Only canonical data lives here. Derived or denormalized data should be stored elsewhere.

Strong Integrity

Use foreign keys, constraints, and indexes to enforce correctness at the storage layer.

Multi-Tenant by Design

All tenant-scoped entities include a tenant_id column and must be queried with tenant scoping.

Evolvable

Schema changes should be additive when possible and applied through migrations.

Core Entity Groups
1. Identity & Access
Table   Purpose
users   Authenticated identities
roles   Named permission sets
permissions     Action–resource definitions
memberships     Link between users and tenants with roles

2. Tenancy
Table   Purpose
tenants Logical isolation boundary
tenant_configs  Per-tenant configuration

3. Domain Data

These tables represent the core business entities of the platform.

Narralytica Canonical Domain Tables

Table   Purpose
videos          Canonical video sources and metadata (multi-source)
transcripts     Full timecoded transcript per video
segments        Time-bounded units of speech
speakers        Speaker identities within or across videos
layers          Versioned AI outputs attached to segments

Note: AI layers are derived but stored as durable, versioned outputs for reproducibility.
Search indexes remain fully derived systems.

4. Operational Tables

Table   Purpose
jobs    Background task tracking
pipeline_checkpoints    Progress tracking
event_logs      Event history
audit_logs      Security and compliance records

Common Columns and Conventions
Identifiers

Primary keys are stable unique identifiers. IDs must not be reused.

Timestamps

Most tables include created_at and updated_at.

Tenant Scoping

Tenant-scoped tables include tenant_id (indexed).

Indexing Strategy

Indexes support:
- PK lookups
- tenant_id scoping
- common filter patterns

Relationships

Foreign keys should enforce integrity wherever possible.

Migrations

Schema changes must be applied through versioned migrations.
Prefer additive changes.

Anti-Patterns to Avoid

Storing derived AI/search data as canonical truth.
Cross-tenant queries without scoping.

Relationship to Other Systems

Search, Pipelines, API, and Workers all derive from this canonical store.

Summary

The database schema safely stores canonical tenant-scoped data, enforces integrity,
and supports derived systems through controlled evolution.
