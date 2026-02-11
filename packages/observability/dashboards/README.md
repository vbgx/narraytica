# Dashboards
Purpose

This directory contains definitions and documentation for observability dashboards.

Dashboards provide real-time and historical visibility into system behavior. They help engineers understand:

system health

performance trends

workload patterns

capacity and cost drivers

Dashboards support decision-making and incident investigation but do not replace alerts.

What Dashboards Are For

Dashboards are used to:

Monitor system health at a glance

Investigate incidents and anomalies

Understand performance regressions

Track growth and capacity usage

Support operational and cost planning

They provide situational awareness, not automatic intervention.

Dashboard Categories
Category	Focus
API	Request rate, latency, error rate
Workers	Throughput, queue depth, failures
Pipelines	Processing speed, backlogs, retries
Search	Query latency, error rates, cluster health
AI	Inference latency, token usage, request volume
Database	Query performance, connection usage
Infrastructure	CPU, memory, disk, network
Cost	Resource usage and spend trends

Each major subsystem should have at least one dedicated dashboard.

Design Principles
Actionable Views

Dashboards should help answer:

What changed?

Is the system healthy?

Which subsystem is responsible?

Avoid cluttered dashboards with unrelated metrics.

Layered Detail

Provide:

High-level overview dashboards for quick checks

Deeper, subsystem-specific dashboards for investigation

Consistent Time Windows

Use common time ranges (last 5m, 1h, 24h, 7d) for easier comparison.

Metric Selection

Dashboards should prioritize:

Latency (avg, p95, p99)

Throughput (requests/sec, jobs/sec)

Error rates

Queue or backlog size

Resource saturation (CPU, memory, I/O)

Avoid vanity metrics that do not inform operational decisions.

Naming Conventions

Use clear, consistent names:

API — Overview

Pipelines — Ingestion

Search — Query Performance

AI — Usage & Cost

Names should make it obvious what part of the system the dashboard represents.

Dashboard Ownership

Each dashboard should have an owner responsible for:

Keeping metrics relevant

Updating panels after system changes

Removing obsolete visualizations

Outdated dashboards create confusion during incidents.

Relationship to Alerts

Dashboards and alerts work together:

Dashboards help detect trends and diagnose issues

Alerts notify when thresholds are crossed

Every critical alert should have a related dashboard for deeper inspection.

During Incidents

Dashboards are essential for:

Confirming incident scope

Identifying affected subsystems

Tracking recovery progress

Validating that metrics return to normal

They provide context that logs and traces alone cannot.

Continuous Improvement

Dashboards should evolve as the system evolves:

Add panels when new subsystems are introduced

Remove unused metrics

Adjust visualizations after incidents reveal blind spots

Observability is a living part of the system.

Goal

Dashboards give engineers shared visibility into system behavior.
A good dashboard makes it easy to see what’s happening — and where to look next.

End of Dashboards README