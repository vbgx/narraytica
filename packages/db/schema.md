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
Table	Purpose
users	Authenticated identities
roles	Named permission sets
permissions	Action–resource definitions
memberships	Link between users and tenants with roles

These tables support authentication and authorization.

2. Tenancy
Table	Purpose
tenants	Logical isolation boundary
tenant_configs	Per-tenant configuration

Every tenant-scoped table references tenants.id.

3. Domain Data

These tables represent the core business entities of the platform.

Examples (names will vary by domain):

Table	Purpose
documents	Primary content or records
datasets	Logical collections of data
records	Individual domain items
attachments	Associated artifacts stored in object storage

These tables are the inputs to pipelines and indexing.

4. Operational Tables

These support system operation rather than domain meaning.

Table	Purpose
jobs	Background task tracking
pipeline_checkpoints	Progress tracking for long processes
event_logs	Record of emitted or processed events
audit_logs	Security and compliance records

Operational tables are critical for reliability and observability.

Common Columns and Conventions
Identifiers

Primary keys are stable, unique identifiers

IDs must not be reused

Public APIs may expose safe IDs, but internal numeric IDs should remain internal when possible

Timestamps

Most tables include:

created_at

updated_at

These support auditing and synchronization with derived systems.

Tenant Scoping

Tenant-scoped tables include:

tenant_id (indexed)

Foreign key to tenants(id)

Queries must always filter by tenant_id.

Indexing Strategy

Indexes should support:

Lookup by primary key

Lookup by tenant_id

Common filter and join patterns

Uniqueness constraints where required

Over-indexing should be avoided to reduce write overhead.

Relationships

Common relationship types:

One-to-many (tenant → users, dataset → records)

Many-to-many (users ↔ roles via memberships)

One-to-many (entity → jobs, entity → events)

Foreign keys should be used to enforce integrity where possible.

Migrations

Schema changes must be applied through versioned migrations.

Guidelines:

Prefer additive changes

Avoid destructive changes without a migration plan

Deploy schema changes before code that depends on them

Test migrations in staging environments

Anti-Patterns to Avoid

Storing derived search or AI data as canonical truth

Cross-tenant queries without explicit scoping

Unbounded text fields without purpose

Business logic embedded in the database without documentation

Relationship to Other Systems

Search: receives denormalized projections of domain entities

Pipelines: read canonical data and write derived outputs

API: reads/writes canonical data

Workers: update operational tables and derived state

The database anchors the rest of the system.

Summary

The database schema is designed to:

Safely store canonical, tenant-scoped data

Enforce integrity through constraints

Support pipelines and derived systems

Evolve through controlled migrations

It is the foundation on which the rest of the platform is built.

End of Database Schema Overview