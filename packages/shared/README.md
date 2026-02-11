# Shared — Narralytica Common Library

This package contains **small, stable, shared utilities** used across Narralytica services.

It provides foundational building blocks that ensure consistency between the API, workers, and other platform components.

This package should remain **lightweight and dependency-minimal**.

---

## 🎯 Purpose

The shared package exists to:

- Standardize identifiers and key formats
- Provide time and language utilities
- Define common error types
- Centralize security-related helpers

It reduces duplication and prevents subtle inconsistencies across services.

---

## 📦 What’s Inside

| Folder | Purpose |
|--------|---------|
| `ids/` | ID generation, hashing, deduplication keys |
| `time/` | Timecode parsing, formatting, and conversions |
| `language/` | ISO language codes and normalization helpers |
| `errors/` | Common error taxonomy and base error classes |
| `security/` | Auth scopes, API key helpers, permission utilities |
| `README.md` | Overview (this file) |

---

## 🧱 Design Principles

### 1️⃣ Small and Stable
This package should not grow into a framework.  
Only include logic that is:
- Widely reused
- Unlikely to change frequently

### 2️⃣ No Business Logic
Business rules belong in services or domain modules, not here.

### 3️⃣ No Heavy Dependencies
Keep dependencies minimal to avoid coupling all services to large libraries.

---

## 🆔 Identifiers

The `ids/` module defines:

- Canonical ID formats
- Hashing and fingerprint helpers
- Deduplication key strategies

All services should use these helpers to ensure consistent IDs across the system.

---

## ⏱ Time Utilities

The `time/` module handles:

- Parsing timecodes
- Converting between formats (seconds, ms, HH:MM:SS)
- Validating segment timing

This ensures consistent handling of time across ingestion, transcription, and search.

---

## 🌍 Language Utilities

The `language/` module provides:

- ISO language code normalization
- Validation helpers
- Language mapping utilities

Used in transcription, indexing, and filtering.

---

## ⚠️ Error Taxonomy

The `errors/` module defines base error classes and categories used across services to ensure:

- Consistent error handling
- Predictable API responses
- Structured logging

---

## 🔐 Security Helpers

The `security/` module may include:

- Scope definitions
- Permission checks
- API key handling utilities

Authentication itself lives in the API layer, but shared logic can live here.

---

## 🚫 What Does NOT Belong Here

- Service-specific models
- Database logic
- API route logic
- Pipeline orchestration

This package is for **cross-cutting utilities only**.

---

## 📚 Related Documentation

- API architecture → `docs/architecture/api.md`
- Contracts → `packages/contracts`
- Specs (permissions) → `docs/specs/permissions.md`
