# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

The original Android artifact is preserved under the `v1.0.0-android` tag and
is intentionally not listed here; this changelog tracks the web rebuild only.

## [0.1.0] - 2026-05-23


### Added

- **backend:** Add application settings module

- **backend:** Add health-check endpoint

- **backend:** Add Alembic migration harness

- **frontend:** Add Vitest test setup and MUI theme

- **frontend:** Add App component within the MUI theme provider

- **frontend:** Add React Router 6 route declarations

- **frontend:** Add AuthContext and PreferencesContext providers

- **frontend:** Add shared layout and utility components

- **frontend:** Add api-client, error-mapping, and format utilities

- **frontend:** Add placeholder and stub feature pages

- **frontend:** Wire BrowserRouter, QueryClient, and auth/prefs providers in App

- **backend:** Scaffold screaming architecture domain folders

- **backend:** Configure import-linter contracts for clean architecture dependency rule

- **backend:** Add shared logging setup and base domain exceptions

- **auth:** Domain entities, use cases, and infrastructure adapters (Phase 6)

- **auth:** Infrastructure adapters, FastAPI interface, and Alembic migration (Phase 6)

- **api:** Emit RFC 7807 validation errors with field-level details (SRS §9.2)

- **auth:** Add zod schemas for login and register (FR-A-1, FR-A-2)

- **error-mapping:** Add mapValidationErrors for 422 field errors

- **api-client:** Send credentials, parse RFC 7807 errors, reactive 401 refresh interceptor

- **auth:** Add typed auth-client for /api/v1/auth endpoints

- **auth:** Rebuild AuthContext on React Query and add hydration splash

- **auth:** Add RegisterForm with complexity rules and confirm-password check

- **auth:** Add LoginForm with zod resolver and a11y-live error region

- **auth:** Add useLogin, useRegister, and useLogout mutations

- **auth:** Wire LoginPage and RegisterPage to forms and mutations

- **auth:** Add user menu in AppBar with logout (DDR-0003)

- **db:** Add weight_entries migration (FR-W-1..5)

- **domain:** Add WeightEntry entity, port, and exceptions

- **application:** Add five weight use cases (FR-W-1..5)

- **infra:** Add WeightEntryModel ORM and SqlAlchemy repository

- **interface:** Add weight-entries router and Pydantic schemas (FR-W-1..5)

- **dashboard:** Add dashboard summary slice (FR-D-1)

- **frontend:** Add weight schemas, clients, format helpers, and hooks

- **frontend:** Add weight and dashboard UI components

- **frontend:** Replace stub pages with real weight and dashboard pages

- **weight:** Paginate weight history with Load more button


### Changed

- Relocate Android project into android/ directory

- Standardize the web database identifier on weighttogo


### Documentation

- Add ADR-0007 and ADR-0008 for the web rebuild and monorepo

- Renumber the ADR index in the SRS for the M2 ADR set

- Rewrite the README for the polyglot monorepo

- Point CONTRIBUTING Android setup at the android/ directory

- Record Phase 2 restructure in SUMMARY

- Address Phase 2 review findings

- Drop the intermediate restructure tag

- Repair corrupted manual-testing command guides

- Remove live AI-tool references from committed documentation

- Remove project instruction-file citations from documentation

- Correct retired-tracker references in the testing index

- Correct milestone tags to 0.x development versioning

- Repair a corrupted command in the testing index README

- Correct a remaining restructure-stale path in the test setup guide

- Record Phase 2 documentation-hygiene follow-up in SUMMARY

- Update README and SUMMARY for the web scaffold

- Record the review-driven hardening in SUMMARY

- **srs:** Remove branch naming, fix backend commands to use uv, correct §5.3 procedure

- **srs:** Update §4.3.1 frontend versions to reflect actual installed stack

- **readme:** Update frontend tech stack table to reflect actual versions

- **plan:** Write ADRs at decision time, not at closeout

- **adr:** Add ADR-0009 email as primary user identifier

- **adr:** Add ADR-0010 generic authentication error policy

- **adr:** Add ADR-0011 PII masking strategy in logs

- **adr:** Add ADR-0012 three-pattern backend architecture

- **adr:** Add ADR-0013 refresh token rotation with family-based revocation

- **auth:** Add auth environment variables to .env.example (SRS §12.5.1)

- Add ADR-0014 React Query and DDR-0003 user menu placement

- Complete Phase 7 SUMMARY.md entries

- **api:** Refresh OpenAPI snapshot and update project docs (subtasks 39-44)

- **api:** Refresh OpenAPI snapshot for cursor and limit changes

- Add top-level docs/README index (GH-17)

- Add ADR decision-log index (GH-17)

- Add DDR decision-log index (GH-17)

- **srs:** Reconcile Appendix A ADR index with on-disk ADRs (GH-15)

- **readme:** Final pass — web CI badges, M2 status, docs index link (GH-15)

- **contributing:** Add web stack contribution guidelines (GH-15)

- **architecture:** Add ARCHITECTURE.md stub deferring to SRS §4 (GH-15)

- **review:** Record CS 499 checklist self-review findings (GH-15)

- **narrative:** Add Milestone Two narrative (GH-15)


### Fixed

- **frontend:** Declare all lint and test dependencies in the manifest

- **backend:** Construct settings lazily and harden the Alembic environment

- **frontend:** Type-check e2e specs and harden the Playwright config

- **frontend:** Annotate ThrowingComponent return type as never for strict TypeScript

- **frontend:** Upgrade @mui/material to v9.0.1, add @mui/icons-material@9.0.1, remove unused placeholder install

- **config:** Require DATABASE_URL — raise ValidationError if unset

- **backend:** Remove users/ domain — user identity belongs in auth/ per SRS §4.2.1

- **logging:** Configure structlog centrally with automatic PII redaction

- **arch:** Add layers contracts to import-linter for all bounded contexts

- **lint:** Sort imports in test_exceptions.py

- **types:** Add full type annotations to logging module and tests

- **security:** Enforce SECRET_KEY strength and derive cookie_secure from environment

- **security:** Atomic refresh rotation, logout without access token, inactive-user guard

- **db:** Commit session exactly once per request

- **auth:** Revoke token family when refresh finds no user

- **auth:** Populate replaced_by during refresh rotation

- **auth:** Equalize timing for locked-account login attempts

- **auth:** Derive dummy bcrypt hash from current cost factor

- **auth:** Logout revokes full token family via injected adapter

- **cors:** Honor CORS_ALLOWED_ORIGINS env var

- **auth:** Normalize email case at API boundary

- **auth:** Rate-limit logout endpoint

- **security:** Support trusted proxy headers in rate limiter

- **auth:** Include attribute parity in cookie deletion

- **auth:** Scope refresh cookie to auth endpoints

- **auth:** Validate JWT typ/aud/iss claims

- **auth:** Cap password length at bcrypt's 72-byte limit

- **schema:** Align ORM types with migration (BigInt, UUID)

- **e2e:** Use repo-relative path in screenshot spec

- **api-client:** Call onLogout when post-refresh retry fails

- **auth:** Add 3/hour rate limit to /register per NFR-S-5

- **e2e:** Bypass /register rate limit for E2E via RATE_LIMIT_ENABLED env var

- **e2e:** Replace __dirname with ESM-compatible import.meta.url in screenshot spec

- **e2e:** Wait for post-login redirect and disambiguate delete locator

- **weight:** Exclude soft-deleted from get_by_id; add get_by_id_including_deleted

- **weight:** Validate list limit range with Query(ge=1, le=100)

- **weight:** Opaque compound cursor for list pagination (ADR-0015)

- **weight:** Render not-found state when edit-form fetch fails


### Security

- Address Phase 3 review findings

- Pin GitHub Actions and the pre-commit hook to commit SHAs

- **auth:** Security tests for lockout, enumeration prevention, and PII masking



