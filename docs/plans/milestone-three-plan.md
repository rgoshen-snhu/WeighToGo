# Milestone Three Implementation Brief

| Field | Value |
| --- | --- |
| Course | CS 499, Computer Science Capstone (SNHU) |
| Milestone | Three |
| Enhancement Category | Two: Algorithms and Data Structure |
| Status | Active |
| Authoritative Spec | `/docs/specs/WeighToGo_Web_SRS_v2.md` |
| Predecessor Brief | `/docs/plans/milestone-two-plan.md` |
| Tag Target | `v0.2.0` |
| Last Updated | 2026-05-28 |

---

## 1. Purpose and Scope

This brief is the entry point for Milestone Three work on the Weigh to Go! capstone artifact. The milestone covers Enhancement Two: Algorithms and Data Structure. The work builds on the Milestone Two web application (auth + weight-entry CRUD, tagged `v0.1.0`) and adds the domain logic the architecture was designed to host: goal management, achievement detection (milestone and streak), trend visualization with rate-of-change, and user preferences.

The algorithmic core — milestone detection, streak detection, and rate-of-change — is the rubric centerpiece. Each algorithm is written first as pure domain logic with in-memory fakes (TDD, zero framework imports), then wrapped in persistence and UI. Every algorithm documents its time/space complexity in both its docstring and its ADR.

Deliverables at the end of M3:

- Technical artifact (zip of all code, original Android plus enhanced web)
- Narrative document (Word format) addressing the four reflection prompts in the CS 499 Milestone Three rubric

The narrative is drafted in parallel with the code work and finalized once implementation is complete.

### 1.1 Scope Tiers

**Core (committed):**

- FR-G-1 through FR-G-4 — goal management and progress percentage
- FR-Ach-1, FR-Ach-2 — achievement recording and milestone detection
- FR-N-1 — in-app achievement notification
- FR-P-1, FR-P-3 — global weight-unit preference and notification toggles
- FR-D-4 — goal progress visualization (progress bar)
- NFR-P-3 — composite indexes for trend read paths

**Planned stretch (in-milestone, sequenced after core):**

- FR-Ach-3 — streak detection (prioritized first among stretch items for its rubric value)
- FR-Ach-4 — achievement listing
- FR-G-5 — goal history
- FR-D-2 — weight trend chart
- FR-D-3 — weekly rate of change
- FR-W-6 — weight unit conversion for display
- NFR-P-5 — TTL-based server-side caching

**Already delivered in Milestone 2 (cite in the narrative, do not rebuild):**

- FR-W-2 / NFR-P-4 — opaque compound cursor pagination, delivered in M2 PR #30 and documented in [ADR-0015](../adr/0015-opaque-compound-cursor-pagination.md). This is claimed in the M3 narrative as the data-structure exemplar; M3 verifies it still passes its tests but adds no new pagination code.

### 1.2 Reconciling Spec Drift Discovered During Planning

Two discrepancies between SRS v2 and the on-disk state were found during planning. The plan accounts for both, and Step 6 reconciles the documents:

1. **ADR numbering.** SRS Appendix A §17.2 reserves ADR-0016/0017/0018 for M3 (TTL caching, milestone detection, composite index). Those numbers are already taken on disk by M2 quality-remediation decisions (ADR-0016 security headers, ADR-0017 CSRF Origin/Referer, ADR-0018 concurrent-refresh coalescing). Per the ADR README policy ("use the next available number"), M3 ADRs are renumbered to **0019–0022**.
2. **Cursor pagination.** SRS §13.2.1 deliverable 4 still lists cursor-based pagination as M3 work; it was actually delivered in M2 (ADR-0015). It is treated here as already complete.

---

## 2. Authoritative References

Read these before generating detailed task lists. The SRS is the source of truth when references conflict.

| Document | Location | Key Sections for M3 |
| --- | --- | --- |
| **Software Requirements Specification** | `/docs/specs/WeighToGo_Web_SRS_v2.md` | §6.3 Goals, §6.4 Achievements, §6.5 Notifications, §6.6 Preferences, §6.7 Dashboard and Trends, §7.2 Performance, §8 Data Architecture, §13.2 Milestone 3 Roadmap, §14 Acceptance Criteria |
| **CS 499 Milestone Three Guidelines and Rubric** | `/docs/plans/CS 499 Milestone Three Guidelines and Rubric.md` | Possible Indicators of Success; the four narrative prompts; pass/fail criteria |
| **CS 499 Code Review Checklist** | `/docs/standards/cs499_code_review_checklist.md` | Program-standard self-review gate, applied in Step 6 before tagging `v0.2.0` |
| **Existing ADRs** | `/docs/adr/0001-*.md` through `/docs/adr/0018-*.md` | Context on prior decisions. New ADRs build on or supersede these. ADR-0004 (Android weight-unit preference) is carried forward by FR-P-1. ADR-0013/0018 (refresh rotation) constrain any new cross-cutting work. |
| **Android Database Architecture** | `/docs/architecture/WeighToGo_Database_Architecture.md` | Original goals, achievements, and key-value preferences design. Informs the web schema; superseded by SRS §8 for the web side. |

---

## 3. Implementation Sequence

Six high-level steps, ordered by data dependency (Approach A: vertical slices). Each step is a single vertical slice — migration -> domain (algorithm first, framework-free) -> application -> API -> frontend -> end-to-end — and each ends with a green CI run and all coverage thresholds met before moving to the next. Each FR gets its own feature branch per project convention (`feature/FRx.x-short-title`).

**Layout patterns to mirror (established in M2):**

- Backend domain: `web/backend/src/weighttogo/<domain>/{domain/entities.py, domain/exceptions.py, domain/ports.py, application/<use_case>.py, infrastructure/models.py, infrastructure/repositories.py, interface/router.py, interface/schemas.py}`
- Backend tests: `web/backend/tests/unit/<domain>/test_*.py`, `web/backend/tests/integration/<domain>/test_*.py`, plus `web/backend/tests/architecture/test_import_contracts.py` (the import-boundary linter)
- Migrations: `web/backend/alembic/versions/000N_*.py`
- Frontend feature: `web/frontend/src/features/<feature>/{api/<feature>-client.ts, components/*.tsx, hooks/use*.ts, pages/*Page.tsx, schemas/<feature>-schemas.ts}` with co-located `*.test.ts(x)` files
- Frontend routes: `web/frontend/src/routes.tsx`; contexts in `web/frontend/src/contexts/`

### Step 1: Goals Vertical Slice

Implements goal management end-to-end and the goal progress bar. Goals come first because achievement milestone detection (Step 2) depends on a goal's `start_value` and `target_value`.

**Functional requirements:** FR-G-1 (set active goal), FR-G-2 (track progress), FR-G-3 (update goal), FR-D-4 (progress visualization). FR-G-4 (auto-mark a goal achieved when a weight entry reaches it) shares the on-write detection mechanism and is wired in Step 2 alongside FR-Ach-1; Step 1 builds the `is_achieved`/`achieved_at` fields and the mark-achieved capability the detector calls.

**Migration:** `web/backend/alembic/versions/0003_goals.py` — create the `goals` table per SRS §8.2.4 and define the CHECK constraints the SRS left as TBD:

- `goal_type IN ('lose', 'gain')`
- `target_value > 0`, `start_value > 0`, `target_unit IN ('lbs', 'kg')`
- achievement consistency: `(is_achieved = FALSE AND achieved_at IS NULL) OR (is_achieved = TRUE AND achieved_at IS NOT NULL)`
- one active goal per user: `CREATE UNIQUE INDEX idx_goals_one_active_per_user ON goals(user_id) WHERE is_active = TRUE`

**Backend (create):**

- `goals/domain/entities.py` — `Goal` entity; `GoalProgress` value object
- `goals/domain/exceptions.py` — `ActiveGoalAlreadyExistsError`, `GoalNotFoundError`
- `goals/domain/ports.py` — `GoalRepository` port (interface)
- `goals/domain/progress.py` — `calculate_progress(start, current, target) -> Percentage` (FR-G-2): `(start - current) / (start - target)` clamped to `[0, 100]`, direction-aware via `goal_type`. Pure function, documented complexity O(1).
- `goals/application/set_active_goal.py`, `update_goal.py`, `get_active_goal_with_progress.py`, `abandon_goal.py`
- `goals/infrastructure/models.py` (SQLAlchemy `GoalModel`), `repositories.py` (`SqlAlchemyGoalRepository`)
- `goals/interface/router.py` (`POST /api/v1/goals`, `GET /api/v1/goals/active`, `GET /api/v1/goals`, `PUT /api/v1/goals/{goal_id}`, `DELETE /api/v1/goals/{goal_id}`), `interface/schemas.py`
- Register router in `web/backend/src/weighttogo/main.py`

**Frontend (create / modify):**

- Replace `features/placeholders/GoalsPlaceholderPage.tsx` usage with a real `features/goals/pages/GoalsPage.tsx`
- `features/goals/schemas/goal-schemas.ts` (Zod), `api/goal-client.ts`, `hooks/useActiveGoal.ts`, `useSetGoal.ts`, `useUpdateGoal.ts`
- `features/goals/components/GoalForm.tsx`, `GoalProgressBar.tsx` (FR-D-4)
- Update `web/frontend/src/routes.tsx` to point `/goals` at `GoalsPage`

**Testing strategy:** unit tests for `calculate_progress` (boundary cases: at-start 0%, at-target 100%, past-target clamps to 100%, lose vs gain direction); unit tests for each use case with an in-memory fake repository; integration tests for the five endpoints against the transactional test DB; a `test_migration_0003` upgrade/downgrade test; frontend component tests for the form and progress bar via accessible queries; one Playwright E2E for goal creation through progress display.

**Risks:** the one-active-goal partial unique index must be enforced at the DB level, not only in the use case, to avoid a race. Cover the conflict path (409) explicitly.

### Step 2: Achievements and Milestone Detection

Implements the milestone detection algorithm and the in-app notification. This is the primary algorithmic showcase.

**Functional requirements:** FR-Ach-1 (goal achievement recording), FR-Ach-2 (milestone detection at 5/10/25/50 lb), FR-G-4 (auto-mark the goal achieved on the entry that reaches it), FR-N-1 (in-app notification).

**ADR (write before any code in this step):** ADR-0019 Milestone Detection Algorithm.

**Migration:** `web/backend/alembic/versions/0004_achievements.py` — create `achievements` table with a unique constraint that guarantees once-per-goal idempotency at the DB level: `CONSTRAINT achievements_unique_milestone UNIQUE (goal_id, achievement_type, threshold)`.

**Backend (create):**

- `achievements/domain/entities.py` — `Achievement` entity; `AchievementType` enum (`goal_reached`, `milestone`, later `streak`)
- `achievements/domain/milestone_detector.py` — pure function `detect_milestones(goal, latest_weight, already_recorded: set) -> list[Milestone]`. Algorithm: for each threshold T in `(5, 10, 25, 50)`, compute progress delta from `start_value` in the goal direction; if `delta >= T` and `(goal_id, T) not in already_recorded`, emit a milestone. Complexity O(k), k = 4 thresholds, O(1) per entry in practice. The `already_recorded` set is the data structure that makes detection idempotent without an N-query scan.
- `achievements/domain/ports.py` — `AchievementRepository` port
- `achievements/application/detect_achievements.py` — orchestration-friendly use case that loads recorded milestones into a set, runs the detector, and persists new achievements
- `achievements/infrastructure/models.py`, `repositories.py`
- `achievements/interface/router.py` (`GET /api/v1/achievements`, `GET /api/v1/achievements/{achievement_id}`), `interface/schemas.py`

**Cross-domain wiring (respect NFR-M-3):** detection runs synchronously on weight-entry create, but `weight_tracking` must not import `achievements`. Orchestrate at the composition root: the weight-entries router (interface layer), after `CreateWeightEntry` succeeds, invokes `DetectAchievements`. The create response is extended with a `newly_earned_achievements: []` field so the frontend can react. Modify `weight_tracking/interface/router.py` and `weight_tracking/interface/schemas.py` only; the architectural import test (`tests/architecture/test_import_contracts.py`) must still pass.

**Frontend (create / modify):**

- Real `features/achievements/pages/AchievementsPage.tsx` (replaces placeholder), `api/achievement-client.ts`, `hooks/useAchievements.ts`
- `features/achievements/components/AchievementNotification.tsx` (FR-N-1) — celebratory modal or banner shown when a weight-entry create returns a non-empty `newly_earned_achievements`. Honor `prefers-reduced-motion` (NFR-A-6) and use an ARIA live region (NFR-A-3).
- Wire the notification trigger into the existing weight-entry create flow (`features/weight/hooks/useCreateWeightEntry.ts`)
- Update `routes.tsx` to point `/achievements` at `AchievementsPage`

**Testing strategy:** exhaustive unit tests for `detect_milestones` (crossing exactly one threshold, multiple thresholds in one jump, re-running with the same weight emits nothing, lose vs gain direction, idempotency via the recorded set); integration test proving a weight entry that crosses a threshold creates exactly one achievement row and a second identical entry creates none (DB unique constraint backstop); frontend test that the notification renders only when achievements are returned; E2E: weight entry crosses a milestone -> notification appears.

**Risks:** double-counting if detection is not idempotent. Defense in depth: in-memory recorded set in the detector plus the DB unique constraint. The synchronous-on-write decision (vs event-driven) is captured in ADR-0019 with its trade-offs.

### Step 3: Preferences

Implements user preferences and makes the unit preference drive display formatting before charts are built in Step 4.

**Functional requirements:** FR-P-1 (global weight-unit preference, carries Android ADR-0004), FR-P-3 (notification preferences).

**Migration:** `web/backend/alembic/versions/0005_user_preferences.py` — key-value `user_preferences` table per SRS §8.2.6, carrying forward the Android key-value design.

**Backend (create):**

- `preferences/domain/entities.py` (`Preference`), `domain/ports.py` (`PreferenceRepository`)
- `preferences/application/get_preferences.py`, `set_preference.py`
- `preferences/infrastructure/models.py`, `repositories.py`
- `preferences/interface/router.py` (`GET /api/v1/preferences`, `PUT /api/v1/preferences/{key}`), `interface/schemas.py`

**Frontend (modify — context already exists):**

- Wire the existing `web/frontend/src/contexts/PreferencesContext.tsx` to the backend (it currently exists from M2 scaffolding; connect it to `GET/PUT /preferences`)
- Real `features/settings/pages/SettingsPage.tsx` (replaces `SettingsPlaceholderPage`), `api/preferences-client.ts`, `hooks/usePreferences.ts`
- `features/settings/components/UnitPreferenceControl.tsx`, `NotificationTogglesControl.tsx`
- Update `routes.tsx` to point `/settings` at `SettingsPage`

**Testing strategy:** unit tests for use cases with a fake repository; integration tests for get/put; frontend tests that changing the unit preference updates display formatting and that toggles persist; E2E: change unit preference and confirm display updates.

**Risks:** preference key typos. Constrain valid keys (`weight_unit`, `notify_achievement`, `notify_milestone`, `notify_streak`) with a Pydantic enum at the API boundary and reject unknown keys with 422.

### Step 4: Trend and Analytics

Implements the composite indexes, the rate-of-change algorithm, and the trend chart.

**Functional requirements:** NFR-P-3 (composite indexes), FR-D-2 (trend chart), FR-D-3 (weekly rate of change). FR-D-4 progress bar was delivered in Step 1; here the dashboard aggregates it.

**ADR (write before any code in this step):** ADR-0020 Composite Index Strategy for Trend Queries.

**Migration:** `web/backend/alembic/versions/0006_performance_indexes.py` — add the composite/partial indexes SRS §7.2 (NFR-P-3) requires: `(user_id, observation_date)` and `(user_id, created_at)`, scoped `WHERE is_deleted = FALSE`. Confirm against indexes already created in migration `0002` to avoid duplicates.

**Backend (create / modify):**

- `weight_tracking/domain/rate_of_change.py` — pure function `weekly_rate_of_change(entries) -> RateOfChange`. Algorithm: sliding-window moving average over the entry series; weekly rate derived from two windowed averages resolved by two indexed lookups against the composite index. Document complexity (O(w) over the window; O(log n) index seeks).
- `weight_tracking/application/get_rate_of_change.py`
- Extend `dashboard/application/build_dashboard_summary.py` to include active-goal progress and the latest trend slice; extend `dashboard/interface/schemas.py`

**Frontend (create / modify):**

- `features/dashboard/components/WeightTrendChart.tsx` (FR-D-2) using a charting library (Recharts or equivalent — chosen in DDR-0006), with selectable ranges (7/30/90/all)
- `features/dashboard/components/RateOfChangeCard.tsx` (FR-D-3)
- Integrate `GoalProgressBar` (from Step 1) into the dashboard
- `features/dashboard/hooks/useRateOfChange.ts`; extend `features/dashboard/pages/` summary

**Testing strategy:** unit tests for `weekly_rate_of_change` (rising trend, falling trend, flat, sparse data, single entry edge case); integration test asserting the trend query plan uses the composite index (e.g., `EXPLAIN` assertion or row-count guard per NFR-P-3 "zero full table scans over 100 rows"); frontend chart tested via accessible roles and an empty-state; axe-core scan on the dashboard (NFR-A-1).

**Risks:** chart accessibility. Charts must expose a text/table alternative for screen readers (NFR-A-3) and meet contrast (NFR-A-4). Captured in DDR-0006.

### Step 5: Stretch Slices

Implemented in priority order if core lands with milestone headroom. Streak detection is first because it is the strongest remaining algorithmic showcase. Any item not reached is deferred with documented rationale in Step 6 and the narrative.

1. **Streak detection (FR-Ach-3) — ADR-0021 (write first).**
   - `achievements/domain/streak_detector.py` — pure function `detect_streaks(observation_dates: set[date], today) -> list[Streak]`. Algorithm: consecutive-day run scan over a sorted/`set`-backed date sequence; detect 7- and 30-day streaks; record idempotently via the `(goal_id, achievement_type, threshold)` constraint. Document complexity (O(n) scan when dates arrive sorted from the indexed query; O(n log n) if a sort is needed).
   - Hook into the same composition-root orchestration as Step 2 (`DetectAchievements`); extend, do not duplicate.
   - Unit tests: exact 7-day run, broken run, 30-day run, gaps, duplicate-day entries collapse to one calendar day.
2. **Achievement listing (FR-Ach-4)** — sorted-by-date-descending listing endpoint + UI (mostly delivered by Step 2's `GET /achievements`; add ordering + pagination reuse).
3. **Goal history (FR-G-5)** — list past achieved/abandoned goals; reuse `GET /api/v1/goals`.
4. **Weight unit conversion (FR-W-6)** — `shared` or `weight_tracking/domain/unit_conversion.py` pure converter (`lbs <-> kg`), driven by the preference from Step 3; display-only, original unit preserved on the row.
5. **TTL caching (NFR-P-5) — ADR-0022 (write first).**
   - `shared/cache.py` — small TTL cache for expensive, stable computed values (rate-of-change, milestone counters), with a documented TTL. Document the eviction/expiry data structure.
   - Unit tests: hit, miss, expiry, invalidation on new weight entry.

**Testing strategy:** same TDD discipline; each stretch slice ends green before the next starts.

### Step 6: Documentation and Closeout

Verification and reconciliation only — ADRs and DDRs are authored during their steps, not here.

- Verify ADR-0019 through ADR-0022 are committed (those that were reached) and listed in `docs/adr/README.md` with correct numbers and status.
- Verify DDR-0005 through DDR-0008 are committed in `docs/ddr/`.
- **Reconcile SRS v2 drift:** update Appendix A §17.2 to renumber the M3 ADRs to 0019–0022 and record 0016–0018 as the M2 remediation decisions they actually are; correct §13.2.1 deliverable 4 to mark cursor pagination as M2-delivered; update `docs/adr/README.md` index (currently stops at 0015) to include 0016–0018 plus the new M3 ADRs.
- Update the root `README.md` with the M3 feature set (goals, achievements, trends, preferences).
- Regenerate and commit the OpenAPI snapshot to `/docs/api/openapi.json` with the new goal, achievement, and preference routes.
- Self-review all M3 code against `/docs/standards/cs499_code_review_checklist.md`; record findings as PR comments and resolve before merge.
- Draft the M3 narrative addressing the four rubric prompts, with explicit emphasis on the algorithms (milestone detection, streak detection, rate-of-change) and their complexity analysis; cite cursor pagination (ADR-0015) as the data-structure exemplar; acknowledge AI-tool usage per the rubric's AI Usage section and the Shapiro Library citation guide.
- Confirm any unreached stretch items are recorded as deferred with rationale.
- Tag the repository `v0.2.0`.

**Note on ADR/DDR timing:** records must be written at the time of the decision — on the feature branch, before the first line of implementation code that depends on the decision. Step 6 is a verification step, not the authorship step. A record committed after the code it documents is a retrospective note, not a decision document.

---

## 4. New ADRs Required

Four new ADRs for M3, numbered from the next available slot (0019) because 0016–0018 are already taken by M2 remediation work. Each documents an engineering decision with viable alternatives considered and includes explicit time/space complexity analysis for the algorithm it governs. None reference course requirements as rationale. The "When to write" column is the gate.

| ID | Title | Decision Captured | When to Write |
| --- | --- | --- | --- |
| ADR-0019 | Milestone Detection Algorithm | Threshold-crossing detection at 5/10/25/50 lb from goal start; idempotency via an in-memory recorded-milestone set plus a DB unique constraint; synchronous detection on weight-entry write vs an event-driven alternative; O(k) per entry. | Before Step 2 — before writing `milestone_detector.py` |
| ADR-0020 | Composite Index Strategy for Trend Queries | Which composite/partial indexes back the trend and rate-of-change read paths and why; how rate-of-change resolves via two indexed lookups; trade-offs vs scanning. | Before Step 4 — before writing migration `0006` and `rate_of_change.py` |
| ADR-0021 | Streak Detection Algorithm | Consecutive-day run detection over a set-backed sorted date sequence; how duplicate same-day entries collapse; idempotent recording; O(n) scan trade-offs. | Before the streak slice in Step 5 — before writing `streak_detector.py` |
| ADR-0022 | TTL-Based Server-Side Caching Strategy | What is cached (rate-of-change, milestone counters), the TTL, the expiry data structure, and invalidation triggers; trade-offs vs recompute-on-read. | Before the caching slice in Step 5 — before writing `shared/cache.py` |

SRS Appendix A §17.2 is updated in Step 6 to reflect this numbering.

---

## 5. New DDRs Required

Per the project rule that any UI change gets a Design Decision Record, four DDRs accompany the M3 frontend work, numbered from the next available slot (existing DDRs run 0001–0004). Each is written before its UI is built.

| ID | Title | When to Write |
| --- | --- | --- |
| DDR-0005 | Goal progress visualization (progress-bar pattern) | Before Step 1 frontend |
| DDR-0006 | Weight trend chart (charting library choice, range selector, screen-reader alternative) | Before Step 4 frontend |
| DDR-0007 | Achievement notification (modal vs banner, motion, ARIA live region) | Before Step 2 frontend |
| DDR-0008 | Settings/preferences page layout | Before Step 3 frontend |

---

## 6. M3-Specific Constraints

Project-wide constraints — TDD discipline, security baseline, strict typing, import linters, branching strategy, lint/test gates, and commit conventions — are specified in the SRS (§7 Non-Functional Requirements and §12 DevOps and Tooling) and the repository's contribution guidelines. Refer to them for execution rules.

M3-specific additions:

- Each algorithm (milestone detection, streak detection, rate-of-change, goal progress) is written first as a pure domain function with in-memory fakes, with zero framework imports, and is verified by the existing architectural import test (`tests/architecture/test_import_contracts.py`).
- Each algorithm states its time and space complexity in its docstring and in its governing ADR — this is the rubric's "algorithms and data structures" evidence.
- Cross-domain coordination (weight entry triggering achievement detection) happens at the interface/composition-root layer; no domain package imports another domain package.
- **Security thread (rubric indicator).** Every new resource (goals, achievements, preferences) is scoped to the authenticated user. Cross-user access returns 404 Not Found — never 403 and never another user's data — closing the insecure-direct-object-reference (IDOR) class of logical/structural flaw, mirroring the M2 weight-entry pattern. All new endpoints validate inputs with Pydantic at the boundary (NFR-S-4); the preferences endpoint rejects unknown keys with 422. This is the security flaw the M3 rubric looks for and is given explicit narrative treatment.
- All four ADRs and four DDRs that are reached must be written before the code they govern, not after, and before the `v0.2.0` tag is applied.
- The narrative must acknowledge AI-tool usage per the rubric's AI Usage section.

---

## 7. Definition of Done

Adapted from SRS §14 for Milestone Three:

- [ ] All core M3 functional requirements (§1.1) are implemented with passing tests written test-first
- [ ] Stretch items are either implemented or deferred with documented rationale
- [ ] Coverage thresholds met per SRS §11.5 (backend domain 95%/90%, application 90%/85%; frontend 90%/90%)
- [ ] CI is green on every relevant workflow
- [ ] ADR-0019 through ADR-0022 (those reached) are written, committed, and indexed in `docs/adr/README.md`
- [ ] DDR-0005 through DDR-0008 (those reached) are committed in `docs/ddr/`
- [ ] SRS v2 drift reconciled (Appendix A numbering, §13.2.1 cursor note, ADR README index)
- [ ] Code self-reviewed against `/docs/standards/cs499_code_review_checklist.md`
- [ ] OpenAPI snapshot regenerated to `/docs/api/openapi.json` with goal, achievement, and preference routes
- [ ] Root `README.md` updated with the M3 feature set
- [ ] All new resources are user-scoped; cross-user access returns 404 (IDOR prevention), verified by tests
- [ ] All existing M2 tests (including cursor pagination, FR-W-2) still pass
- [ ] The M3 narrative document is drafted and reviewed against the rubric, with algorithm complexity emphasized and AI usage acknowledged
- [ ] The repository is tagged `v0.2.0`

---

## 8. Out of Scope

The following are explicitly NOT in M3. They are deferred to later milestones or out of capstone entirely.

| Item | Deferred To |
| --- | --- |
| Audit log schema and write strategy | M4 (Databases) |
| CHECK constraint inventory and database-level validation hardening | M4 |
| Backup and restore procedure | M4 |
| SMS notifications (FR-N-2) | Out of capstone / Final stretch |
| Email notifications (FR-N-3) | Out of capstone / Final stretch |
| Password change (FR-A-6), password reset (FR-A-7), account deactivation (FR-A-8) | Final |
| Theme preference — light/dark/system (FR-P-2) | Final |
| User data export (NFR-Priv-3) and deletion (NFR-Priv-4) | Final |
| Cloud deployment (AWS, GCP, Azure) | Out of capstone |
| Infrastructure-as-code tooling | Out of capstone |
| Native mobile rebuild | Out of capstone |
| Real-time features (websockets, server-sent events) | Out of capstone |

---

**End of Brief**
