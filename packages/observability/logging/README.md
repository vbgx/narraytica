# Logging
Purpose

This directory documents conventions and configuration related to application logging.

Logs are a primary tool for:

debugging issues

investigating incidents

understanding system behavior

auditing critical actions

Good logging makes problems diagnosable without needing to reproduce them.

Logging Principles
Structured Logs First

Logs should be structured (e.g., JSON), not free-form strings.

This allows:

filtering by fields

aggregation

correlation across services

Signal Over Noise

Log meaningful events and state changes.
Avoid excessive debug logs in production.

No Secrets

Never log:

passwords

tokens

API keys

raw sensitive personal data

Mask or omit sensitive fields.

Log Levels

Use levels consistently:

Level	Use Case
debug	Detailed internal state (local or controlled environments)
info	Normal high-level operations
warn	Unexpected but non-fatal conditions
error	Failures that affect a request or task
fatal	Process-level failures leading to shutdown

Production environments should minimize debug logs.

Required Log Fields

Every log entry should include:

timestamp

level

service or component name

message

request_id (for API logs)

correlation_id (for cross-service workflows)

Additional fields may include:

tenant_id (if multi-tenant context applies)

user_id (if safe and necessary)

job_id (for background tasks)

API Logging

For each request:

Log request start and completion

Include latency and status code

Log validation or authorization failures at warn or error level

Avoid logging full request bodies unless necessary and safe

Errors should include enough context to debug without exposing sensitive data.

Worker and Pipeline Logging

Workers should log:

Task start and completion

Key identifiers (entity IDs, batch ranges)

Retry attempts and backoff

Failure reasons with structured error info

Long-running jobs should log progress periodically.

Error Logging

Error logs should include:

Clear description of the failure

Stack trace (where applicable)

Context fields (IDs, operation type)

Correlation identifiers

Avoid generic messages like “Something went wrong”.

Correlation and Tracing

Use consistent identifiers:

request_id — per inbound API request

correlation_id — shared across related events, jobs, and services

This enables tracing a workflow across multiple logs and systems.

Log Retention

Log retention policies should balance:

debugging needs

compliance requirements

storage costs

High-volume debug logs should have shorter retention periods.

Anti-Patterns to Avoid

Logging entire objects without filtering

Swallowing errors without logs

Using logs instead of metrics for monitoring

Writing unstructured, inconsistent messages

Logging at error level for expected user mistakes

Relationship to Other Observability Signals

Logs complement:

Metrics → trends and thresholds

Traces → request flow timing

Alerts → proactive notification

Logs provide detailed context once a problem is detected.

Goal

Logging should make it possible to answer:

What happened?

When did it happen?

Which component was involved?

Which tenant/user/request was affected?

If you cannot answer these questions from logs, the logging is insufficient.

End of Logging README