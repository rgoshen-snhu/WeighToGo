# M2 Web App Quality Review

**Date:** 2026-05-23  
**Scope:** Web application only (`web/backend`, `web/frontend`, web CI, web docs). Android implementation code is excluded.  
**Checklist:** `docs/standards/cs499_code_review_checklist.md`  
**Overall assessment:** Strong M2 baseline with a few review-blocking gaps against the SRS security/accessibility contract.

## Documentation Reviewed

The review used the documentation hierarchy in `docs/README.md`: the authoritative web spec is `docs/specs/WeighToGo_Web_SRS_v2.md`, followed by the M2 brief, ADRs, DDRs, and historical Android docs for predecessor context only.

Key architecture references:

- `ARCHITECTURE.md` and SRS section 4: polyglot monorepo, React frontend, FastAPI backend, PostgreSQL.
- `docs/adr/0007-rebuild-as-full-stack-web-application.md`: rebuild rationale and debt addressed from the Android artifact.
- `docs/adr/0008-polyglot-monorepo.md`: Android preserved, web active.
- `docs/adr/0012-three-pattern-backend-architecture.md`: Screaming + Clean + Hexagonal backend.
- `docs/adr/0013-refresh-token-rotation-family-revocation.md`: one-time refresh tokens with family replay revocation.
- `docs/adr/0014-tanstack-query-for-server-state.md`: TanStack Query as server-state standard.
- `docs/adr/0015-opaque-compound-cursor-pagination.md`: keyset cursor pagination for weight entries.
- `docs/plans/milestone-two-plan.md`: M2 scope and definition of done.
- `docs/standards/CODE_QUALITY_AUDIT.md` and `docs/plans/CODE_QUALITY_FIX_PLAN.md`: historical Android findings that the web rebuild is intended to address.

## Verification Performed

Commands run from the local checkout:

| Area | Command | Result |
| --- | --- | --- |
| Backend tests | `uv run pytest` | 277 passed, 1 deprecation warning |
| Backend lint | `uv run ruff check .` | Passed |
| Backend format | `uv run ruff format --check .` | Passed |
| Backend types | `uv run mypy` | Passed, 120 source files |
| Frontend types | `npm run typecheck` | Passed |
| Frontend tests | `npm run test:ci` | 42 files / 218 tests passed; coverage thresholds passed |
| Frontend lint | `npm run lint` | 0 errors, 1 React Compiler warning |
| Frontend format | `npm run format:check` | Passed |

E2E was reviewed statically but not executed in this pass.

## High-Level Strengths

- The backend folder structure matches the documented bounded contexts: `auth`, `weight_tracking`, `dashboard`, `goals`, and `shared`.
- Clean Architecture boundaries are machine-checked by import-linter contracts in `web/backend/pyproject.toml` and exercised by `tests/architecture/test_import_contracts.py`.
- The weight-entry slice has clear domain/application/interface separation and strong coverage for CRUD, validation, soft delete, and cursor pagination.
- The frontend follows the documented feature-based structure and uses TanStack Query for auth, dashboard, and weight-entry server state.
- The test pyramid is credible for M2: backend unit/integration tests, frontend unit/component/hook tests, and Playwright specs for auth, weight, dashboard, and axe checks.
- Rate limiting is now compatible with Playwright because `web/frontend/playwright.config.ts` starts the backend with `RATE_LIMIT_ENABLED=false`.
- OpenAPI JSON is present and valid at `docs/api/openapi.json`.

## Hybrid Architecture Conformance

Overall, the web app conforms strongly to the selected hybrid architecture. The backend is the strongest evidence: the architecture is not merely documented in ADR-0012, it is reflected in folder layout, dependency direction, port/adapter boundaries, and import-linter enforcement.

### Screaming Architecture

**Status:** Strong conformance.

The backend top-level packages describe business capabilities rather than technical roles. A reader sees `auth`, `weight_tracking`, `dashboard`, `goals`, and `shared`, which makes the domain visible before framework details. This directly satisfies the Screaming Architecture goal in ADR-0012 and SRS section 4.2.

The frontend mirrors this direction through `src/features/auth`, `src/features/weight`, `src/features/dashboard`, and `src/features/placeholders`, so both sides of the web app mostly organize around product concepts rather than generic component buckets.

### Clean Architecture

**Status:** Strong conformance with pragmatic M2 exceptions.

The backend generally preserves inward dependency flow:

- `domain/` contains entities, exceptions, and ports without FastAPI, SQLAlchemy, Pydantic, or Starlette dependencies.
- `application/` contains use cases that depend on domain entities and port interfaces.
- `infrastructure/` contains SQLAlchemy repositories, ORM models, bcrypt, and JWT adapters.
- `interface/` contains FastAPI routers, Pydantic request/response schemas, cookie handling, and HTTP error mapping.

This is materially better than convention-only architecture because `web/backend/pyproject.toml` defines import-linter contracts, and `web/backend/tests/architecture/test_import_contracts.py` verifies the dependency rule in the test suite.

The main exception is the `dashboard` slice, which is intentionally a read-model slice with `interface` and `application` only. That is acceptable for M2 because dashboard owns no independent domain model yet; it composes weight-entry data through the weight-entry repository port. Future dashboard growth should either keep this read-model role explicit or introduce a full bounded-context structure if dashboard behavior becomes domain-rich.

### Hexagonal Architecture

**Status:** Strong conformance.

Ports and adapters are visible in the implemented use cases. For example, auth use cases depend on repository/password/JWT capabilities through narrow interfaces or protocols, while SQLAlchemy repositories, bcrypt hashing, and JWT signing live at the infrastructure edge. Weight-entry use cases similarly depend on `IWeightEntryRepository`, with `SqlAlchemyWeightEntryRepository` as the concrete adapter.

The router layer wires these adapters together per request. That is the correct place for framework-specific composition because FastAPI, cookies, rate limiting, and HTTP exceptions are outer-layer concerns.

### Frontend Architecture Alignment

**Status:** Good conformance by convention; less formally enforced than backend.

The frontend follows the documented feature-based architecture and uses TanStack Query for server state, React Hook Form + Zod for form validation, and React Router for declarative navigation. This avoids the Android-era hardcoded navigation and activity-bloat problems described in the historical review.

The frontend does not currently have an import-boundary enforcement tool equivalent to backend import-linter. That is not a blocker for M2, but it means frontend architectural conformance depends more on review discipline and tests than automated contracts.

### Overall Architecture Assessment

The selected hybrid architecture is real and mostly well implemented. The structure is not cosmetic: domain logic is testable without a database or HTTP server, infrastructure is kept at the edge, and use cases are independently exercised by unit tests.

The review-blocking findings below are not evidence that the hybrid architecture failed. They are mostly incomplete cross-cutting security/accessibility requirements and one frontend session-refresh edge case. The architecture provides a good place to fix those issues without large rewrites.

## Blocking Findings

### 1. Security headers are incomplete for SRS NFR-S-10

**Severity:** High  
**Checklist areas:** Structure, Defensive Programming  
**Files:** `web/backend/src/weighttogo/main.py:64-77`

The SRS requires these headers: `Strict-Transport-Security`, `X-Content-Type-Options`, `X-Frame-Options`, `Content-Security-Policy`, `Referrer-Policy`, and `Permissions-Policy`. The middleware currently emits only four of them and omits HSTS and CSP.

Impact: A deployment that reaches users outside localhost would fail the documented security baseline. CSP is especially important because the app is cookie-authenticated; it reduces XSS blast radius around authenticated sessions.

Recommended fix:

- Add environment-aware HSTS, enabled when `environment == "production"` or when TLS is guaranteed.
- Add a CSP appropriate for the Vite/React frontend and FastAPI API.
- Add regression tests asserting the full required header set.

### 2. CSRF origin/referer validation is absent for state-changing requests

**Severity:** High  
**Checklist areas:** Defensive Programming  
**Files:** `web/backend/src/weighttogo/main.py:45-59`, auth and weight routers

SRS NFR-S-9 requires SameSite=Strict cookies plus backend verification of `Origin` or `Referer` on state-changing requests. The app configures CORS and SameSite cookies, but there is no middleware or dependency that validates `Origin`/`Referer` on `POST`, `PUT`, or `DELETE`.

Impact: SameSite is a strong baseline, but the documented defense-in-depth layer is missing. This is a direct SRS compliance gap.

Recommended fix:

- Add middleware that checks `Origin` first, then `Referer`, for unsafe methods.
- Allow same-origin localhost development and configured production origins.
- Add integration tests for allowed origin, missing/invalid origin, and safe-method exemption.

### 3. Concurrent 401 handling can replay a rotated refresh token

**Severity:** High  
**Checklist areas:** Structure, Defensive Programming, Branches  
**Files:** `web/frontend/src/lib/api-client.ts:90-102`; ADR-0013

The frontend retries every 401 by calling `interceptor.refresh()` immediately. There is no shared in-flight refresh promise. If two API requests receive 401 at the same time, both can call `/api/v1/auth/refresh` with the same refresh cookie. ADR-0013 makes refresh tokens single-use and revokes the whole token family on replay, so the second refresh can turn a recoverable expired access token into a forced logout.

Impact: Users can be logged out during normal concurrent query refreshes after access-token expiry. This is most likely when dashboard and weight queries refetch together.

Recommended fix:

- Coalesce refresh attempts behind one module-level `refreshPromise`.
- Await the in-flight refresh for all concurrent 401s, then retry each original request once.
- Add a unit test with two parallel `fetchJson()` calls that asserts only one refresh call occurs.

### 4. Registration UI reintroduces email-existence disclosure

**Severity:** Medium-High  
**Checklist areas:** Structure, Defensive Programming, Documentation consistency  
**Files:** `web/frontend/src/features/auth/hooks/useRegister.ts:37-39`; ADR-0010; SRS FR-A-1 / FR-A-9

The backend intentionally returns a generic duplicate-registration body, but the frontend maps HTTP 409 to `An account with this email already exists.` This contradicts the documented generic-authentication-error policy and confirms account existence to anyone using the UI.

Impact: The API body is generic, but the shipped client still reveals the sensitive fact the policy is trying to hide.

Recommended fix:

- Replace the message with a generic completion failure, such as `The account could not be created with those details.`
- Keep field-level validation for syntactic errors, but do not confirm existing account state.
- Update the register-hook test that currently expects the account-exists wording.

### 5. Weight table action controls likely miss the 44px target requirement

**Severity:** Medium  
**Checklist areas:** Structure, Defensive Programming  
**Files:** `web/frontend/src/features/weight/components/WeightEntryTable.tsx:68-87`; SRS NFR-A-5

The edit/delete row actions use `IconButton size="small"`. MUI small icon buttons are below the 44 by 44 CSS pixel target required by the SRS. The current axe scans do not catch target-size violations, and the Playwright accessibility checks on authenticated pages only assert no critical violations, not full WCAG AA or target sizing.

Impact: The implementation risks repeating one of the Android-era accessibility findings the web rebuild is meant to close.

Recommended fix:

- Use default-size icon buttons or explicit `sx={{ minWidth: 44, minHeight: 44 }}`.
- Prefer icon-only buttons with accessible labels, or use normal `Button` controls if text must remain visible.
- Add a Playwright or component-level assertion for action target dimensions.

## Checklist Review

### Structure

**Status:** Mostly pass with targeted gaps.

- The code implements the documented M2 slice: auth, weight-entry CRUD, dashboard summary, placeholder goals/achievements/settings.
- Backend structure strongly conforms to ADR-0012. Domain and application layers avoid FastAPI/SQLAlchemy/Pydantic imports.
- Frontend structure mirrors bounded contexts and uses declarative routes, avoiding the Android-era hardcoded navigation pattern.
- Gaps:
  - Security middleware does not completely implement the design.
  - The frontend refresh interceptor is structurally incomplete for the one-time refresh-token architecture.
  - Some docs still contain version drift, for example SRS text mentions React Router v6 in some sections while code uses v7.

### Documentation

**Status:** Pass with minor drift.

- Public backend modules, use cases, routers, schemas, and frontend components generally explain intent rather than mechanics.
- ADRs are unusually strong and make review decisions traceable.
- Minor drift exists where comments reference old SRS sections or older library versions. Example: `RegisterForm.tsx` references `SRS §3.1 FR-03`, while current SRS requirements are FR-A-*.

### Variables

**Status:** Pass.

- Naming is clear and domain-driven: `RefreshSession`, `WeightEntry`, `BuildDashboardSummary`, `WeightEntryListResponse`.
- Type safety gates pass: `mypy --strict` and `tsc --noEmit`.
- No redundant variable pattern was significant enough to raise as a finding.

### Arithmetic Operations

**Status:** Pass.

- Weight values use `Decimal` in backend domain/application layers and `NUMERIC(6, 2)` in the ORM/migration.
- The API converts response values to JSON numbers at the edge, which is acceptable for display-oriented M2 behavior.
- Date comparisons use `date.today()` consistently in schema and use cases. A later production hardening pass should consider injectable clocks for deterministic time-boundary tests.

### Loops and Branches

**Status:** Pass with one frontend branch-risk finding.

- Pagination branch behavior is correct after ADR-0015: the cursor uses `(observation_date, entry_id)` and derives `next_cursor` from the last returned row.
- Delete is idempotent for already-deleted entries.
- The refresh retry branch lacks concurrency coordination and is the main branch/flow defect.

### Defensive Programming

**Status:** Partially pass.

Strong areas:

- Pydantic and Zod validate API/form inputs.
- SQLAlchemy parameterized queries avoid string-interpolated SQL.
- Database constraints enforce weight ranges, units, future-date rejection, and soft-delete consistency.
- Cookies are `HttpOnly`, `SameSite=Strict`, and production-secure through `cookie_secure`.
- CORS is allowlisted and tested.

Gaps:

- Missing HSTS/CSP headers.
- Missing Origin/Referer CSRF validation.
- Frontend account-existence message violates the generic-auth policy.
- Authenticated-page accessibility tests are not strict enough to prove WCAG AA or target-size compliance.

## Recommended Remediation Order

1. Add full security-header middleware and tests.
2. Add CSRF Origin/Referer validation for unsafe methods and tests.
3. Coalesce frontend refresh retries and add a concurrent-401 regression test.
4. Replace the duplicate-registration UI message with generic copy.
5. Increase weight table action hit targets and add target-size coverage.
6. Clean documentation version drift after functional/security fixes.

## Review Conclusion

The web app is a strong M2 implementation of the intended architecture. The core backend layering, auth use cases, weight-entry domain logic, keyset pagination, and frontend server-state approach are all well supported by tests and documentation.

The remaining issues are concentrated in security hardening and edge-condition UX/accessibility. I would not call the web app M2 quality-complete until the missing SRS security requirements and refresh-token concurrency issue are fixed or explicitly deferred with rationale.
