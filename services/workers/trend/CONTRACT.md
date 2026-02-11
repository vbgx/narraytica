# Trend Worker Contract
Purpose

Defines the contract between the Trend worker and the rest of the system.

Inputs

The worker consumes events of type:

trend.analysis_requested

Payload
Field	Description
entity_id	ID to analyze
tenant_id	Tenant context
timestamp	Trigger time
Outputs

The worker emits:

trend.analysis_completed
trend.analysis_failed

Completed Payload
Field	Description
entity_id	Processed entity
score	Computed trend score
signals	Derived indicators
Guarantees

Processing is idempotent

Failures are retryable

Results are derived and rebuildable

End of Trend Worker Contract
