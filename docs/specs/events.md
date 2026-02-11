# Events Specification
Purpose

This document defines the event model used for communication between system components.

Events enable decoupled, asynchronous workflows and are a core part of the platform’s orchestration strategy.

This specification ensures events are:

consistent in structure

versioned and evolvable

observable and traceable

safe for cross-service consumption

What Is an Event?

An event represents something that already happened in the system.

Examples:

A dataset was ingested

A search index was rebuilt

An AI enrichment completed

A user-triggered process finished

Events are facts, not commands.

Event Structure

All events must follow a common envelope format:

{
  "id": "event-uuid",
  "type": "domain.event_name",
  "version": 1,
  "timestamp": "ISO-8601",
  "source": "service-name",
  "correlation_id": "workflow-or-request-id",
  "payload": { }
}

Field Definitions
Field	Description
id	Unique identifier for the event
type	Event name, namespaced by domain
version	Schema version for the event type
timestamp	Time the event occurred
source	Service that emitted the event
correlation_id	Identifier linking related workflow steps
payload	Event-specific data
Naming Conventions

Event types should follow this format:

<domain>.<entity>.<past_tense_action>


Examples:

ingestion.dataset_created

search.index_rebuilt

ai.enrichment_completed

Use past tense to reflect that events describe completed facts.

Versioning

Events must be versioned to support safe evolution.

Rules:

Increment version when the payload schema changes in a non-backward-compatible way

Consumers must handle versioning explicitly

Avoid breaking existing consumers without a migration plan

Idempotency

Event consumers must be idempotent:

Processing the same event more than once must not corrupt state

Use event id for deduplication when necessary

Delivery and Ordering

Events are delivered asynchronously and may:

Arrive out of order

Be delivered more than once

Experience delays

Consumers must not rely on strict ordering unless explicitly guaranteed by the infrastructure.

Observability

Events must be traceable across services:

Include correlation_id for workflow tracking

Log event processing start and completion

Emit metrics for processing success/failure

This enables debugging of multi-step workflows.

Security and Privacy

Event payloads must not contain:

Secrets

Sensitive personal data unless strictly required

If sensitive data is unavoidable, ensure access is restricted and data is minimized.

When to Introduce a New Event

Introduce an event when:

A state transition may be relevant to another service

A workflow step completes and triggers further processing

Observability or auditability benefits from explicit signaling

Avoid emitting events for purely internal, short-lived operations.

Future Evolution

The event model may evolve to include:

Schema registries

Stronger validation tooling

Event replay capabilities

For now, consistent structure and versioning are the foundation of reliable event-driven systems.

End of Events Specification