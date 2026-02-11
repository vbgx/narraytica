# Runbook — Incident Response

Purpose

This runbook defines how to respond to production incidents affecting system reliability, performance, or data integrity.

The goal is to:

restore service quickly

minimize user impact

identify root causes

prevent recurrence

What Is an Incident?

An incident is any unplanned event that:

Causes system downtime or degraded performance

Impacts data integrity or availability

Breaks critical user flows

Creates significant cost or operational risk

Incident Severity Levels
Level	Description
SEV-1	Major outage or data loss affecting many users
SEV-2	Significant degradation or partial feature outage
SEV-3	Minor issue with limited impact
SEV-4	Cosmetic or low-risk issue

Severity determines response urgency.

Immediate Response
1. Acknowledge

Confirm the incident is real and begin tracking it.

2. Assign an Incident Lead

One person coordinates response and communication.

3. Stabilize

Focus on stopping the impact before finding the root cause.

Examples:

Roll back a recent deployment

Disable a failing feature via flag

Scale resources if capacity-related

Investigation

After stabilization:

Check logs and monitoring dashboards

Identify recent changes (deployments, config updates)

Look for correlated failures (database, search, AI services)

Confirm whether the issue is ongoing or resolved

Avoid making multiple uncontrolled changes at once.

Communication

For significant incidents:

Inform internal stakeholders

Provide regular updates during resolution

Avoid speculation; share verified information

Clear communication reduces confusion and duplicate work.

Mitigation Strategies

Common mitigation actions:

Roll back to a known stable version

Restart failing services

Temporarily disable non-critical features

Throttle traffic to overloaded components

Document any temporary measures for later cleanup.

Recovery

Once the issue is resolved:

Monitor system health closely

Confirm error rates return to normal

Re-enable features gradually if they were disabled

Do not consider the incident closed until the system is stable.

Post-Incident Review

After recovery, conduct a retrospective:

What happened

Timeline of events

Root cause

What worked well

What failed

Preventive actions

Document findings and assign follow-up tasks.

Prevention

Typical preventive improvements include:

Better monitoring or alerts

Improved rate limits or safeguards

Additional tests or validation

Safer deployment practices

Every serious incident should lead to system improvements.

Goal

Incident response is about calm, structured action under pressure.
Stabilize first, investigate second, and improve afterward.

End of Incident Response Runbook
