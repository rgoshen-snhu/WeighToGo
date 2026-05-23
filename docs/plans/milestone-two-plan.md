# Milestone Two Implementation Brief

| Field | Value |
| --- | --- |
| Course | CS 499, Computer Science Capstone (SNHU) |
| Milestone | Two |
| Enhancement Category | One: Software Design and Engineering |
| Status | Active |
| Authoritative Spec | `/docs/specs/WeighToGo_Web_SRS_v1.md` |
| Last Updated | 2026-05-22 |

---

## 1. Purpose and Scope

This brief is the entry point for Milestone Two work on the Weigh to Go! capstone artifact. The milestone covers Enhancement One: Software Design and Engineering. The work rebuilds the existing Android application as a full-stack web application with React/TypeScript on the frontend and FastAPI/Python on the backend, establishes the polyglot monorepo structure, scaffolds the three-pattern backend architecture, and implements the authentication system as the proof of architecture.

Deliverables at the end of M2:

- Technical artifact (zip of all code, original Android plus enhanced web)
- Narrative document (Word format) addressing the four reflection prompts in the CS 499 Milestone Two rubric

The narrative is drafted in parallel with the code work and finalized once implementation is complete.

---

## 2. Authoritative References

Read these before generating the detailed plan. The SRS is the source of truth when references conflict.

| Document | Location | Key Sections for M2 |
| --- | --- | --- |
| **Software Requirements Specification** | `/docs/specs/WeighToGo_Web_SRS_v1.md` | §4 Architecture, §5 Restructure Plan, §6 Functional Requirements (M2-tagged), §7 Non-Functional Requirements, §10 Frontend Specification, §11 Quality Engineering, §14 Acceptance Criteria, Appendix A (ADR Index) |
| **CS 499 Code Review Checklist** | `/docs/standards/cs499_code_review_checklist.md` | Program-standard review framework. Applied as self-review gate during Step 7 before tagging `v0.1.0`. |
| **Existing ADRs** | `/docs/adr/0001-*.md` through `/docs/adr/0006-*.md` | Context on Android-era decisions. New ADRs build on or supersede these where the rebuild changes the answer. |
| **Android Database Architecture** | `/docs/architecture/WeighToGo_Database_Architecture.md` | Original schema. Informs the web rebuild's data model. Superseded by SRS §8 for the web side. |

---

## 3. Implementation Sequence

Seven high-level steps. Each is expanded into detailed sub-tasks with affected files, approach, risks, and testing strategy. Each step ends with a green CI run and all coverage thresholds met before moving to the next.

### Step 1: Repository Restructure

Move from Android-only layout to polyglot monorepo per SRS §5. Preserve the Android build (all existing Android tests must still pass after the restructure). The Android codebase moves into `/android/` and all path references update accordingly. Web subtree is created at `/web/` ready for Step 2.

### Step 2: Web Scaffold

Create `/web/frontend/` and `/web/backend/` skeletons. Set up Vite + React + TypeScript on the frontend with Material UI theme configured. Set up FastAPI + Python on the backend with pyproject.toml, ruff, mypy, and pytest configured. Stand up Docker Compose for local PostgreSQL. Establish pre-commit hooks. Verify dev servers run cleanly on both sides.

### Step 3: Three-Pattern Backend Architecture

Implement the Screaming + Clean + Hexagonal pattern stack documented in SRS §4. Create the domain folder structure for the four domains (weight_tracking, goals, users, auth). Define the ports and adapters layout. Install and configure import linters that enforce the dependency rule. Validate the structure with a smoke test that confirms domain code has zero framework imports.

**Write before this step begins:** ADR-0012 (three-pattern backend architecture).

### Step 4: Frontend Architecture

Mirror the domain organization on the frontend per SRS §10. Set up React Router 6 with route declarations for the planned views. Establish providers (TanStack Query, MUI theme, auth context). Configure the Material UI theme to match the design system color and typography from the Android original.

### Step 5: Authentication System

Implement the full auth flow per SRS §6 and §7 (NFR-SEC requirements). Email as the primary user identifier, not username. Bcrypt password hashing with cost factor 12 or higher. JWT access tokens in HTTP-only cookies. Refresh tokens with rotation and family-based revocation. Generic authentication error messages to prevent username enumeration. Account lockout after configured failure threshold. PII masking in all logs. Rate limiting on auth endpoints. Explicit test cases for the security scenarios per SRS §11.

**Write before this step begins:** ADR-0009 (email as primary identifier), ADR-0010 (generic auth error policy), ADR-0011 (PII masking strategy), ADR-0013 (refresh token rotation and family revocation).

### Step 6: Vertical Slice (Registration + Login)

Wire the authentication system end-to-end from frontend form through backend domain service through PostgreSQL persistence. Cover the happy path and the documented error paths. This step is the architecture proof. If something is wrong with the three-pattern structure or the ports/adapters separation, this is where it surfaces.

### Step 7: Documentation and Closeout

Verify all ADRs (ADR-0007 through ADR-0013) are committed — they should already exist from the steps above. Update the README at the repo root with project overview, quickstart instructions for both stacks, and a pointer to the SRS. Generate and commit the OpenAPI snapshot to `/docs/api/openapi.json`. Self-review the M2 code against the CS 499 Code Review Checklist at `/docs/standards/cs499_code_review_checklist.md`. Draft the M2 narrative document addressing the four rubric prompts. Tag the repository `v0.1.0`.

**Note on ADR timing:** ADRs must be written at the time of the decision — on the feature branch, before the first line of implementation code that depends on the decision. Step 7 is a verification step, not the authorship step. An ADR committed after the code it documents is a retrospective record, not a decision document.

---

## 4. New ADRs Required

Seven new ADRs for M2. The numbering inserts the rebuild rationale at the front and shifts the originally planned IDs up by one. Each ADR documents an engineering decision with viable alternatives considered. None reference course requirements as rationale.

ADRs must be written **before** the first line of implementation code that depends on the decision — on the same feature branch, committed before any implementation commits. The "When to write" column is the gate.

| ID | Title | Decision Captured | When to Write |
| --- | --- | --- | --- |
| ADR-0007 | Rebuild Weigh to Go! as Full-Stack Web Application | Why a web rebuild rather than continuing the Android app: separation of concerns at scale, modern stack ecosystem, API-first design enables a future mobile client, addresses every finding from the Android code review, broader portfolio reach to web-focused employers. | Before Step 1 (repo restructure) |
| ADR-0008 | Polyglot Monorepo for Mobile-Web Artifact | Why a single repo holding both stacks vs. two separate repos: preserves the original artifact for portfolio reference, shared docs and ADRs, single source of truth for project history. | Before Step 1 (repo restructure) |
| ADR-0009 | Email as Primary User Identifier | Why email replaces username from the Android version: industry default, supports password recovery flow, avoids the username enumeration class of issues. | Before Step 5 (auth system) — before writing the User entity |
| ADR-0010 | Generic Authentication Error Policy | Why every auth failure returns the same generic message: closes the username enumeration finding from the code review, aligns with OWASP authentication guidance. | Before Step 5 (auth system) — before writing auth error handling |
| ADR-0011 | PII Masking Strategy in Logs | Why and how all logs mask PII: closes the unmasked phone number and username findings from the code review, supports future compliance work. | Before Step 3 (backend scaffold) — before writing the logging module |
| ADR-0012 | Three-Pattern Backend Architecture (Screaming + Clean + Hexagonal) | Why this combination of patterns: domain visibility from folder structure, framework independence at the core, swappable adapters for testability and future change. | Before Step 3 (backend scaffold) — before creating the domain folder structure |
| ADR-0013 | Refresh Token Rotation with Family-Based Revocation | Why rotation plus family tracking: detects token replay, limits blast radius if a refresh token leaks, aligns with industry best practice for long-lived sessions. | Before Step 5 (auth system) — before writing RefreshSession use case |

SRS Appendix A is updated to reflect this numbering.

---

## 5. M2-Specific Constraints

Project-wide constraints — TDD discipline, security baseline, strict typing, import linters, branching strategy, lint/test gates, and commit conventions — are specified in the SRS (§7 Non-Functional Requirements and §12 DevOps and Tooling) and the repository's contribution guidelines. Refer to them for execution rules.

M2-specific additions:

- The vertical slice in Step 6 must demonstrate the full three-pattern architecture working end-to-end before M2 is considered complete.
- All seven new ADRs must be written before the `v0.1.0` tag is applied, not after.

---

## 6. Definition of Done

Per SRS §14.2:

- [x] All M2-tagged functional requirements (SRS §6) are implemented with passing tests — Phase 8 (PR #30) closes FR-W-1..5 and FR-D-1
- [ ] Coverage thresholds met per SRS §11 — 255 backend tests, 213 frontend tests at ≥90% coverage
- [ ] CI is green on the `main` branch
- [x] ADR-0007 through ADR-0013 are written and committed
- [ ] Code self-reviewed against `/docs/standards/cs499_code_review_checklist.md`
- [x] OpenAPI snapshot generated to `/docs/api/openapi.json` — refreshed with weight-entries and dashboard routes
- [x] README at the repo root is updated with quickstart instructions for both stacks
- [ ] All existing Android tests still pass after the restructure
- [ ] The M2 narrative document is drafted and reviewed against the rubric
- [ ] The repository is tagged `v0.1.0`

**Phase 8 closes the FR-coverage portion of the M2 DoD.** The weight tracking bounded context (FR-W-1..5) and dashboard summary (FR-D-1) are fully implemented with TDD, 5 Playwright E2E specs, accessibility scans (axe WCAG 2.1 AA), and RFC 7807 error responses on all paths.

---

## 7. Out of Scope

The following items are explicitly NOT in M2. They are deferred to later milestones or out of capstone entirely.

| Item | Deferred To |
| --- | --- |
| Cursor-based pagination for time-series data | M3 (Algorithms and Data Structures) |
| TTL-based server-side caching | M3 |
| Sliding-window moving average for trend smoothing | M3 |
| Milestone detection algorithm | M3 |
| Composite index strategy for trend queries | M3 |
| Audit log schema and write strategy | M4 (Databases) |
| CHECK constraint inventory and database-level validation policy | M4 |
| Cloud deployment (AWS, GCP, Azure) | Out of capstone |
| Infrastructure-as-code tooling (OpenTofu, Terraform, Pulumi) | Out of capstone |
| Native mobile rebuild | Out of capstone |
| SMS notifications (carry-over from Android) | Out of capstone, no business need in web context |
| Real-time features (websockets, server-sent events) | Out of capstone |

---

**End of Brief**
