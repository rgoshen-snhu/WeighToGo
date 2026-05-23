# Architecture Decision Records (ADRs)

This is the decision log for architecture-level choices made across both the
Android artifact and the CS 499 web rebuild. Each row links to the full record.

Status values: **Accepted**, **Proposed**, **Deprecated**, **Superseded**.
When a record is superseded, both the old and new entries remain in the log —
the old one keeps its number and is marked accordingly.

New ADRs follow the structure shown by existing records in this folder and use
the next available number.

## Index

| # | Title | Status | Date | Scope |
|---|---|---|---|---|
| [0001](0001-initial-database-architecture.md) | Initial Database Architecture | Accepted | 2025-12-10 | Android |
| [0002](0002-database-versioning-strategy.md) | Database Versioning Strategy | Accepted | 2025-12-10 | Android |
| [0003](0003-overall-app-architecture.md) | Overall Application Architecture | Accepted | 2025-12-10 | Android |
| [0004](0004-global-weight-unit-preference.md) | Global Weight Unit Preference Architecture | Accepted | 2025-12-12 | Android |
| [0005](0005-dependency-injection-testing.md) | Dependency Injection for Testing | Accepted | 2025-12-13 | Android |
| [0006](0006-emulator-sms-testing.md) | Emulator SMS Testing | Accepted | — | Android |
| [0007](0007-rebuild-as-full-stack-web-application.md) | Rebuild Weigh to Go! as a Full-Stack Web Application | Accepted | — | Cross-stack |
| [0008](0008-polyglot-monorepo.md) | Polyglot Monorepo for the Mobile-Web Artifact | Accepted | — | Cross-stack |
| [0009](0009-email-as-primary-user-identifier.md) | Email as Primary User Identifier | Accepted | 2026-05-22 | Web |
| [0010](0010-generic-authentication-error-policy.md) | Generic Authentication Error Policy | Accepted | 2026-05-22 | Web |
| [0011](0011-pii-masking-strategy-in-logs.md) | PII Masking Strategy in Logs | Accepted | 2026-05-22 | Web |
| [0012](0012-three-pattern-backend-architecture.md) | Three-Pattern Backend Architecture (Screaming + Clean + Hexagonal) | Accepted | 2026-05-22 | Web |
| [0013](0013-refresh-token-rotation-family-revocation.md) | Refresh Token Rotation with Family-Based Revocation | Accepted | 2026-05-22 | Web |
| [0014](0014-tanstack-query-for-server-state.md) | TanStack Query for Server State | Accepted | 2026-05-23 | Web |
| [0015](0015-opaque-compound-cursor-pagination.md) | Opaque Compound Cursor for Weight-Entry Pagination | Accepted | 2026-05-23 | Web |
