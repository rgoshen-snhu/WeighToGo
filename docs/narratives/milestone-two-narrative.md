# Milestone Two Narrative — Software Design and Engineering

**Course:** CS 499, Computer Science Capstone — Southern New Hampshire University
**Milestone:** Two (Enhancement Category One — Software Design and Engineering)
**Artifact:** Weigh to Go! — repository <https://github.com/rgoshen-snhu/WeighToGo>
**Tag:** `v0.1.0` (this milestone) · prior baseline `v1.0.0-android`
**Author:** Rick Goshen

> Render to Word for submission:
>
> ```bash
> cd docs/narratives
> pandoc milestone-two-narrative.md -o milestone-two-narrative.docx \
>     --reference-doc=reference.docx   # optional — for SNHU style
> ```
>
> The `.docx` output is git-ignored (see `.gitignore`); the markdown is the
> single source of truth.

---

## 1. Briefly describe the artifact. What is it? When was it created?

The artifact is **Weigh to Go!**, a weight-tracking application I originally
built as a native Android app for **CS 360 (Mobile Architecture and
Programming)** in 2025. The Android version uses Java, the Android SDK,
SQLite for local persistence, and Material Components for the UI. Its
feature set covers user registration and login, daily weight logging with
unit selection, weight history, goal setting and progress tracking, push and
SMS notifications for goal achievements, and basic accessibility settings.

For the CS 499 capstone I have rebuilt Weigh to Go! as a **full-stack web
application** while preserving the original Android codebase in the same
repository as a historical artifact. The web rebuild uses **React 19 with
TypeScript** and Material UI v9 on the frontend, **FastAPI on Python 3.12**
with SQLAlchemy 2.0 and Pydantic v2 on the backend, and **PostgreSQL** for
persistence. Both stacks live in a polyglot monorepo: `android/` holds the
preserved Java code and `web/` holds the new Python and TypeScript code.

This narrative covers **Milestone Two (Software Design and Engineering)**,
which delivered the architectural foundation, the authentication system,
weight-entry CRUD, and the dashboard summary — the vertical slice that
proves the architecture works end-to-end. Milestone Two is tagged `v0.1.0`.

---

## 2. Justify the inclusion of the artifact in your ePortfolio

### Why this artifact

I selected Weigh to Go! because the original Android version, while
functionally complete for CS 360, surfaced concrete architectural debt under
a structured engineering code review I performed at the start of the
capstone. The findings — over-large activity classes with single-responsibility
violations, model-view-controller drift, database writes executed on the UI
thread, an `ExecutorService` lifecycle defect, unmasked personally identifiable
information in logs, username enumeration through differentiated authentication
error messages, a hardcoded navigation chain, and accessibility gaps — were
architectural rather than incidental. Patching them in place would have left
the underlying design problems unchanged. Rebuilding as a full-stack web
application lets me address every finding through deliberate design rather
than incremental repair, while also demonstrating modern web engineering
practices that are directly relevant to my career goals.

### Components that showcase software-engineering skills

The Milestone Two work showcases the following:

- **Three-pattern backend architecture** (`web/backend/src/weighttogo/`) combining
  Screaming Architecture (folder structure named after bounded contexts —
  `auth/`, `weight_tracking/`, `goals/`, `users/`), Clean Architecture (the
  dependency rule, enforced in CI by `import-linter` — domain code with any
  framework import breaks the build), and Hexagonal Architecture (ports
  defined in the domain, adapters in `infrastructure/`). The decision is
  documented in [ADR-0012](../adr/0012-three-pattern-backend-architecture.md).

- **Security baseline applied from the first commit.** Email as the primary
  user identifier ([ADR-0009](../adr/0009-email-as-primary-user-identifier.md)),
  generic authentication error messages to prevent username enumeration
  ([ADR-0010](../adr/0010-generic-authentication-error-policy.md)), PII
  masking in every log statement ([ADR-0011](../adr/0011-pii-masking-strategy-in-logs.md)),
  refresh-token rotation with family-based revocation to detect token replay
  ([ADR-0013](../adr/0013-refresh-token-rotation-family-revocation.md)),
  bcrypt password hashing at cost 12, account lockout, and rate-limited auth
  endpoints — every finding from the Android code review is addressed by a
  specific countermeasure with a specific test.

- **Test-driven development discipline throughout.** The Milestone Two diff
  is 544 files / +28,479 / −598 lines across 173 commits. It carries **277
  backend tests** (pytest) and **241 frontend test cases** (vitest) plus
  five end-to-end Playwright specs, with coverage at or above the SRS §11
  threshold. Every feature was written test-first; the commit history shows
  the red-green-refactor cadence.

- **RFC 7807 problem-details error responses** on every API path, with
  field-level validation detail for 422 responses. Both the backend
  emission and the frontend parsing are tested.

- **Cursor-based pagination** with an opaque compound cursor
  ([ADR-0015](../adr/0015-opaque-compound-cursor-pagination.md)) — surfaced
  during PR #30 review when the first-cut cursor leaked schema and skipped
  rows at page boundaries. Authoring an ADR mid-PR captured both the bug
  and the corrected design in one place.

- **Documentation discipline.** A versioned Software Requirements
  Specification ([`/docs/specs/WeighToGo_Web_SRS_v1.md`](../specs/WeighToGo_Web_SRS_v1.md))
  is the authoritative source for architecture, requirements, API, and
  quality gates. Nine new Architecture Decision Records (ADR-0007 through
  ADR-0015) capture every M2 decision with alternatives considered. A
  reverse-chronological `SUMMARY.md` records the rationale and bug-fix
  context for every commit.

### How the artifact was improved

The web rebuild resolves every finding from the Android code review through
deliberate design. The architectural changes — three-pattern backend, ports
and adapters, async I/O, structured logging — eliminate the structural
debt rather than patching around it. The security improvements close the
PII-exposure and enumeration vulnerabilities. The TDD discipline produces
a regression-tested codebase rather than a hand-tested one. The OpenAPI
snapshot generated by the FastAPI app provides a machine-readable API
contract that future clients (a mobile rebuild, a third-party integration)
can consume without ambiguity.

---

## 3. Did you meet the course outcomes you planned to meet in Module One?

The Milestone Two work targets three of the five program outcomes most
directly, and makes incidental progress on the other two.

**Outcome 4 (well-founded techniques and tools for solutions that deliver
value) — Met.** The web rebuild uses React, TypeScript, FastAPI, Pydantic,
SQLAlchemy, PostgreSQL, Vite, ruff, mypy, eslint, prettier, pre-commit, and
Playwright — every choice is current and industry-standard. The three-pattern
backend, the strict typing on both stacks, and the test-driven cadence
demonstrate engineering practices that scale beyond a course project.

**Outcome 5 (security mindset) — Met.** The authentication system addresses
every security finding from the Android code review with an explicit
countermeasure and an explicit test. Bcrypt password hashing, refresh-token
rotation with family revocation, generic error messages, PII masking, rate
limiting, account lockout, strict CORS, and security headers are all in
place from the first commit, documented in ADRs, and verified by tests.

**Outcome 2 (professional-quality written and visual communication) — Met.**
The SRS, the ADRs, the API documentation auto-generated from the OpenAPI
schema, the README, the CONTRIBUTING guide, the ARCHITECTURE summary, the
documentation index, and this narrative collectively demonstrate the
ability to communicate engineering decisions in writing to multiple
audiences (engineers, reviewers, stakeholders).

**Outcome 3 (algorithmic principles and trade-offs) — Partial.** Milestone
Two intentionally defers the algorithm-heavy work to Milestone Three
(trend smoothing, milestone detection, composite index strategy). The
cursor-based pagination decision (ADR-0015) is the one M2 contribution to
this outcome — the trade-offs between offset and cursor pagination, and
between transparent and opaque cursors, are documented with the chosen
alternative justified.

**Outcome 1 (collaborative environments) — Partial.** The ADRs, the code
review checklist self-application, and the README written for an external
audience all contribute. The capstone is a solo project, so the full
collaborative outcome will surface in the workplace; the artifact
demonstrates that I produce work in a form that *would* support collaboration
(decision records, documentation, clean PR history, conventional commits).

I have no updates to the Module One outcome-coverage plan: the milestone
schedule (M2 = software engineering, M3 = algorithms, M4 = databases) maps
cleanly to the program outcomes, and the deferred items in M2 are exactly
the items planned to land in M3.

---

## 4. Reflect on the process of enhancing and modifying the artifact

> The remainder of this section is personal reflection. The bullets below
> are prompts to expand against your own experience — replace each
> placeholder with your own answer in 2–4 sentences before submitting.

**What I learned during the rebuild.**

- [PLACEHOLDER — describe a specific technical lesson you learned that
  surprised you. Examples to consider: the discipline cost of strict TDD
  on a greenfield codebase; what working under `mypy --strict` taught you
  about Python that ordinary Python doesn't; what the three-pattern
  architecture forced you to make explicit that would have stayed implicit
  in a typical monolith.]

- [PLACEHOLDER — describe a non-technical lesson you learned. Examples to
  consider: writing ADRs *before* the code that depends on them; the value
  of a SUMMARY.md narrative log vs. relying on commit messages alone; how
  Phase 0 hygiene paid off during Phase 8 closeout.]

**Challenges I faced.**

- [PLACEHOLDER — describe a concrete challenge that took more than one
  attempt to resolve. Candidates from the SUMMARY.md log include: the
  cursor pagination boundary-skip bug surfaced during PR #30 review and
  the resulting ADR-0015; the soft-delete filter bug caught during PR #30
  multi-agent code review; the auth-race E2E flake that required rewiring
  the post-login navigation; the initial Pydantic/Zod schema drift that
  motivated generating TS types from the OpenAPI snapshot.]

- [PLACEHOLDER — describe how you adapted when something didn't work as
  planned. Examples: switching from per-entry unit selection to a global
  preference; choosing TanStack Query over a hand-rolled fetch hook after
  the auth hydration grew complex; deciding to ship the ARCHITECTURE.md
  as a stub deferring to the SRS rather than duplicating SRS §4.]

**How this work prepares me for the rest of the capstone.**

- [PLACEHOLDER — connect M2 to M3 and M4. What does the M2 vertical slice
  set up for the algorithms (M3) and database (M4) enhancements? Examples:
  the cursor pagination contract is reusable for time-series; the
  three-pattern architecture gives M3 a clean place to put algorithm
  modules without infrastructure leaking; the audit-log ADR planned for M4
  has a clear hook point in the existing logging strategy.]

---

## Appendix A: Verifiable references

- Repository: <https://github.com/rgoshen-snhu/WeighToGo>
- Milestone Two tag: `v0.1.0`
- Prior baseline tag: `v1.0.0-android`
- Software Requirements Specification: [`/docs/specs/WeighToGo_Web_SRS_v1.md`](../specs/WeighToGo_Web_SRS_v1.md)
- Architecture summary: [`/ARCHITECTURE.md`](../../ARCHITECTURE.md)
- ADR index: [`/docs/adr/README.md`](../adr/README.md)
- DDR index: [`/docs/ddr/README.md`](../ddr/README.md)
- Engineering log: [`/SUMMARY.md`](../../SUMMARY.md)
- Milestone Two implementation brief: [`/docs/plans/milestone-two-plan.md`](../plans/milestone-two-plan.md)
- CS 499 code review checklist (and self-review entry in `SUMMARY.md`): [`/docs/standards/cs499_code_review_checklist.md`](../standards/cs499_code_review_checklist.md)
