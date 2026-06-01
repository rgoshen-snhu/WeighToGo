# M3 Web App Quality Review

**Date:** 2026-05-30 12:18 MST  
**Scope:** Web application only (`web/backend`, `web/frontend`, web CI/docs). Android implementation code is excluded.  
**Checklist:** `docs/standards/cs499_code_review_checklist.md`  
**Review posture:** Checklist-based code review with explicit assumption challenges against the SRS, ADRs, and delivered M3 behavior.  
**Overall assessment:** Strong M3 implementation with credible architecture and test coverage, but not fully quality-complete against the documented performance, route-splitting, and end-to-end achievement semantics.

## Documentation Reviewed

- `docs/standards/cs499_code_review_checklist.md`
- `docs/standards/M2_WEB_APP_QUALITY.md`
- `docs/specs/WeighToGo_Web_SRS_v2.md`
- `docs/plans/milestone-three-plan.md`
- `docs/adr/0012-three-pattern-backend-architecture.md`
- `docs/adr/0019-milestone-detection-algorithm.md`
- `docs/adr/0020-preferences-storage-data-structure.md`
- `docs/adr/0021-composite-index-strategy.md`
- `docs/adr/0022-streak-detection-algorithm.md`
- `docs/adr/0023-ttl-caching-strategy.md`
- `web/README.md`, `web/backend/README.md`, `web/frontend/README.md`

## Verification Performed

Commands run from the local checkout:

| Area | Command | Result |
| --- | --- | --- |
| Backend lint | `uv run ruff check .` from `web/backend` | Passed |
| Backend format | `uv run ruff format --check .` from `web/backend` | Passed |
| Backend types | `uv run mypy` from `web/backend` | Passed: 217 source files |
| Backend tests | `uv run pytest` from `web/backend` | 591 passed, 4 skipped, 2 warnings; 97% total coverage |
| Frontend lint | `npm run lint` from `web/frontend` | Passed with 1 React Compiler warning |
| Frontend types | `npm run typecheck` from `web/frontend` | Passed |
| Frontend tests | `npm run test:ci` from `web/frontend` | 67 files / 377 tests passed; 94.63% statements, 96.67% lines |
| Frontend format | `npm run format:check` from `web/frontend` | Passed |
| Frontend build | `npm run build` from `web/frontend` | Passed; emitted a >500 kB chunk warning |

E2E tests were reviewed statically but not executed in this pass. The 4 skipped backend tests are the PostgreSQL index-plan tests in `web/backend/tests/integration/weight/test_index_usage_postgres.py`; they require `WEIGHTTOGO_TEST_POSTGRES_DSN`. That matters because NFR-P-3 is one of the M3 performance deliverables.

## Strengths

- Backend bounded contexts are clear and domain-first: `auth`, `weight_tracking`, `goals`, `achievements`, `preferences`, `dashboard`, and `shared`.
- Import-linter architecture tests enforce Clean Architecture boundaries for the implemented backend contexts.
- M3 algorithm work is represented by pure domain functions: goal progress, milestone detection, streak detection, unit conversion, and rate-of-change.
- Security remediation from M2 is present: CSP/HSTS/security-header middleware, CSRF Origin/Referer middleware, refresh-token coalescing, generic auth messages, and PII-aware logging tests.
- The frontend has a mature feature-based structure with typed API clients, Zod schemas, React Hook Form, TanStack Query, and component/hook tests around the major flows.
- Preference-driven display conversion is implemented in major visible surfaces such as weight history, latest-entry cards, and the trend chart.
- The project has strong ADR coverage through ADR-0023 and CI workflows for backend, frontend, E2E, release, and security audit.

## Blocking and High-Priority Findings

### 1. Rate-of-change implementation does not match the documented indexed-window contract

**Severity:** High  
**Checklist areas:** Structure, Arithmetic Operations, Loops and Branches, Defensive Programming  
**Files:** `web/backend/src/weighttogo/dashboard/application/build_dashboard_summary.py:97`, `web/backend/src/weighttogo/weight_tracking/domain/rate_of_change.py:69`, `docs/specs/WeighToGo_Web_SRS_v2.md`, `docs/adr/0021-composite-index-strategy.md`

SRS §13.2.1 says weekly rate of change is delivered using "two indexed lookups against composite indexes." The M3 plan and `rate_of_change.py` docstring also describe an O(w) algorithm over the two 7-day windows after indexed seeks.

The implementation instead loads the user's entire active weight series using `list_for_user_in_range(user_id, date.min, date.max)` and then scans that full sequence to compute the rate. This is indexed at the database predicate level, but it is not the two-window read path the SRS and ADR story promise. For a long-term user, dashboard summary cost grows with all historical entries even when the rate calculation only needs two 7-day windows.

**Recommended fix:** Split dashboard summary into separate reads: use a bounded indexed range for rate-of-change, keep the full trend read only for the chart path, and add a regression test proving the rate path does not materialize all historical entries.

### 2. Achievement detection only runs on weight-entry creation, not update or delete

**Severity:** Medium-High  
**Checklist areas:** Structure, Loops and Branches, Defensive Programming  
**Files:** `web/backend/src/weighttogo/weight_tracking/interface/router.py:151`, `web/backend/src/weighttogo/weight_tracking/interface/router.py:324`, `web/backend/src/weighttogo/weight_tracking/interface/router.py:397`, `docs/specs/WeighToGo_Web_SRS_v2.md`, `docs/adr/0019-milestone-detection-algorithm.md`

The create endpoint performs achievement detection and returns `newly_earned_achievements`. The update and delete endpoints only invalidate the dashboard cache. If a user edits an existing entry so it now crosses a milestone or reaches the target, no milestone or goal-reached achievement is recorded. If a user deletes or edits down the entry that previously caused a goal to be achieved, the achieved state and achievement rows remain.

ADR-0019 intentionally says detection runs on `POST /weight-entries`, but the SRS language is broader: "when a weight entry causes a goal to be reached" and "detect quantitative milestones." That is an assumption mismatch, not just a missing test.

**Recommended fix:** Decide explicitly whether achievements are create-only and permanent, or recomputed on create/update/delete. If create-only is the intended product rule, update the SRS and tests to say so. If not, move achievement orchestration into a shared write-side service used by create/update/delete and define rollback/recompute semantics.

### 3. Frontend routes are documented as code-split, but all pages are statically imported

**Severity:** Medium  
**Checklist areas:** Structure, Storage use efficiency, Documentation  
**Files:** `web/frontend/src/App.tsx:18`, `web/frontend/src/App.tsx:67`, `docs/specs/WeighToGo_Web_SRS_v2.md`

SRS §10.1 and NFR-P-2 describe React Router with code-split routes loaded on demand. `App.tsx` statically imports every page, including dashboard, auth, goals, achievements, settings, and weight pages. The production build succeeded but emitted a single `dist/assets/index-*.js` chunk of about 1,017.84 kB before gzip and Vite warned that some chunks exceed 500 kB.

This is not a runtime failure, but it is a documented-performance gap. It also weakens the claim that navigation is loaded on demand.

**Recommended fix:** Use `React.lazy`/`Suspense` or React Router lazy route modules for route-level splitting. Add a small build assertion or documented bundle budget so the warning is not ignored.

### 4. Global weight-unit preference is not applied everywhere weight is displayed or prefilled

**Severity:** Medium  
**Checklist areas:** Structure, Variables, Documentation consistency  
**Files:** `web/frontend/src/features/goals/components/GoalHistoryList.tsx:46`, `web/frontend/src/features/goals/pages/GoalsPage.tsx:278`, `web/frontend/src/features/achievements/pages/AchievementsPage.tsx:28`, `web/frontend/src/features/achievements/components/AchievementNotification.tsx:37`

FR-P-1 says the default weight unit drives display formatting throughout the application. The main weight history, latest-entry card, active goal display, and trend chart honor this. Some M3 surfaces still leak stored or hard-coded units:

- Goal history renders raw `start_value -> target_value target_unit`.
- Goal creation prefill takes the latest entry's stored unit rather than converting the prefilled value into the user's preferred unit.
- Achievement labels and toast copy hard-code "lb" for milestones. This may be intentional because FR-Ach-2 defines pound-based thresholds, but it should be explicitly called out as a product decision for users who choose kg.

**Recommended fix:** Use the same `formatWeightInPreferredUnit` helper in goal history, convert goal prefill values to the preferred unit, and document whether milestone labels are intentionally pound-based or should display an equivalent kg value.

## Medium and Low-Priority Findings

### 5. Retired M2 placeholder pages and tests remain in the active source tree

**Severity:** Low-Medium  
**Checklist areas:** Structure, Documentation, leftover stubs/test routines  
**Files:** `web/frontend/src/features/placeholders/AchievementsPlaceholderPage.tsx:1`, `web/frontend/src/features/placeholders/SettingsPlaceholderPage.tsx:1`, `web/frontend/src/features/placeholders/PlaceholderPages.test.tsx:32`

The real M3 pages are wired in `App.tsx`, but the M2 placeholder components and tests still assert "Coming in Milestone 3." They are not routed, yet they remain as maintained code and passing tests.

This is harmless at runtime but creates avoidable documentation and test drift. A future reader can reasonably ask why a released M3 codebase still tests Milestone 3 placeholders.

**Recommended fix:** Remove the retired placeholder components/tests or move them to historical documentation if they are needed as portfolio evidence.

### 6. Frontend lint passes with a React Compiler warning in a form component

**Severity:** Low  
**Checklist areas:** Structure, Variables  
**File:** `web/frontend/src/features/weight/components/WeightEntryForm.tsx:83`

`npm run lint` exits successfully, but React Compiler skips memoization for `WeightEntryForm` because React Hook Form's `watch()` API is incompatible with compiler memoization. This is not a bug by itself, but the code already carries `any` casts around `zodResolver` in `WeightEntryForm.tsx` and `GoalForm.tsx`, so the form layer has a small cluster of type/tooling escape hatches.

**Recommended fix:** Track the warning as accepted technical debt, or refactor to `useWatch`/supported RHF patterns if React Compiler compatibility is a goal. Replace `as any` casts with a typed resolver helper if library typings allow it.

### 7. OpenAPI and SRS descriptions have minor M3 drift

**Severity:** Low  
**Checklist areas:** Documentation  
**Files:** `docs/api/openapi.json`, `docs/specs/WeighToGo_Web_SRS_v2.md`

The OpenAPI snapshot includes M3 endpoints, but the achievement schema description still says achievement type is "`goal_reached` or `milestone`" and omits `streak`. The SRS route table still names placeholder components while annotating them as M3-full later in the row. These are small but visible documentation mismatches.

**Recommended fix:** Regenerate or hand-correct the OpenAPI snapshot descriptions and reconcile the frontend route table to name the delivered M3 page components.

## Assumptions Challenged

1. **"Green tests prove NFR-P-3."** Not fully. The local suite skipped the PostgreSQL index-plan tests, so this checkout has strong unit/integration evidence but not local proof of production planner behavior.
2. **"Synchronous achievement detection means POST-only."** ADR-0019 narrows the implementation to create flow, but the SRS requirement reads broader. That decision needs explicit product sign-off.
3. **"Streaks are goal-scoped."** The implementation records streak achievements against the active goal and filters dates to `goal_created_at`. FR-Ach-3 says "logging streaks," not "goal streaks." Goal-scoping may be the right portfolio story, but it should be explicit.
4. **"All trend data belongs in the dashboard summary."** Returning the full historical series supports an "All" chart range, but it couples initial dashboard payload size to lifetime usage. If the product grows, chart range endpoints or lazy chart data would be cleaner.
5. **"M3 placeholders can remain because they are unrouted."** Keeping stale components and tests is still maintenance surface. The checklist explicitly asks about unneeded procedures, unreachable code, and leftover stubs.

## Checklist Review

### Structure

**Status:** Mostly pass with M3-specific gaps.

The web app implements the M3 domains and keeps most architecture boundaries clean. Backend layering is stronger than frontend layering because it is enforced by import-linter. The main structure gaps are the rate-of-change read path mismatch, create-only achievement detection, no actual route code splitting, and stale placeholder components.

### Documentation

**Status:** Pass with drift.

The ADR set is strong and unusually useful. The SRS, plan, and code comments make most trade-offs discoverable. Drift remains in OpenAPI achievement descriptions, placeholder route naming, and the rate-of-change complexity story.

### Variables

**Status:** Pass.

Naming is domain-driven and consistent across backend and frontend. Type gates pass for Python and TypeScript. Minor type escape hatches remain in frontend form resolver casts.

### Arithmetic Operations

**Status:** Pass with performance caveat.

Backend core numeric work uses `Decimal`, including unit conversion, goals, achievements, and rate-of-change. The rate-of-change formula itself is understandable and tested. The concern is not arithmetic correctness; it is that the implementation scans the full materialized series despite documentation claiming bounded-window computation.

### Loops and Branches

**Status:** Partial pass.

The pure algorithms are simple and testable: milestone detection scans fixed thresholds, streak detection sorts and scans dates, and progress is O(1). The main branch gap is write-flow coverage: create triggers achievements, while update/delete do not.

### Defensive Programming

**Status:** Mostly pass.

Input validation, authentication, CSRF, CORS, security headers, cookie attributes, generic auth messages, and PII-aware logging have strong coverage. Defensive gaps are around proving PostgreSQL index behavior locally, keeping route bundle size under the documented target, and making achievement semantics explicit under updates/deletes.

## Recommended Remediation Order

> Tracked as the **M3 remediation effort**, scoped separately from Milestone Four. See `docs/plans/milestone-three-plan.md` §9 for the work items and the M4 ownership boundary.

1. Resolve the achievement write-flow contract: create-only/permanent vs create/update/delete recomputation.
2. Align rate-of-change implementation with the documented indexed-window design or update the SRS/ADR to reflect the full-series dashboard read.
3. Add route-level code splitting and a bundle-size guard.
4. Apply preferred-unit formatting to goal history and goal prefill, and document milestone unit semantics.
5. Remove retired placeholder pages/tests.
6. Refresh OpenAPI and SRS wording for delivered M3 components and streak achievements.
7. Run PostgreSQL-backed index-plan tests before declaring NFR-P-3 complete.

## Review Conclusion

The M3 web app is a serious implementation: the architecture is coherent, the automated test coverage is high, and the algorithms are written in the right layers. The most important quality issue is that a few M3 claims are stronger than the code currently proves. In particular, rate-of-change is documented as bounded indexed-window work but implemented as a full-series dashboard scan, and achievement detection is documented broadly in the SRS but implemented only on creation.

I would call the web app M3 feature-complete in a broad sense, but not M3 quality-complete until the assumption mismatches above are either fixed or explicitly documented as intentional scope decisions.
