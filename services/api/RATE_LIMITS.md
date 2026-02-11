# API Rate Limits
Purpose

This document defines API-specific rate limiting rules.

It implements the global policy described in docs/specs/rate-limits.md.

Rate Limit Dimensions

Limits may be enforced per:

user

API key

tenant

IP address

endpoint

Endpoint Categories
Category	Example	Limit Strategy
Read	GET endpoints	Higher limits
Write	POST/PUT	Moderate limits
Expensive	AI/search-heavy	Strict limits
Admin	Operational endpoints	Restricted + logged
Enforcement

When a limit is exceeded:

Return HTTP 429

Include rate limit headers

Log the event for abuse monitoring

Special Protections

Endpoints that trigger:

AI inference

heavy search queries

pipeline actions

must have stricter limits and possible per-tenant quotas.

End of API Rate Limits