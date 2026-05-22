# Summary

This file is the durable, reverse-chronological narrative log for the CS 499
capstone work on this repository. The newest entry is at the top. Each entry
records what was done, how it was done, any issues encountered, and how those
issues were resolved.

---

## [2026-05-22 12:10] Commit Summary

**Change Type:** Fix
**Scope:** frontend/components

**Summary:**
Add explicit `: never` return type to ThrowingComponent in ErrorBoundary.test.tsx to satisfy TypeScript's strict JSX element type requirements.

**Rationale:**
TypeScript requires JSX components to return ReactNode | Promise<ReactNode>. A function that unconditionally throws must be typed as returning never, which is assignable to ReactNode. Without this, tsc reports TS2786 under strict mode.

**References:**
- Issue: Phase 5 frontend architecture

---

## [2026-05-22 12:09] Commit Summary

**Change Type:** Feature
**Scope:** frontend/App

**Summary:**
Wire App.tsx with React Router 6 route hierarchy and ProtectedRoute redirect wrapper. Update main.tsx to wrap the app in BrowserRouter, QueryClientProvider, AuthProvider, and PreferencesProvider. All 88 tests pass.

**Rationale:**
Separating BrowserRouter into main.tsx (rather than App.tsx) allows integration tests to supply a MemoryRouter. The ProtectedRoute component reads isAuthenticated from AuthContext and redirects unauthenticated users to /login?from=<original-path>, preserving the intended destination for Phase 6 to use after login.

**References:**
- Issue: Phase 5 frontend architecture

---

## [2026-05-22 12:08] Commit Summary

**Change Type:** Test
**Scope:** frontend/App

**Summary:**
Update App.test.tsx with full integration tests: full provider setup, route-specific page heading assertions (/login → Log In, /register → Create Account), and unauthenticated redirect verification for protected routes.

**Rationale:**
TDD red step for the App wiring subtask. The new tests verify that the router renders the correct page per URL, which the current stub App.tsx cannot satisfy.

**References:**
- Issue: Phase 5 frontend architecture

---

## [2026-05-22 12:07] Commit Summary

**Change Type:** Feature
**Scope:** frontend/pages

**Summary:**
Implement all placeholder pages (Goals, Achievements, Settings) and stub pages (Login, Register, Dashboard, WeightHistory, WeightEntryForm). Fix MUI Typography subtitle1 default HTML element (h6) by adding component="p" on placeholder subtitles to prevent spurious duplicate heading assertions.

**Rationale:**
MUI Typography subtitle1 maps to h6 in the default variantMapping, which would produce two heading elements per placeholder page and break the getByRole('heading') assertions. Using component="p" is semantically correct — the "Coming in Milestone 3" notice is a descriptive paragraph, not a section heading.

**References:**
- Issue: Phase 5 frontend architecture

---

## [2026-05-22 12:05] Commit Summary

**Change Type:** Test
**Scope:** frontend/pages

**Summary:**
Add failing tests for all placeholder pages (Goals, Achievements, Settings) and stub pages (Login, Register, Dashboard, WeightHistory, WeightEntryForm). Tests verify render-without-crash, accessible heading presence, and "Coming in Milestone 3" notice on placeholder pages.

**Rationale:**
TDD red step for the page layer. The "Coming in Milestone 3" assertion ensures placeholder pages are real, informative components rather than empty files.

**References:**
- Issue: Phase 5 frontend architecture

---

## [2026-05-22 12:04] Commit Summary

**Change Type:** Feature
**Scope:** frontend/lib

**Summary:**
Implement api-client (fetchJson + ApiError), error-mapping (mapApiError), and format (formatWeight, formatDate) utilities. Fix a floating-point precision error in the rounding test (70.55 → 70.56 as the test input).

**Rationale:**
The floating-point fix reflects a real IEEE 754 behavior: 70.55 cannot be represented exactly in binary floating-point, so toFixed(1) produces '70.5' rather than '70.6'. Using 70.56 reliably rounds up. The api-client design matches SRS §10.3 (thin fetch wrapper, typed error, JSON Content-Type enforced).

**References:**
- Issue: Phase 5 frontend architecture

---

## [2026-05-22 12:03] Commit Summary

**Change Type:** Test
**Scope:** frontend/lib

**Summary:**
Add failing tests for api-client (fetchJson), error-mapping (mapApiError), and format (formatWeight, formatDate) utilities.

**Rationale:**
TDD red step for the lib layer. Tests drive minimal, focused contracts: fetchJson throws on non-2xx and sets Content-Type; mapApiError returns distinct strings for 401/409/422/500; formatWeight produces fixed decimal notation; formatDate returns a human-readable string.

**References:**
- Issue: Phase 5 frontend architecture

---

## [2026-05-22 12:02] Commit Summary

**Change Type:** Feature
**Scope:** frontend/components

**Summary:**
Implement AuthLayout, AppLayout, NavList, EmptyState, LoadingSpinner, and ErrorBoundary. Also fix test isolation by adding explicit cleanup() calls to the Vitest setup file, and add the inline MenuIcon SVG to AppLayout to avoid an @mui/icons-material ESM directory-import issue in the jsdom environment.

**Rationale:**
@mui/icons-material 6.x uses .mjs entry points that reference @mui/material/SvgIcon as a bare directory import, which Node ESM resolution does not support without an explicit /index.js suffix. Using an inline SvgIcon avoids the dependency and keeps the test environment stable. The cleanup() fix ensures each test gets a pristine DOM, eliminating the "Found multiple elements" false failures from cross-test DOM leakage.

**References:**
- Issue: Phase 5 frontend architecture

---

## [2026-05-22 11:58] Commit Summary

**Change Type:** Test
**Scope:** frontend/components

**Summary:**
Add failing tests for AuthLayout, AppLayout, NavList, EmptyState, LoadingSpinner, and ErrorBoundary. Tests cover render-without-crash, accessible roles, children rendering, and conditional visibility.

**Rationale:**
TDD red step for the shared layout and utility component layer. Accessible-query tests (role, text) ensure WCAG 2.1 AA compliance is verifiable from the test suite itself.

**References:**
- Issue: Phase 5 frontend architecture

---

## [2026-05-22 11:57] Commit Summary

**Change Type:** Feature
**Scope:** frontend/contexts

**Summary:**
Implement AuthContext and PreferencesContext. AuthContext holds user / isAuthenticated state and exposes login / logout actions. PreferencesContext holds weightUnit and colorScheme with a partial-merge setter. Both use useCallback + useMemo to keep reference stability and throw a descriptive error when accessed outside their provider.

**Rationale:**
In-memory context state is sufficient for Phase 5 routing scaffolding. Phase 6 will connect login/logout to the API and persist preferences to localStorage. Keeping Phase 5 self-contained prevents entangling the routing scaffold with API concerns.

**References:**
- Issue: Phase 5 frontend architecture

---

## [2026-05-22 11:56] Commit Summary

**Change Type:** Test
**Scope:** frontend/contexts

**Summary:**
Add failing tests for AuthContext and PreferencesContext. Tests cover the initial state (null user, lbs / light defaults), login/logout state transitions, partial preference updates, and provider-boundary enforcement.

**Rationale:**
TDD red step. Tests drive the exact contract the context implementations must satisfy, preventing scope creep and ensuring the API is fully testable in isolation from the router.

**References:**
- Issue: Phase 5 frontend architecture

---

## [2026-05-22 11:55] Commit Summary (routes implementation)

**Change Type:** Feature
**Scope:** frontend/routes

**Summary:**
Implement routes.tsx with typed RouteConfig interface and publicRoutes / protectedRoutes arrays covering all SRS §10.1 paths. All route declaration tests pass.

**Rationale:**
Centralising route declarations in a single typed module makes the routing contract testable without mounting the router. The iconName field is a string to keep this module free of MUI imports — NavList resolves the icon component dynamically.

**References:**
- Issue: Phase 5 frontend architecture

---

## [2026-05-22 11:55] Commit Summary

**Change Type:** Test
**Scope:** frontend/routes

**Summary:**
Add failing tests for the route declaration module, verifying that publicRoutes and protectedRoutes arrays exist with entries for all required paths.

**Rationale:**
TDD red step: tests must fail before the implementation exists. Tests verify the shape of route declarations (path string property) and the presence of all routes required by SRS §10.1.

**References:**
- Issue: Phase 5 frontend architecture

---

## [2026-05-22 11:54] Commit Summary

**Change Type:** Feature
**Scope:** frontend/dependencies

**Summary:**
Add react-router-dom v6, react-hook-form v7, zod v3, and @tanstack/react-query as production dependencies for the Phase 5 frontend architecture.

**Rationale:**
These libraries implement the technology stack specified in SRS §4.3.1 and §10. React Router v6 replaces the hardcoded navigation chain from the Android predecessor. Zod provides runtime type validation shared with TypeScript types.

**References:**
- Issue: Phase 5 frontend architecture

---

## [2026-05-22 00:00] Commit Summary

**Change Type:** Feature
**Scope:** backend/architecture

**Summary:**
Scaffold the four domain folders (auth, goals, users, weight_tracking) and shared/ package under the screaming architecture layout. Each domain has domain/, application/, infrastructure/, interface/ sub-layers per the Clean Architecture dependency rule. All __init__.py files carry docstrings that describe the layer's permitted imports and responsibilities.

**Rationale:**
The Screaming + Clean + Hexagonal architecture combination (SRS §4.2) makes the application's purpose visible at the folder level and enforces a strict dependency rule that keeps the domain core free of framework coupling. Adding docstrings ensures every empty package communicates its contract immediately to any engineer who opens it.

**References:**
- Issue: Phase 4 backend architecture

---

## Phase 3 — Web Scaffold (2026-05-22)

**What was done**

- Stood up runnable but otherwise empty frontend and backend skeletons
  for the web rebuild, so that later feature phases inherit a complete
  toolchain. Tracked as issue #9, the third phase of Milestone Two.
- Scaffolded the backend under `web/backend/`: a uv-managed FastAPI
  project using a `src/weighttogo/` package layout, with ruff, mypy in
  strict mode, and pytest configured. Added an environment-driven
  settings module, a `GET /health` endpoint reporting service status
  and the active environment, an Alembic migration harness (no
  migrations authored yet), and a Docker Compose definition for a local
  PostgreSQL 16 database.
- Scaffolded the frontend under `web/frontend/`: a Vite project using
  React 19 and TypeScript in strict mode, with ESLint and Prettier,
  Vitest and React Testing Library, and Playwright for end-to-end
  tests. Added the Material UI theme carrying the design-system teal
  palette and a root application component mounted through the theme
  provider.
- Added a single pre-commit hook manager covering both stacks, and four
  path-filtered GitHub Actions workflows: backend CI, frontend CI,
  end-to-end tests, and a daily dependency security audit.
- Updated the repository README with an accurate web-application status
  and quickstart instructions for both stacks.

**How it was done**

- Branched `feature/m2-phase-3-web-scaffold` from `main` and worked in
  sixteen small, atomic commits, one per subtask.
- The three units with genuine behavior — the backend settings module,
  the `/health` endpoint, and the frontend theme and application
  component — were developed test-first on a red-green cycle.
  Configuration, which has no behavior to assert, was verified by
  running its tools: ruff, mypy, tsc, eslint, prettier, the two dev
  servers, the database container, and the Alembic harness.
- Two decisions shaped the scaffold: the `/health` endpoint was kept
  minimal (status and environment only), with the fuller health check
  deferred until the database session layer exists; and a single
  pre-commit framework runs both stacks' linters, because Git exposes
  only one pre-commit slot and two hook managers would conflict.
- Both stacks were verified end to end: the backend dev server serves
  `/health`, the PostgreSQL container reports healthy, and Alembic
  applies cleanly against it; the frontend builds, unit tests pass, and
  a Playwright run drives the application in a real browser.

**Issues encountered**

- The Playwright end-to-end test surfaced a runtime failure that the
  unit tests had not: the Material UI theme provider received a second
  React instance because the development bundler split React across
  separate pre-bundles. It was resolved by pre-bundling React, the
  styling library, and Material UI together and deduplicating React in
  the bundler configuration.
- The frontend linting, test, and UI-library dependencies were briefly
  installed into a stray package manifest at the repository root rather
  than under `web/frontend/`, leaving them undeclared in the frontend
  manifest. The error was caught before the work shipped; the stray
  root files were removed and every dependency consolidated into
  `web/frontend/`, verified with a clean install from the lockfile.

**Documentation**

- The README web-application section was rewritten from a placeholder
  note into an accurate status with backend and frontend quickstarts.
- `CONTRIBUTING.md` was reviewed and remains accurate for the Android
  workflow; it does not yet cover web-stack development or the
  pre-commit hooks, which are recommended for a later documentation
  pass.

**Reviews**

- Three review passes — code, adversarial, and security — were run on
  the branch before the merge gate.
- The code and adversarial reviews both flagged that the backend pinned
  Python 3.13 while the project targets 3.12; the pin was corrected to
  3.12 so the declared minimum is the version actually run. The
  adversarial review confirmed the scaffold is architecture-neutral —
  it introduces no organize-by-technical-layer folders and does not
  pre-empt the later domain-architecture phase. A clarifying comment
  was added to the Vite config explaining why React, the styling
  library, and Material UI are pre-bundled together.
- The security review found no committed secrets, no workflow
  script-injection, and least-privilege workflow permissions. Its
  recommendation to pin third-party CI actions to commit SHAs was
  applied repository-wide: every action across all five workflows and
  the ruff pre-commit hook is now pinned to a commit SHA with a version
  comment.
- A naming inconsistency the reviews raised — the database identifier
  `weightogo` versus the Python package `weighttogo` — was resolved by
  standardizing the web project on `weighttogo`. The database
  identifiers, the `.env.example`, the Docker Compose definition, and
  the SRS examples were all updated to match. The preserved Android
  artifact keeps its own `weightogo` package and is unaffected.
- A subsequent maximum-effort review pass — five finder angles plus a
  gap sweep — surfaced thirteen further findings, all addressed before
  merge. The substantive fixes: application settings are now built
  lazily, so a misconfigured environment no longer crashes every
  importer; the Alembic environment passes the database URL straight to
  the engine, immune to ConfigParser interpolation of characters such
  as a percent sign; end-to-end specs are type-checked; ESLint enforces
  React JSX rules through eslint-plugin-react, which moved ESLint to the
  current stable 9 line; and the pre-commit, Playwright, Docker Compose,
  and CI configurations were each hardened.

---

## Phase 2 Follow-up — Documentation Hygiene (2026-05-22)

**What was done**

- Cleared repository-wide documentation debt that the Phase 2
  documentation sweep surfaced and that was deliberately scoped out of
  the restructure pull request (#19) to keep that change focused.
  Tracked as issue #20; with this work merged, Phase 2 is complete.
- Removed every live AI-tool reference from committed documentation: a
  tooling-attribution line in the Android code quality audit, two
  references in the Milestone Two brief, an attribution and a local
  tool-config path in the Phase 7 SMS testing guide, a local
  tool-config path in the Phase 8 manual test scenarios, and an aside
  in the SRS introduction.
- Removed every citation of the root project instruction file from
  other documentation: three reference-table rows and a constraints
  paragraph in the Milestone Two brief, roughly two dozen citations in
  the Android code quality fix plan (violation labels, workflow
  references, and example-commit-message footers), and one in the
  manual testing checklist.
- Repaired corrupted shell commands across three testing documents
  (two manual-testing command guides and the testing-directory
  README). A botched find/replace had merged the Android application
  package token into adjacent words, dropped a path separator, and —
  in one guide — left a misspelled package name and a wrong database
  filename. Restructure-induced build, source, and data paths were
  corrected, and a post-restructure path note was added to each
  repaired guide.
- Corrected retired-tracker references (`TODO.md`,
  `project_summary.md`) in the actively-maintained testing-directory
  README, while leaving such references intact in frozen historical
  material where they accurately record the project's state at the
  time of writing.
- Replaced a `v2.x` milestone-release version scheme with honest
  `0.x` development versioning across the SRS and the Milestone Two
  brief, since the web application is in initial, pre-1.0 development.
- Delivered as PR #21, branch `docs/m2-phase-2-doc-hygiene`.

**How it was done**

- Branched `docs/m2-phase-2-doc-hygiene` from the latest `main` after
  the Phase 2 restructure pull request merged.
- A read-and-verify documentation sweep opened every in-scope document
  in full; repository-wide searches then confirmed that issue #20's
  diagnosis of AI-tool and instruction-file references was complete.
- The repository owner chose, per file, to repair the corrupted
  command guides in place rather than archive or delete them. Ground
  truth for the repair — application package, Gradle module name,
  launcher activity, and database filename — was read directly from
  the Android sources.
- The corrupted commands were repaired with a scripted, systematic
  pass and then verified line by line.
- The retired-tracker policy was applied by classification: frozen
  historical documents keep their references as accurate history;
  actively-maintained documents have them corrected.
- Work was committed as a sequence of small, atomic commits, one per
  debt category.
- Three review passes — code, adversarial, and security — were run on
  the branch; their findings are recorded below.

**Issues encountered**

- The read-and-verify sweep found one AI-tooling reference in the SRS
  introduction that issue #20's original diagnosis had not listed.
- The corruption in the testing commands was more systematic than
  stale paths: a find/replace had merged shell tokens, dropped a path
  separator, misspelled the package name, and used the wrong database
  filename.
- The adversarial review found a third corrupted snippet — in the
  testing-directory README — and one restructure-stale path that the
  first repair pass had missed.
- The adversarial review also flagged the same wrong package and
  database names in a test-helper script outside this issue's
  documentation scope.

**How issues were resolved**

- The additional SRS reference was surfaced to the repository owner,
  who chose to remove it; it was removed alongside the other AI-tool
  references.
- The corrupted commands were repaired against ground truth from the
  Android sources and verified to contain no residual corruption.
- The third corrupted snippet and the stale path from the adversarial
  review were repaired the same way in follow-up commits and
  re-verified.
- The out-of-scope script defect was surfaced to the repository owner
  as a separate decision rather than folded into this issue.

---

## Phase 2 — Repository Restructure (2026-05-21)

**What was done**

- Restructured the repository from an Android-only layout into a polyglot
  monorepo: the entire Android Gradle project moved from the repository root
  into `android/`, and `web/frontend/` and `web/backend/` were created as
  tracked placeholders for the web rebuild.
- Tagged `v1.0.0-android` on the final pre-restructure commit of `main`,
  marking the end of the Android-only era. The restructure commit itself is not
  separately tagged — it is a structural change, not a release.
- Updated the Android CI workflow to build from `android/`, corrected its
  report and artifact paths, and path-filtered its triggers so it runs only for
  Android changes.
- Extended `.gitignore` with Python and Node sections ahead of the web stack.
- Added ADR-0007 (rebuild as a full-stack web application) and ADR-0008
  (polyglot monorepo); renumbered the SRS ADR index and every in-text ADR
  reference to the seven-ADR M2 set.
- Rewrote the root `README.md` around the monorepo layout and the mobile-to-web
  narrative, resolving the two pre-existing `README.md` defects flagged in
  Phase 1 — the broken `TODO.md` links and the stale project-structure tree.
- Pointed the CONTRIBUTING Android setup instructions at the new `android/`
  path.
- Delivered as PR #19, branch `feature/m2-phase-2-repo-restructure`.

**How it was done**

- Branched `feature/m2-phase-2-repo-restructure` from the latest `main`.
- Every Android file was relocated with `git mv` so the move is recorded as a
  set of pure renames; `git log --follow` confirmed that history, blame, and
  log all trace through the move.
- The relocated Android build was verified before any further change:
  `./gradlew test`, `lint`, and `assembleDebug` all pass at the new path with
  no source modifications.
- The work was committed as a sequence of small, atomic commits — the move, the
  CI change, the web scaffold, the ignore rules, the ADRs, the SRS renumber,
  and the documentation updates each as their own commit.
- A documentation sweep was run as the pre-push gate, updating the README,
  CONTRIBUTING, the SRS, and this log.
- Three review passes — code, adversarial, and security — were run on PR #19;
  their findings are recorded below.

**Issues encountered**

- `local.properties` was listed for relocation but is machine-specific and
  git-ignored, so it could not be moved with `git mv`.
- The Android CI workflow's report and artifact paths referred to a module
  named `app`, but the actual module is `weightogo` — a stale reference that
  predated this phase.
- The SRS carried two ADR cross-references that pointed at the wrong ADR
  independently of the renumbering.
- A thorough documentation sweep surfaced pre-existing documentation debt wider
  than this phase's scope: corrupted command snippets in `docs/testing/`, live
  AI-tool references and project-instruction-file citations in several committed
  documents, and retired tracker references.
- The review passes flagged three documentation and configuration gaps: the
  expanded `.gitignore` did not ignore `.env` files; the README
  repository-layout tree omitted several directories; and the SRS ADR-index
  subsection was still headed "Planned" although two of its ADRs are now
  written.

**How issues were resolved**

- `local.properties` was excluded from the tracked move and copied into
  `android/` instead, where the existing ignore rule still covers it; the
  Android build locates the SDK correctly at the new path.
- The CI paths were corrected to `android/weightogo/build/...` in the same
  change that repointed the workflow at the new directory, fixing the stale
  module name and the new path layer together.
- The two mis-targeted SRS references were corrected to their proper ADRs while
  the index was renumbered, leaving the SRS internally consistent.
- That debt predates this phase. It is tracked as Phase 2 follow-on work in
  issue #20 — a dedicated documentation-hygiene pass delivered as its own pull
  request — rather than expanding the restructure PR.
- The three review findings were resolved on the PR: an `.env` ignore rule was
  added (with `.env.example` kept tracked), the README layout tree was
  completed, and the SRS subsection heading was corrected. The security pass
  found no vulnerabilities.

---

## Phase 1 — Tracking Log Scaffold (2026-05-21)

**What was done**

- Added this `SUMMARY.md` file at the repository root: the durable,
  reverse-chronological narrative log for the milestone, with the newest entry
  prepended at the top.
- Seeded the log with two entries — this Phase 1 entry and the Phase 0 entry
  below it — so the record is complete from the start of the milestone.
- Delivered as PR #18, branch `docs/m2-phase-1-summary-scaffold`.

**How it was done**

- Branched `docs/m2-phase-1-summary-scaffold` from the latest `main`.
- The Phase 0 entry was carried forward from the breakdown prepared at the close
  of Phase 0 and recorded on the Phase 1 tracking issue (#7), then verified
  against the merged Phase 0 pull request before inclusion; no changes were
  needed.
- The file was checked through the GitHub Markdown renderer to confirm both
  entries display correctly.
- A documentation sweep was run as the pre-push gate. It confirmed `SUMMARY.md`
  is the only document this phase needs to add or change. The sweep also noted
  pre-existing staleness in the root `README.md` — a project-structure tree
  predating the repository restructure, and two links to the retired `TODO.md`
  task tracker — which is out of scope for this phase and is left for the README
  revisions scheduled in the repository-restructure phase (Phase 2) and the
  documentation-closeout phase (Phase 9).
- Three review passes — code, adversarial, and security — were run on PR #18.

**Issues encountered**

- None arose in this phase's own work: adding a single documentation file raised
  no blocker or defect, and there is no application code, test, or build impact.
  The documentation sweep's observation about pre-existing `README.md` staleness,
  noted above under "How it was done", is a deferred out-of-scope item rather
  than an issue in this phase.

**How issues were resolved**

- Not applicable.

---

## Phase 0 — Repository & Project Setup (2026-05-21)

**What was done**

- Renamed the working repository on GitHub: `rgoshen-snhu/cs360-WeightToGoMobile`
  → `rgoshen-snhu/WeighToGo`; updated the local `snhu` remote and the `gh`
  default repo.
- Stood up GitHub project tracking: a Project board ("WeighToGo — CS 499
  Capstone"), four epic issues (M2 #2, M3 #3, M4 #4, Final #5), and ten M2 phase
  issues (Phases 0–9, issues #6–#15) attached as sub-issues of the M2 epic.
- Updated old repository-name references in the SRS, README, and CONTRIBUTING;
  fixed a broken CI badge and placeholder repository URLs.
- Added a `## Tasks` section to the issue templates; relocated the Android
  development journal to `docs/history/android_summary.md` and documented the
  new directory with a README.
- Removed two unused legacy GitHub Actions workflows left from an earlier
  integration setup.
- Delivered as PR #16, branch `chore/m2-phase-0-repo-project-setup`.

**How it was done**

- Repository renamed with `gh repo rename`; GitHub's automatic old-URL redirect
  verified (HTTP 301).
- Board, epics, and phase issues created with the `gh` CLI; phase issues linked
  as sub-issues via the GitHub sub-issue API; all issues added to the board.
- Documentation edits were surgical — only repository-name references were
  changed; historical mentions in the SRS naming-considerations narrative were
  deliberately preserved.
- The core change was committed as two atomic commits (`chore:` templates +
  journal relocation, `docs:` repo-name updates), with follow-up commits for
  review findings and owner-directed changes.
- Three review passes — code, adversarial, and security — were run on PR #16.

**Issues encountered**

- The `gh` token lacked the `project` OAuth scope, blocking Project board
  creation.
- The journal relocation broke a relative link in `docs/testing/README.md`
  (review finding W1).
- Two unused legacy GitHub Actions workflows were present; the automated review
  workflow failed on every pull request for lack of a configured token secret.
- The newly created `docs/history/` directory was initially undocumented
  (adversarial review note N1).
- Phase 0 expanded beyond the original plan during execution, at the repository
  owner's direction.

**How issues were resolved**

- The owner refreshed the `gh` token with the `project` scope.
- W1 was fixed during the phase — the link was repointed to
  `../history/android_summary.md`.
- The two legacy workflows were removed (owner-directed) after verifying they
  had no branch-protection or file dependencies.
- A README was added for `docs/history/`, resolving N1.
- Broader `docs/` indexing was captured as a separate tracked issue (#17) under
  the M2 epic rather than expanding Phase 0 further.

## [2026-05-22 21:15] Commit Summary

**Change Type:** Docs
**Scope:** srs/tech-stack

**Summary:**
Update SRS §4.3.1 frontend tech stack to reflect actual installed versions: TypeScript 6, React 19, MUI 9, React Router 7, Vite 8, Vitest 4.1, Playwright 1.60, ESLint 9, Prettier 3.8. Correct state management entry to reflect TanStack Query v5.

**Rationale:**
The SRS should document what the project actually runs. Floor versions like "6+" give agents license to use outdated releases, which conflicts with the project policy of using latest stable versions.

**References:**
- Issue: SRS consistency
