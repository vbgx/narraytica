# API Error Model
Purpose

This document defines the standard error response format for the API.

All endpoints must return consistent, structured errors.

Error Response Format
{
  "error": {
    "code": "string_code",
    "message": "Human readable message",
    "details": {},
    "correlation_id": "uuid"
  }
}

Fields
Field	Description
code	Stable machine-readable error identifier
message	Human-readable explanation
details	Optional structured context
correlation_id	Request tracing ID
Error Categories
Category	Examples
Validation	invalid_input, missing_field
Auth	unauthorized, forbidden
Not Found	resource_not_found
Rate Limit	rate_limit_exceeded
Server	internal_error
Rules

Never expose stack traces

Never leak secrets

Keep error codes stable

Log full errors internally

End of API Error Model