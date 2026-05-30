> **Document Version:** v2 — post-Milestone 2 baseline.
> Supersedes [WeighToGo_Web_SRS_v1.md](WeighToGo_Web_SRS_v1.md) (the pre-M2 spec).
>
> **Changes from v1:**
> - **Appendix A §17.2** reflects actual on-disk ADRs (ADR-0014 *TanStack Query for Server State* and ADR-0015 *Opaque Compound Cursor for Weight-Entry Pagination* are recognized as M2 work); planned M3/M4 ADRs renumbered to ADR-0016 through ADR-0020.
> - **FR-W-2 §6.2** cross-reference points at the actual cursor ADR (ADR-0015) instead of the prior "planned ADR-0014 (finalized in M3)" text.
>
> The document body is otherwise identical to v1.

# Weigh to Go! Web Application

## Software Requirements Specification

| Field | Value |
| --- | --- |
| Document Title | Weigh to Go! Web Application, Software Requirements Specification |
| Document Version | 1.0 |
| Status | Draft |
| Last Updated | 2026-05-22 |
| Author | Rick Goshen |
| Course | CS 499, Computer Science Capstone |
| Institution | Southern New Hampshire University |
| Artifact Repository | github.com/rgoshen-snhu/WeighToGo (pending restructure) |
| Predecessor Artifact | Weigh to Go! (Android, CS 360, November 2025) |

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Stakeholders and Personas](#2-stakeholders-and-personas)
3. [System Vision and Goals](#3-system-vision-and-goals)
4. [Architecture](#4-architecture)
5. [Repository Structure and Restructure Plan](#5-repository-structure-and-restructure-plan)
6. [Functional Requirements](#6-functional-requirements)
7. [Non-Functional Requirements](#7-non-functional-requirements)
8. [Data Architecture](#8-data-architecture)
9. [API Specification](#9-api-specification)
10. [Frontend Specification](#10-frontend-specification)
11. [Quality Engineering](#11-quality-engineering)
12. [DevOps and Tooling](#12-devops-and-tooling)
13. [Milestone Roadmap](#13-milestone-roadmap)
14. [Acceptance Criteria and Definition of Done](#14-acceptance-criteria-and-definition-of-done)
15. [Risks and Mitigations](#15-risks-and-mitigations)
16. [Glossary](#16-glossary)
17. [Appendix A: ADR Index](#17-appendix-a-adr-index)
18. [Appendix B: Course Outcome Alignment](#18-appendix-b-course-outcome-alignment)
19. [Appendix C: Source Document References](#19-appendix-c-source-document-references)

---

## 1. Introduction

### 1.1 Purpose

This document specifies the requirements for the Weigh to Go! web application. The web application is a full-stack rebuild of the existing Weigh to Go! Android artifact, originally built in CS 360 (November 2025). The rebuild serves as the capstone artifact for CS 499 and demonstrates competency across software design, algorithms, and database engineering.

This specification is the authoritative source for what the system does, what it does not do, and the standards it meets. It is structured so that any engineer can read it and produce work that satisfies the requirements without further clarification.

### 1.2 Background

The original Weigh to Go! Android app handles user authentication, daily weight logging, goal tracking, achievement milestones, and SMS notifications. The application is functional and ships with 373 passing tests, six Architecture Decision Records, and a comprehensive database architecture specification. A CS 499 code review identified specific technical debt that the rebuild addresses, including activity bloat with single-responsibility violations, MVC drift where activities also serve as the model layer, database writes blocking the UI thread, an ExecutorService lifecycle bug, personally identifiable information appearing unmasked in logs, username enumeration via exception messages, a hardcoded if-elseif navigation chain that violates open-closed, and accessibility gaps in the XML layouts.

### 1.3 Scope

The web application replaces the Android application's user interface and business logic with a browser-based experience while preserving the domain model. The system covers the same problem space as the Android predecessor and adds capabilities the mobile codebase cannot provide cleanly. The rebuild also restructures the existing repository to host both the Android codebase and the new web codebase as a polyglot monorepo.

**In Scope:**

- Full-stack web application with React/TypeScript frontend and FastAPI/Python backend
- PostgreSQL persistence layer with strict typing and database-level constraints
- Repository restructure to support both the Android artifact and the web artifact
- Architecture Decision Records documenting every nontrivial decision
- Industry-standard security posture from initial commit
- Automated testing across unit, integration, and end-to-end layers
- Continuous integration with quality gates
- Accessibility conformance to WCAG 2.1 Level AA
- Auto-generated API documentation via OpenAPI

**Out of Scope:**

- Cloud deployment (AWS, GCP, Azure)
- Infrastructure-as-code tooling (OpenTofu, Terraform, Pulumi)
- A native mobile rebuild of the artifact (the API is designed to support a future mobile client but no mobile work is part of this capstone)
- Multi-tenant architecture
- Real-time features (websockets, server-sent events)
- Internationalization beyond US English
- Third-party fitness tracker integration
- Payment processing or subscription management

### 1.4 Definitions and Acronyms

| Term | Definition |
| --- | --- |
| ADR | Architecture Decision Record. A short markdown document capturing a single architectural decision, its context, and its trade-offs. |
| Artifact | The capstone deliverable, here meaning the Weigh to Go! application across both Android and web platforms. |
| Clean Architecture | Architectural style that enforces a dependency rule where outer layers depend on inner layers and never the reverse. |
| Hexagonal Architecture | Architectural style where the domain core is surrounded by ports (interfaces) and adapters (implementations), enabling framework substitution. |
| JWT | JSON Web Token. A signed, self-contained token used for stateless authentication. |
| Monorepo | A single source repository containing multiple related projects or packages. |
| ORM | Object-Relational Mapper. Software that maps relational database records to programming language objects. |
| Polyglot | Using multiple programming languages or platforms. Here referring to a repo containing both Android (Java) and web (TypeScript, Python) codebases. |
| Screaming Architecture | Folder and module organization where the top-level structure reveals the application's domain rather than its technical framework. |
| SRP | Single Responsibility Principle. The design principle that a class or module should have exactly one reason to change. |
| SRS | Software Requirements Specification. This document. |
| TDD | Test-Driven Development. A development practice where tests are written before the implementation they verify. |
| WCAG | Web Content Accessibility Guidelines. The W3C standard for accessible web content, with conformance levels A, AA, and AAA. |

### 1.5 Document Conventions

- Requirement identifiers follow the pattern `FR-XX-N` (functional) and `NFR-XX-N` (non-functional), where `XX` is a two-letter area code and `N` is a sequential number within that area
- Requirement priority is indicated as `[MUST]`, `[SHOULD]`, or `[MAY]` following RFC 2119 conventions
- Milestone tags `[M2]`, `[M3]`, `[M4]`, or `[Final]` indicate when a requirement is delivered
- Code blocks, file paths, and command-line invocations appear in `monospaced` formatting
- ADR references appear as `[ADR-NNNN]` where `NNNN` is the four-digit ADR number

---

## 2. Stakeholders and Personas

### 2.1 Stakeholders

| Stakeholder | Role | Primary Concerns |
| --- | --- | --- |
| Capstone Instructor | Evaluator | Rubric alignment, demonstration of competency, ePortfolio readiness |
| Capstone Author (Rick Goshen) | Developer, Designer, Reviewer | Engineering quality, security posture, narrative coherence, career portfolio value |
| Future Employer (Reviewer of ePortfolio) | External Reviewer | Code quality, architectural reasoning, modern tooling familiarity |
| Future Engineer (Continuation Reader) | Maintainer | Decision rationale via ADRs, readable code, clear setup and contribution guides |
| End User (Hypothetical) | Application User | Reliable weight tracking, secure account, accessible interface |

### 2.2 User Personas

**Primary Persona: Weight Tracking User**

A health-conscious adult who wants to log daily weight, track progress against a goal, and see trends over time. The user values speed of entry, accurate progress visualization, and predictable behavior. The user expects modern web application standards including responsive design, keyboard accessibility, and reasonable performance.

**Secondary Persona: Accessibility-Dependent User**

A user who relies on assistive technology including screen readers, keyboard-only navigation, or system-level zoom. This persona surfaces requirements that the Android predecessor failed to meet, including content descriptions on every interactive element, adequate touch and click targets, and semantic HTML structure.

**Tertiary Persona: Security-Conscious User**

A user whose health data is sensitive and who trusts the application to handle credentials, personal information, and behavioral data responsibly. The persona drives requirements around encryption in transit, password storage, audit logging, and explicit consent for data collection.

---

## 3. System Vision and Goals

### 3.1 Vision Statement

Weigh to Go! is a web application that helps individuals track daily weight and progress toward personal health goals through a fast, accessible, and secure interface. The application demonstrates production-grade engineering practices on a domain simple enough to serve as a teaching artifact while sufficient to demonstrate full-stack competency.

### 3.2 Goals

The rebuild has four overarching goals that drive all subsequent requirements:

1. **Architectural quality**. The system implements a deliberate architectural blend of Screaming Architecture, Clean Architecture, and Hexagonal Architecture. Each pattern is documented in an ADR with the alternatives considered and the reason for the choice.

2. **Security from initial commit**. The system applies defense-in-depth at every layer. Database constraints, ORM-parameterized queries, Pydantic validation at the API boundary, bcrypt password hashing, secure session management, generic error messages, and PII-aware logging are all present in the first feature delivered, not retrofitted later.

3. **Test-driven development**. Every feature is developed test-first. The system maintains separate unit, integration, and end-to-end test layers with explicit coverage thresholds. Tests are executed in continuous integration on every push.

4. **Documentation as a first-class deliverable**. The system carries this requirements document, an ADR log, an auto-generated OpenAPI specification, inline code documentation, and a top-level README that tells the artifact's narrative across both the Android predecessor and the web rebuild.

### 3.3 Non-Goals

- The application does not attempt to compete with commercial weight-tracking products. Feature scope stays deliberate.
- The application does not target zero-downtime deployment, multi-region availability, or horizontal scaling. Operational scope stays academic.
- The application does not target sub-100ms latency or other performance characteristics that would dictate architectural choices beyond what the curriculum benefits from.

---

## 4. Architecture

### 4.1 High-Level Architecture

The system is a three-tier web application with a single-page application frontend, a stateless REST API backend, and a relational database. The frontend and backend communicate over HTTP using JSON request and response bodies. Authentication is implemented with JWT access tokens delivered in HTTP-only cookies, with refresh tokens stored server-side for revocation control.

```
+----------------------------+         +----------------------------+         +----------------------+
|    Browser (Frontend)      |  HTTPS  |    FastAPI Application     |   TCP   |  PostgreSQL 16+      |
|                            | <-----> |                            | <-----> |                      |
|  React 19 + TypeScript     |  JSON   |  Python 3.12 + FastAPI     |   SSL   |  Strict schema       |
|  Material UI v9            |         |  Pydantic v2 + SQLAlchemy  |         |  CHECK constraints   |
|  React Router v7           |         |  Alembic for migrations    |         |  Foreign keys        |
|  Vite build tooling        |         |  bcrypt + JWT auth         |         |                      |
+----------------------------+         +----------------------------+         +----------------------+
```

### 4.2 Architectural Patterns

The backend uses a deliberate blend of three patterns. Each pattern addresses a different design concern, and the combination produces a codebase that is easy to navigate, easy to test, and easy to evolve.

#### 4.2.1 Screaming Architecture (Folder Structure)

Top-level packages inside the backend reflect the application's domains, not technical roles. A new engineer reading the file tree sees what the application does before seeing what frameworks it uses.

```
backend/src/weighttogo/
├── auth/              # User identity, sessions, credentials
├── weight_tracking/   # Weight entries, history, validation
├── goals/             # Goal definition, progress, achievement detection
├── notifications/     # In-app and SMS notification dispatch
├── preferences/       # User-scoped preferences and settings
└── shared/            # Cross-domain utilities (logging, security primitives)
```

#### 4.2.2 Clean Architecture (Dependency Rule)

Inside each domain folder, dependencies point inward. The domain core (entities, value objects, domain services) has no knowledge of FastAPI, SQLAlchemy, or any other framework. Adapters (database repositories, HTTP routers) depend on the domain, never the reverse.

```
auth/
├── domain/            # Entities, value objects, domain exceptions
├── application/       # Use cases (CreateUser, AuthenticateUser, RevokeSession)
├── infrastructure/    # SQLAlchemy repositories, bcrypt adapter, JWT issuer
└── interface/         # FastAPI routers, Pydantic schemas, dependency injection
```

A use case in `application/` accepts a repository interface from `domain/`. The infrastructure layer provides a concrete SQLAlchemy implementation of that interface. The interface layer wires them together. Swapping SQLAlchemy for another ORM or PostgreSQL for another database requires changes only in `infrastructure/`.

#### 4.2.3 Hexagonal Architecture (Ports and Adapters)

Framework integrations live at the edges. The FastAPI router is an adapter for the HTTP port. The SQLAlchemy repository is an adapter for the persistence port. The bcrypt utility is an adapter for the password-hashing port. The domain knows about ports (interfaces) and never about adapters (implementations).

This blend is documented in `[ADR-0012]` (planned). The decision builds on the existing six ADRs in the Android repository.

### 4.3 Technology Stack

#### 4.3.1 Frontend

| Concern | Technology | Version | Notes |
| --- | --- | --- | --- |
| Language | TypeScript | 6.0 | Strict mode enabled |
| UI Framework | React | 19 | Functional components, hooks |
| Component Library | Material UI (MUI) | 9 | Accessibility-conformant components |
| Routing | React Router | 7 | Declarative routes, code splitting |
| Forms | React Hook Form | 7.76 | Performant, uncontrolled-by-default |
| Form Validation | Zod | 4.4 | Runtime type validation, shares schemas with TypeScript types |
| HTTP Client | Fetch API + custom wrapper | Native | Wrapper enforces auth, error mapping, base URL |
| State Management | TanStack Query + React Context | 5.100 | Server state via TanStack Query; no Redux |
| Build Tool | Vite | 8 | Fast dev server, optimized production bundle |
| Unit Testing | Vitest | 4.1 | Vite-native test runner |
| Component Testing | React Testing Library | 16 | Behavior-focused tests |
| E2E Testing | Playwright | 1.60 | Cross-browser end-to-end coverage |
| Linting | ESLint | 9 | TypeScript + React rules |
| Formatting | Prettier | 3.8 | Single source of truth for style |

#### 4.3.2 Backend

| Concern | Technology | Version | Notes |
| --- | --- | --- | --- |
| Language | Python | 3.12+ | Strict typing via mypy |
| Web Framework | FastAPI | 0.110+ | Async, OpenAPI-native |
| Validation | Pydantic | 2+ | Schemas for requests, responses, settings |
| ORM | SQLAlchemy | 2.0+ | Async engine, typed sessions |
| Migrations | Alembic | 1.13+ | Version-controlled schema changes |
| Password Hashing | bcrypt | 4+ | Cost factor 12, matches Android baseline |
| Authentication | python-jose or PyJWT | Latest stable | JWT issuance and verification |
| Rate Limiting | slowapi | 0.1.9+ | Per-endpoint and per-IP limits |
| Database Driver | psycopg | 3+ | Async-capable PostgreSQL driver |
| Logging | structlog | 24+ | Structured JSON output |
| Test Framework | pytest | 8+ | With pytest-asyncio for async tests |
| Test Coverage | coverage.py via pytest-cov | 7+ | HTML and XML reports |
| Linting | ruff | 0.4+ | Replaces flake8, isort, and most others |
| Type Checking | mypy | 1.10+ | Strict mode |
| Formatting | ruff format | 0.4+ | Replaces black |
| Dependency Management | Poetry or uv | Latest stable | Reproducible lockfile |

#### 4.3.3 Database

| Concern | Technology | Version | Notes |
| --- | --- | --- | --- |
| Database | PostgreSQL | 16+ | Strict typing, CHECK constraints, partial indexes |
| Local Hosting | Docker Compose | 2+ | Reproducible dev environment |
| Connection | SSL required | Always | Even in development |

#### 4.3.4 Cross-Cutting

| Concern | Technology | Version | Notes |
| --- | --- | --- | --- |
| Version Control | Git | 2.40+ | Conventional Commits |
| CI/CD | GitHub Actions | N/A | Existing Android workflow preserved |
| Containerization (dev) | Docker + Compose | 24+ | Database only, not the application |
| Pre-commit Hooks | pre-commit (Python), husky + lint-staged (Node) | Latest stable | Enforce style and basic checks before push |
| Documentation | Markdown, MkDocs (optional) | N/A | Living docs in `/docs/` |

### 4.4 Component Architecture

#### 4.4.1 Backend Component Diagram

```
                                       +-------------------+
   HTTP Request                        |   FastAPI App     |
   ----------->                        |  (Interface)      |
                                       +---------+---------+
                                                 |
                                                 v
                                       +---------+---------+
                                       |   Use Case        |
                                       |  (Application)    |
                                       +---------+---------+
                                                 |
                          +----------------------+----------------------+
                          |                                             |
                          v                                             v
                +---------+---------+                       +-----------+-----------+
                |  Domain Entity    |                       |  Repository Port      |
                |  (Domain)         |                       |  (Domain Interface)   |
                +-------------------+                       +-----------+-----------+
                                                                        |
                                                                        v
                                                            +-----------+-----------+
                                                            | SQLAlchemy Adapter    |
                                                            | (Infrastructure)      |
                                                            +-----------+-----------+
                                                                        |
                                                                        v
                                                            +-----------+-----------+
                                                            |    PostgreSQL         |
                                                            +-----------------------+
```

#### 4.4.2 Frontend Component Diagram

```
+-----------------------------+
|        AppRouter            |   React Router v7 with code-split routes
+-------------+---------------+
              |
   +----------+----------+
   |                     |
   v                     v
+--+--------+    +-------+--------+
| Public    |    |  Protected     |
| Routes    |    |  Routes        |
| (Login,   |    |  (Dashboard,   |
| Register) |    |  WeightEntry,  |
|           |    |  Goals*,       |
|           |    |  Settings*)    |
+--+--------+    +-------+--------+
   |                     |
   v                     v
+--+--------+    +-------+--------+
| AuthLayout|    |  AppLayout     |
+-----------+    | (Header, Nav,  |
                 |  Outlet,       |
                 |  Footer)       |
                 +-------+--------+
                         |
                         v
                 +-------+--------+
                 |  Feature       |
                 |  Pages         |
                 +----------------+

* Goals and Settings are auth-gated placeholder pages in Milestone 2.
```


---

## 5. Repository Structure and Restructure Plan

### 5.1 Current Repository State

The artifact currently lives at `github.com/rgoshen-snhu/WeighToGo`. The repository contains the Android application, six ADRs in `/docs/adr/`, a database architecture specification, design specifications, requirements documents, HTML mockups, and a GitHub Actions workflow for Android CI. The root directory contains Android-specific build files including `build.gradle`, `settings.gradle`, `gradle.properties`, and `gradlew`.

The Android codebase consists of 32 Java files across activities, adapters, database, models, utilities, and constants, plus XML layouts, resources, and 373 passing tests. The repository's identity is platform-bound, both in its name and its root-level tooling. Adding a Python backend and a TypeScript frontend at the same root would create root-level naming conflicts and obscure the artifact's evolution.

### 5.2 Target Repository Structure

The repository is restructured into a polyglot monorepo with each technology stack isolated under a top-level folder. Shared documentation lives at the repository root. The proposed target structure follows:

```
WeighToGo/                          # Repository root (renamed from cs360-WeightToGoMobile)
├── android/                        # Existing Android application (moved from root)
│   ├── app/
│   ├── gradle/
│   ├── build.gradle
│   ├── settings.gradle
│   ├── gradlew
│   └── ...
├── web/
│   ├── frontend/                   # React + TypeScript application
│   │   ├── src/
│   │   ├── public/
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   ├── vite.config.ts
│   │   └── ...
│   └── backend/                    # FastAPI + Python application
│       ├── src/weighttogo/
│       ├── tests/
│       ├── alembic/
│       ├── pyproject.toml
│       ├── docker-compose.yml      # PostgreSQL only
│       └── ...
├── docs/
│   ├── adr/                        # Existing six ADRs + new ADRs starting at 0007
│   ├── architecture/
│   ├── requirements/               # This document lives here
│   ├── design/
│   ├── api/                        # Auto-generated OpenAPI snapshots
│   └── user-guide/
├── .github/
│   └── workflows/
│       ├── android-ci.yml          # Existing Android workflow, preserved
│       ├── backend-ci.yml          # New Python workflow
│       └── frontend-ci.yml         # New Node/TypeScript workflow
├── README.md                       # Rewritten to tell the full mobile-to-web story
├── CONTRIBUTING.md                 # Updated with web contribution guidelines
├── LICENSE.md                      # Unchanged
└── .gitignore                      # Expanded to cover Python and Node artifacts
```

### 5.3 Restructure Procedure

The restructure is performed in a single feature branch and merged via pull request with all CI checks passing. The procedure preserves git history for every Android source file.

| Step | Action | Verification |
| --- | --- | --- |
| 1 | Create a feature branch from `main` | `git branch` shows the new branch |
| 2 | Use `git mv` to move every Android file under `/android/` | `git log --follow android/app/...` shows full history |
| 3 | Update the Android CI workflow to reference `/android/` as the working directory | Workflow runs successfully on the branch |
| 4 | Create empty `/web/frontend/` and `/web/backend/` folders with `.gitkeep` | Folders exist in `git status` |
| 5 | Move existing requirements docs into `/docs/requirements/` | Documents appear at new path |
| 6 | Update README to describe the polyglot structure and link to mobile-to-web narrative | README renders correctly on GitHub |
| 7 | Write ADR-0007 and ADR-0008 documenting the restructure decision | ADRs exist at `/docs/adr/0007-rebuild-as-full-stack-web-application.md` and `/docs/adr/0008-polyglot-monorepo.md` |
| 8 | Update `.gitignore` to cover Python (`__pycache__`, `.venv`, etc.) and Node (`node_modules`, `dist`, etc.) | `git status` is clean after dependency install |
| 9 | Run the existing Android test suite | All 373 Android tests pass against the new path |
| 10 | Open pull request, run all CI workflows | All checks green |
| 11 | Squash or rebase-merge to `main` | History preserved per chosen strategy |
| 12 | Rename the repository on GitHub | New URL active, redirects from old URL work |

### 5.4 Naming Considerations

The repository name `cs360-WeightToGoMobile` is bound to the original course and platform. Two naming options are viable:

| Option | Rationale | Recommendation |
| --- | --- | --- |
| `WeighToGo` | Permanent name, decoupled from any course, matches the product name | **Preferred for portfolio durability** |
| `cs499-WeighToGo` | Matches the existing `cs360-` prefix convention used on the SNHU GitHub org | Acceptable if course traceability is preferred |

This decision is documented in `[ADR-0008]` alongside the polyglot monorepo decision.

### 5.5 Git History Preservation

All file moves use `git mv` (or equivalent index operations) so that `git log --follow` traces every Android source file's complete history through the move. The merge to `main` preserves the linear history of the original 373 commits where present. No `git filter-branch` or history rewriting is performed.

### 5.6 Branch and Tag Strategy

The Android artifact's final commit before the restructure is tagged `v1.0.0-android` to mark the mobile-only era. The restructure itself is a structural change and is not separately tagged. The web application is in initial, pre-1.0 development and uses `0.x` development versioning; each milestone ships under its own tag, and the `1.0.0` release marks the final capstone submission. Exact tag values are confirmed when each tag is applied.

| Tag | Meaning |
| --- | --- |
| `v1.0.0-android` | Final state of Android-only repository, before restructure |
| `v0.1.0` | Milestone 2 deliverable (auth + weight entry vertical slice) |
| `v0.2.0` | Milestone 3 deliverable (algorithms enhancement) |
| `v0.3.0` | Milestone 4 deliverable (database enhancement) |
| `v1.0.0` | Final capstone submission |

---

## 6. Functional Requirements

This section catalogs every functional requirement across the full final-project scope. Each requirement is tagged with a milestone marker so that Milestone 2 implementation work can be identified at a glance. Requirements tagged `[M2]` are in scope for the current milestone. Requirements tagged `[M3]`, `[M4]`, or `[Final]` are documented now but implemented later.

### 6.1 Authentication and Session Management (FR-A)

#### FR-A-1: User Registration `[MUST]` `[M2]`

The system shall allow new users to create an account by providing a valid email address, a display name, and a password. The system validates inputs at the API boundary using Pydantic schemas and rejects invalid submissions with field-level error messages.

**Acceptance Criteria:**

- Email must be RFC 5322 compliant and unique across the user table
- Display name must be 2 to 50 characters, trimmed of leading and trailing whitespace
- Password must be at least 12 characters with at least one uppercase letter, one lowercase letter, one digit, and one non-alphanumeric character
- Passwords are never stored in plain text; bcrypt cost factor 12 is used
- Successful registration returns 201 Created with a session cookie
- Duplicate email returns 409 Conflict with a generic error message that does not confirm whether the email is already registered (see FR-A-9)

`[ADR-0009]` Email as primary identifier (planned).

#### FR-A-2: User Login `[MUST]` `[M2]`

The system shall authenticate users by validating an email and password combination against stored credentials. Successful authentication issues a JWT access token in an HTTP-only cookie and a refresh token recorded server-side.

**Acceptance Criteria:**

- Login endpoint accepts email and password
- Failed authentication returns 401 Unauthorized with a generic error message
- Successful authentication returns 200 OK with session cookie set
- Access token expires in 15 minutes
- Refresh token expires in 7 days and is single-use (rotated on each refresh)
- Failed login attempts are recorded for rate limiting (see NFR-S-5)

#### FR-A-3: User Logout `[MUST]` `[M2]`

The system shall allow authenticated users to end their session by invalidating their refresh token and clearing session cookies.

**Acceptance Criteria:**

- Logout endpoint requires authentication
- Refresh token is marked invalid in the database
- Session cookies are cleared via `Set-Cookie` with past expiration
- Returns 204 No Content on success

#### FR-A-4: Token Refresh `[MUST]` `[M2]`

The system shall issue a new access token when presented with a valid, non-expired, non-revoked refresh token. Each refresh rotates the refresh token.

**Acceptance Criteria:**

- Refresh endpoint reads the refresh token from the HTTP-only cookie
- Valid refresh issues a new access token and a new refresh token
- The presented refresh token is immediately invalidated
- Invalid or expired refresh returns 401 Unauthorized
- Re-use of an already-rotated refresh token revokes the entire token family (security event logged)

#### FR-A-5: Authenticated Session State `[MUST]` `[M2]`

The system shall expose an endpoint that returns the current user's identity if a valid access token is present, or an unauthenticated response if not.

**Acceptance Criteria:**

- `GET /api/v1/auth/me` returns 200 with user identity for authenticated requests
- Returns 401 Unauthorized when no valid access token is present
- The frontend uses this endpoint on initial load to determine routing

#### FR-A-6: Password Change `[SHOULD]` `[Final]`

The system shall allow an authenticated user to change their password by providing the current password and a new password meeting all complexity requirements.

#### FR-A-7: Password Reset `[MAY]` `[Final]`

The system may support password reset via email-delivered token. Out of scope for Milestone 2 because the email delivery infrastructure is not part of the academic project.

#### FR-A-8: Account Deactivation `[SHOULD]` `[Final]`

The system shall allow an authenticated user to deactivate their account. Deactivation marks the account inactive without deleting data, in line with the soft-delete pattern from the Android predecessor.

#### FR-A-9: Generic Error Messages `[MUST]` `[M2]`

The system shall return generic error messages for authentication failures that do not reveal whether an email exists, whether a password was the cause of failure, or which specific validation rule failed for password complexity.

This requirement directly addresses the username enumeration finding in the Android code review where `UserDAO` line 59 exposed the attempted username in its exception message.

`[ADR-0010]` Generic authentication error policy (planned).

#### FR-A-10: PII-Aware Logging `[MUST]` `[M2]`

The system shall log authentication events without exposing personally identifiable information in plain text. Email addresses, when logged, are masked. User identifiers in logs use opaque internal IDs rather than email addresses or display names.

This requirement directly addresses the PII logging findings in the Android code review where `SessionManager` lines 139, 190, and 229 logged usernames in plain text, and `UserDAO` line 329 logged phone numbers.

`[ADR-0011]` PII masking strategy in logs (planned).

### 6.2 Weight Tracking (FR-W)

#### FR-W-1: Create Weight Entry `[MUST]` `[M2]`

The system shall allow an authenticated user to record a weight entry with a value, a unit, an observation date, and optional notes.

**Acceptance Criteria:**

- Weight value is a positive decimal between 1 and 1500 (covering both lbs and kg practical ranges)
- Weight unit is one of `lbs` or `kg`, enforced via CHECK constraint at the database level
- Observation date is not in the future
- Notes are optional, maximum 500 characters
- Duplicate (user_id, observation_date) raises a conflict (one entry per user per day)
- Successful creation returns 201 Created with the persisted entry
- Validation errors return 422 Unprocessable Entity with field-level error details

#### FR-W-2: List Weight Entries `[MUST]` `[M2]`

The system shall return a paginated list of the authenticated user's weight entries sorted by observation date descending.

**Acceptance Criteria:**

- Pagination parameters: `limit` (default 20, max 100), `cursor` (optional)
- Cursor-based pagination using observation date and entry ID as the cursor key
- Results are scoped to the authenticated user
- Soft-deleted entries are excluded
- Response includes `next_cursor` when more results exist

The cursor-based approach is documented in [ADR-0015 — Opaque Compound Cursor for Weight-Entry Pagination](../adr/0015-opaque-compound-cursor-pagination.md), authored during Milestone 2 PR #30 review.

#### FR-W-3: Update Weight Entry `[MUST]` `[M2]`

The system shall allow the authenticated user to update the value, unit, date, or notes of an existing entry they own.

**Acceptance Criteria:**

- Same validation as creation
- Attempts to update another user's entry return 404 Not Found
- Returns 200 OK with the updated entry
- `updated_at` timestamp is automatically maintained

#### FR-W-4: Delete Weight Entry `[MUST]` `[M2]`

The system shall allow the authenticated user to soft-delete an entry they own.

**Acceptance Criteria:**

- Soft delete sets `is_deleted = true` and records `deleted_at`
- Subsequent listings exclude soft-deleted entries
- Attempts to delete another user's entry return 404 Not Found
- Returns 204 No Content on success
- The matching idempotency rule ensures a re-delete returns 204 (not 404)

#### FR-W-5: Get Single Weight Entry `[SHOULD]` `[M2]`

The system shall return a single weight entry by ID for the authenticated user.

#### FR-W-6: Weight Unit Conversion `[SHOULD]` `[M3]`

The system shall convert weight values for display according to the user's preferred unit, while storing the original entered unit on the row.

### 6.3 Goal Management (FR-G)

#### FR-G-1: Set Active Goal `[MUST]` `[M3]`

The system shall allow an authenticated user to set an active goal weight with a target value, a goal type (`lose` or `gain`), a starting weight reference, and an optional target date. Only one goal may be active per user at a time. In Milestone 2, the Goals page is a placeholder requiring authentication and displays a "Coming in Milestone 3" message.

#### FR-G-2: Track Goal Progress `[MUST]` `[M3]`

The system shall calculate a user's progress toward their active goal as a percentage, based on the difference between the starting weight and the most recent weight entry, divided by the difference between the starting weight and the target weight.

#### FR-G-3: Update Goal `[MUST]` `[M3]`

The system shall allow an authenticated user to modify their active goal's target value or target date.

#### FR-G-4: Mark Goal Achieved `[MUST]` `[M3]`

The system shall automatically detect when a weight entry causes a goal to be reached and record the achievement.

#### FR-G-5: Goal History `[SHOULD]` `[M3]`

The system shall maintain a history of past goals (achieved or abandoned) for the user to view.

### 6.4 Achievements and Milestones (FR-Ach)

#### FR-Ach-1: Goal Achievement Recording `[MUST]` `[M3]`

The system shall record an achievement when a weight entry causes the active goal to be reached.

#### FR-Ach-2: Milestone Detection `[MUST]` `[M3]`

The system shall detect quantitative milestones at intervals of 5, 10, 25, and 50 pounds lost or gained from the goal's starting weight, and record each milestone exactly once per goal.

#### FR-Ach-3: Streak Detection `[SHOULD]` `[M3]`

The system shall detect logging streaks at 7 and 30 consecutive days and record them as achievements.

#### FR-Ach-4: Achievement Listing `[SHOULD]` `[M3]`

The system shall provide an endpoint and UI listing for past achievements, sorted by date descending.

### 6.5 Notifications (FR-N)

#### FR-N-1: In-App Achievement Notification `[MUST]` `[M3]`

The system shall display a celebratory in-app notification (modal or banner) when an achievement is recorded during a weight entry session.

#### FR-N-2: SMS Notification (Stretch) `[MAY]` `[Final]`

The system may send SMS notifications for achievements via a third-party provider (Twilio or equivalent), gated by user opt-in and a verified phone number. SMS support is a stretch goal due to provider account requirements that complicate academic project scope.

#### FR-N-3: Email Notification (Stretch) `[MAY]` `[Final]`

The system may send email notifications for achievements via a third-party provider. Same scope considerations as FR-N-2.

### 6.6 User Preferences (FR-P)

#### FR-P-1: Global Weight Unit Preference `[MUST]` `[M3]`

The system shall allow an authenticated user to choose a default weight unit (`lbs` or `kg`) that drives display formatting throughout the application. This requirement carries forward the design decision from `[ADR-0004]` of the Android codebase.

#### FR-P-2: Theme Preference `[MAY]` `[Final]`

The system may support a theme preference (`light`, `dark`, `system`) that drives the Material UI palette.

#### FR-P-3: Notification Preferences `[MUST]` `[M3]`

The system shall allow users to toggle individual notification types (achievement, milestone, streak) on and off.

### 6.7 Dashboard and Trends (FR-D)

#### FR-D-1: Dashboard Summary `[MUST]` `[M2]`

The system shall present an authenticated user with a dashboard showing the most recent weight entry, total entries, and a placeholder for goal progress. In Milestone 2, the goal progress section is a placeholder; the rest is populated from real data.

**Acceptance Criteria:**

- Renders the most recent weight value and observation date
- Renders total entry count
- Renders an empty state when no entries exist, with a prominent "Add your first entry" call to action
- Loads in under 1 second on a typical connection

#### FR-D-2: Weight Trend Chart `[SHOULD]` `[M3]`

The system shall display a line chart of weight over time, with selectable date ranges (7 days, 30 days, 90 days, all time).

#### FR-D-3: Rate of Change `[SHOULD]` `[M3]`

The system shall display the user's weekly rate of weight change calculated from a rolling average.

#### FR-D-4: Goal Progress Visualization `[MUST]` `[M3]`

The system shall display a progress bar showing percentage completion toward the active goal.


---

## 7. Non-Functional Requirements

### 7.1 Security (NFR-S)

#### NFR-S-1: Transport Encryption `[MUST]` `[M2]`

All HTTP traffic between the browser and the backend uses TLS in any environment where the application is reachable beyond `localhost`. The backend rejects plain HTTP requests with 426 Upgrade Required.

#### NFR-S-2: Password Hashing `[MUST]` `[M2]`

Passwords are stored using bcrypt with cost factor 12. Plain-text passwords are never logged, written to disk, or stored in any form. Password verification uses constant-time comparison provided by the bcrypt library.

#### NFR-S-3: Session Token Security `[MUST]` `[M2]`

Access tokens and refresh tokens are delivered as HTTP-only, Secure, SameSite=Strict cookies. Tokens are signed using HS256 with a key of at least 256 bits stored as an environment variable. Token payloads contain only the user identifier and standard JWT claims (iat, exp, jti); no PII appears in tokens.

#### NFR-S-4: Input Validation `[MUST]` `[M2]`

Every API endpoint validates inputs using Pydantic schemas before any business logic executes. Invalid inputs return 422 Unprocessable Entity with structured field-level error details. Database queries use SQLAlchemy parameterized bindings exclusively; no string interpolation of user input into SQL is permitted.

#### NFR-S-5: Rate Limiting `[MUST]` `[M2]`

The authentication endpoints (`/auth/register`, `/auth/login`, `/auth/refresh`) enforce per-IP rate limits using slowapi. Default limits are 5 requests per minute for login and refresh, and 3 requests per hour for registration. Rate-limited requests return 429 Too Many Requests with a `Retry-After` header.

#### NFR-S-6: Account Lockout `[MUST]` `[M2]`

After 5 consecutive failed login attempts for a given email, the account enters a lockout state for 15 minutes. Repeated lockout cycles apply exponential backoff capped at 24 hours. Lockout events are logged as security events.

#### NFR-S-7: Generic Error Messages `[MUST]` `[M2]`

Authentication and authorization failures return generic error messages that do not leak user existence, password complexity rule details, or account state. Cross-references FR-A-9.

#### NFR-S-8: CORS Policy `[MUST]` `[M2]`

The backend enforces a strict allowlist of origins. Wildcards are not used. Allowed origins are configured per environment via environment variables.

#### NFR-S-9: CSRF Mitigation `[MUST]` `[M2]`

CSRF protection is provided by SameSite=Strict cookies. The backend additionally verifies the `Origin` or `Referer` header on state-changing requests.

#### NFR-S-10: Security Headers `[MUST]` `[M2]`

The backend emits the following response headers:

| Header | Value |
| --- | --- |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` |
| `X-Content-Type-Options` | `nosniff` |
| `X-Frame-Options` | `DENY` |
| `Content-Security-Policy` | Strict policy disallowing inline scripts and external sources beyond the configured backend |
| `Referrer-Policy` | `strict-origin-when-cross-origin` |
| `Permissions-Policy` | Minimal feature set; geolocation, camera, microphone all disabled |

#### NFR-S-11: Dependency Auditing `[MUST]` `[M2]`

The CI pipeline runs dependency vulnerability scans on every push using `pip-audit` for Python and `npm audit` for Node. Builds fail on findings rated high or critical.

#### NFR-S-12: Secrets Management `[MUST]` `[M2]`

Secrets (JWT signing key, database password, third-party API keys) are never committed to source control. Local development uses `.env` files listed in `.gitignore`. A checked-in `.env.example` documents the required variables without secret values.

### 7.2 Performance (NFR-P)

#### NFR-P-1: API Latency `[SHOULD]` `[M2]`

The 95th percentile of API response time for read endpoints is below 200ms under typical load. Write endpoints target below 500ms.

#### NFR-P-2: Frontend Time-to-Interactive `[SHOULD]` `[M2]`

The initial page load is interactive within 3 seconds on a typical broadband connection. Subsequent navigation uses code-split routes loaded on demand.

#### NFR-P-3: Database Query Performance `[MUST]` `[M3]`

All read paths for the weight history use indexed lookups. The full table scan threshold is zero for queries hitting more than 100 rows. Composite indexes on `(user_id, observation_date)` and `(user_id, created_at)` are present.

#### NFR-P-4: Pagination Strategy `[MUST]` `[M3]`

Time-series data uses cursor-based pagination, not offset-based, to avoid the O(n) overhead of large offsets and to prevent inconsistency under concurrent writes.

#### NFR-P-5: Caching Strategy `[SHOULD]` `[M3]`

Computed values that are expensive and stable (recent rate-of-change, milestone counters) are cached server-side with a documented TTL.

### 7.3 Accessibility (NFR-A)

#### NFR-A-1: WCAG 2.1 Level AA Conformance `[MUST]` `[M2]`

The application conforms to WCAG 2.1 Level AA. This is verified through automated tooling (axe-core via Playwright) and manual checks documented in the testing strategy.

#### NFR-A-2: Keyboard Navigation `[MUST]` `[M2]`

Every interactive element is reachable and operable via keyboard alone. Focus order follows visual order. Focus indicators are visible.

#### NFR-A-3: Screen Reader Support `[MUST]` `[M2]`

Every interactive element exposes an accessible name. Form fields have associated labels. Status updates use ARIA live regions.

#### NFR-A-4: Color Contrast `[MUST]` `[M2]`

Text-to-background color contrast meets WCAG AA minimums (4.5:1 for normal text, 3:1 for large text). The color palette inherits from `[Weight_Tracker_Figma_Design_Specifications.md]` and is verified for contrast.

#### NFR-A-5: Touch and Click Targets `[MUST]` `[M2]`

All interactive targets are at least 44 by 44 CSS pixels. This requirement directly addresses the Android findings of 36dp and 32dp targets in `item_weight_entry.xml` and `activity_main.xml`.

#### NFR-A-6: Reduced Motion `[SHOULD]` `[M2]`

Animations honor the `prefers-reduced-motion` user setting.

### 7.4 Usability (NFR-U)

#### NFR-U-1: Form Inline Validation `[MUST]` `[M2]`

Forms display validation errors inline next to the affected field, with the first invalid field receiving focus on submission attempt.

#### NFR-U-2: Empty States `[MUST]` `[M2]`

Every page that displays a list provides an empty state with a clear call to action.

#### NFR-U-3: Loading States `[MUST]` `[M2]`

Asynchronous operations show a loading indicator or skeleton screen. The application never shows blank content for more than 500ms.

#### NFR-U-4: Error Recovery `[MUST]` `[M2]`

User-facing errors include both what happened and a recovery path (retry button, link to documentation, contact information where appropriate).

### 7.5 Maintainability (NFR-M)

#### NFR-M-1: Code Style Enforcement `[MUST]` `[M2]`

Linting and formatting are enforced by ruff (Python) and ESLint plus Prettier (TypeScript). Pre-commit hooks reject non-conforming commits locally; CI re-verifies on push.

#### NFR-M-2: Type Safety `[MUST]` `[M2]`

The Python codebase passes `mypy --strict`. The TypeScript codebase passes `tsc --noEmit` with `strict: true` in `tsconfig.json`.

#### NFR-M-3: Module Boundaries `[MUST]` `[M2]`

Imports across domain folders go through explicit interfaces rather than directly referencing concrete classes. This is verified by a lightweight architectural test that scans imports in CI.

#### NFR-M-4: Documentation Coverage `[SHOULD]` `[M2]`

Every public class, function, and module includes docstrings (Python) or JSDoc-style comments (TypeScript) explaining intent, parameters, return values, and exceptions.

#### NFR-M-5: ADR Practice `[MUST]` `[M2]`

Every nontrivial architectural decision is documented in a new ADR under `/docs/adr/`, sequentially numbered starting at 0007.

### 7.6 Testability (NFR-T)

#### NFR-T-1: Test-Driven Development `[MUST]` `[M2]`

Features are developed test-first. The commit history reflects red-green-refactor cadence.

#### NFR-T-2: Test Coverage Thresholds `[MUST]` `[M2]`

The backend maintains at least 85% line coverage and 80% branch coverage on the domain and application layers. The frontend maintains at least 90% line and branch coverage on components, hooks, and utilities.

#### NFR-T-3: Test Pyramid `[MUST]` `[M2]`

The test suite follows the standard pyramid shape: many fast unit tests, fewer integration tests, a small number of end-to-end tests.

#### NFR-T-4: Test Isolation `[MUST]` `[M2]`

Unit tests run without a database, network, or filesystem. Integration tests use an isolated, transactional database session that rolls back after each test.

#### NFR-T-5: Continuous Integration `[MUST]` `[M2]`

All tests run on every push and pull request via GitHub Actions. Builds fail when any test fails or coverage thresholds are not met.

### 7.7 Observability (NFR-O)

#### NFR-O-1: Structured Logging `[MUST]` `[M2]`

The backend emits structured JSON logs via structlog. Every log entry includes a timestamp, level, message, request ID (when in request context), and any structured context relevant to the event.

#### NFR-O-2: Request Tracing `[MUST]` `[M2]`

Every incoming HTTP request is assigned a unique request ID, propagated through all log entries for that request, and returned to the client in the `X-Request-ID` response header.

#### NFR-O-3: Health Check Endpoint `[MUST]` `[M2]`

The backend exposes `GET /health` returning 200 OK with the current commit SHA, build timestamp, and a database connectivity check.

#### NFR-O-4: Error Reporting `[SHOULD]` `[Final]`

Unhandled exceptions are reported with enough context to reproduce the issue, including the request ID, the user ID (when authenticated), and the relevant input shape (with PII masked).

### 7.8 Privacy (NFR-Priv)

#### NFR-Priv-1: PII Masking in Logs `[MUST]` `[M2]`

Email addresses and any future phone numbers are masked in logs by default. Only the last four characters of an email's local part and the domain are emitted (for example, `***ick@example.com`).

#### NFR-Priv-2: Data Minimization `[MUST]` `[M2]`

The application collects only the data required to deliver its features. No analytics, tracking, or third-party telemetry is included.

#### NFR-Priv-3: User Data Export `[SHOULD]` `[Final]`

The application provides an endpoint allowing a user to export their data in JSON.

#### NFR-Priv-4: User Data Deletion `[SHOULD]` `[Final]`

The application provides an endpoint allowing a user to permanently delete their account and associated data.

---

## 8. Data Architecture

### 8.1 Entity Overview

The web application's domain model carries forward the conceptual entities from the Android predecessor while taking the opportunity of a fresh schema to apply lessons learned. The full final-project schema includes seven tables. Milestone 2 implements a subset.

| Entity | Purpose | Milestone |
| --- | --- | --- |
| `users` | User account, credentials, profile | M2 |
| `refresh_tokens` | Server-side refresh token store with rotation | M2 |
| `weight_entries` | Daily weight observations | M2 |
| `goals` | Active and historical user goals | M3 |
| `achievements` | Goal and milestone achievement records | M3 |
| `user_preferences` | Key-value user-scoped settings | M3 |
| `audit_log` | Security and compliance event trail | M4 |

### 8.2 Schema Specification (PostgreSQL)

The schema uses PostgreSQL 16+ features. CHECK constraints enforce domain rules at the database level rather than relying solely on the application layer. The original Android implementation deferred validation entirely to application code; the web rebuild closes this defensive-programming gap.

#### 8.2.1 `users` (Milestone 2)

```sql
CREATE TABLE users (
    user_id         BIGSERIAL PRIMARY KEY,
    email           CITEXT NOT NULL UNIQUE,
    password_hash   TEXT NOT NULL,
    display_name    VARCHAR(50) NOT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_login_at   TIMESTAMPTZ,
    failed_login_count   INTEGER NOT NULL DEFAULT 0,
    locked_until    TIMESTAMPTZ,

    CONSTRAINT users_email_format CHECK (email ~* '^[^@\s]+@[^@\s]+\.[^@\s]+$'),
    CONSTRAINT users_display_name_length CHECK (length(trim(display_name)) BETWEEN 2 AND 50),
    CONSTRAINT users_failed_login_nonneg CHECK (failed_login_count >= 0)
);

CREATE INDEX idx_users_email_active ON users(email) WHERE is_active = TRUE;
```

The `CITEXT` extension provides case-insensitive email comparison without requiring application-layer normalization on every query.

#### 8.2.2 `refresh_tokens` (Milestone 2)

```sql
CREATE TABLE refresh_tokens (
    token_id        BIGSERIAL PRIMARY KEY,
    user_id         BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    token_hash      TEXT NOT NULL UNIQUE,
    family_id       UUID NOT NULL,
    issued_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at      TIMESTAMPTZ NOT NULL,
    revoked_at      TIMESTAMPTZ,
    replaced_by     BIGINT REFERENCES refresh_tokens(token_id),

    CONSTRAINT refresh_tokens_expiry_after_issuance CHECK (expires_at > issued_at)
);

CREATE INDEX idx_refresh_tokens_user_active
    ON refresh_tokens(user_id)
    WHERE revoked_at IS NULL;

CREATE INDEX idx_refresh_tokens_family ON refresh_tokens(family_id);
```

The `family_id` enables family-level revocation when token reuse is detected, which is a recognized refresh-token rotation security pattern. The full rotation policy is documented in `[ADR-0013]` (planned).

#### 8.2.3 `weight_entries` (Milestone 2)

```sql
CREATE TABLE weight_entries (
    entry_id        BIGSERIAL PRIMARY KEY,
    user_id         BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    weight_value    NUMERIC(6, 2) NOT NULL,
    weight_unit     VARCHAR(3) NOT NULL,
    observation_date    DATE NOT NULL,
    notes           VARCHAR(500),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_deleted      BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at      TIMESTAMPTZ,

    CONSTRAINT weight_entries_value_positive CHECK (weight_value > 0),
    CONSTRAINT weight_entries_value_max CHECK (weight_value <= 1500),
    CONSTRAINT weight_entries_unit_valid CHECK (weight_unit IN ('lbs', 'kg')),
    CONSTRAINT weight_entries_observation_not_future CHECK (observation_date <= CURRENT_DATE),
    CONSTRAINT weight_entries_deletion_consistency
        CHECK ((is_deleted = FALSE AND deleted_at IS NULL)
            OR (is_deleted = TRUE AND deleted_at IS NOT NULL))
);

CREATE UNIQUE INDEX idx_weight_entries_user_date_active
    ON weight_entries(user_id, observation_date)
    WHERE is_deleted = FALSE;

CREATE INDEX idx_weight_entries_user_observation_desc
    ON weight_entries(user_id, observation_date DESC)
    WHERE is_deleted = FALSE;
```

The database-level CHECK constraints close the defensive-programming finding from the Android code review where `daily_weights.weight_value` and `weight_unit` had no value-domain enforcement.

#### 8.2.4 `goals` (Milestone 3)

```sql
-- Schema defined in Milestone 3, summarized here for completeness
CREATE TABLE goals (
    goal_id         BIGSERIAL PRIMARY KEY,
    user_id         BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    target_value    NUMERIC(6, 2) NOT NULL,
    target_unit     VARCHAR(3) NOT NULL,
    start_value     NUMERIC(6, 2) NOT NULL,
    goal_type       VARCHAR(10) NOT NULL,
    target_date     DATE,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    is_achieved     BOOLEAN NOT NULL DEFAULT FALSE,
    achieved_at     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    -- CHECK constraints to be defined in Milestone 3
);
```

#### 8.2.5 `achievements` (Milestone 3)

Schema deferred to Milestone 3 documentation.

#### 8.2.6 `user_preferences` (Milestone 3)

Schema deferred to Milestone 3 documentation. Carries forward the key-value design from the Android `user_preferences` table.

#### 8.2.7 `audit_log` (Milestone 4)

Schema deferred to Milestone 4 documentation. Captures authentication events, sensitive data access, and administrative actions for compliance and security review.

### 8.3 Migration Strategy

All schema changes flow through Alembic migrations. Each migration is a single logical change with both `upgrade` and `downgrade` paths. Migrations are reviewed and run in CI against a fresh database to validate they can be applied from scratch.

| Migration | Purpose | Milestone |
| --- | --- | --- |
| `0001_initial_users_and_auth` | Create `users` and `refresh_tokens` tables, install CITEXT extension | M2 |
| `0002_weight_entries` | Create `weight_entries` table with constraints and indexes | M2 |
| `0003_goals` | Create `goals` table | M3 |
| `0004_achievements` | Create `achievements` table | M3 |
| `0005_user_preferences` | Create `user_preferences` table | M3 |
| `0006_performance_indexes` | Add composite and partial indexes for trend queries | M3 |
| `0007_audit_log` | Create `audit_log` table | M4 |
| `0008_constraint_hardening` | Add additional CHECK constraints and tighten column types | M4 |

### 8.4 Database Connection Policy

The application connects to PostgreSQL with SSL required in all environments. Connection strings are loaded from environment variables. Connection pooling is managed by SQLAlchemy's `QueuePool` with a default pool size of 5 and overflow of 10 for development; production tuning is out of scope.

---

## 9. API Specification

### 9.1 Conventions

The API is REST-shaped with JSON request and response bodies. Versioning is in the URL path: every route begins with `/api/v1/`. Future major versions get new path prefixes.

| Concern | Convention |
| --- | --- |
| Content Type | `application/json` for requests and responses |
| Date and Time | ISO 8601 with timezone, UTC where unspecified |
| IDs | Bigint internal IDs in URLs and responses |
| Errors | RFC 7807 Problem Details format |
| Pagination | Cursor-based with `limit` and `cursor` query parameters |
| Filtering | Query parameters (deferred to specific endpoints) |
| Authentication | HTTP-only cookies; no Authorization header |

### 9.2 Error Model

Errors follow RFC 7807 Problem Details:

```json
{
  "type": "https://api.weighttogo.example/errors/validation-error",
  "title": "Validation failed",
  "status": 422,
  "detail": "The submitted data did not pass validation.",
  "instance": "/api/v1/weight-entries",
  "request_id": "01HXX...",
  "errors": [
    {
      "field": "weight_value",
      "code": "value_out_of_range",
      "message": "Weight value must be between 1 and 1500."
    }
  ]
}
```

| HTTP Status | Meaning | Typical Cause |
| --- | --- | --- |
| 400 | Bad Request | Malformed JSON, missing required headers |
| 401 | Unauthorized | Missing or invalid session |
| 403 | Forbidden | Authenticated but action not permitted |
| 404 | Not Found | Resource does not exist or is not visible to caller |
| 409 | Conflict | Duplicate resource or business rule violation |
| 422 | Unprocessable Entity | Validation failed |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Unhandled exception (logged with full context) |

### 9.3 Authentication Endpoints (Milestone 2)

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| `POST` | `/api/v1/auth/register` | None | Create a new user account |
| `POST` | `/api/v1/auth/login` | None | Authenticate and receive session cookies |
| `POST` | `/api/v1/auth/logout` | Required | End the current session, revoke refresh token |
| `POST` | `/api/v1/auth/refresh` | Refresh cookie | Rotate tokens, return new session |
| `GET` | `/api/v1/auth/me` | Required | Return current user identity |

#### 9.3.1 Register Request Schema

```json
{
  "email": "string (RFC 5322)",
  "password": "string (12+ chars, meets complexity)",
  "display_name": "string (2-50 chars)"
}
```

#### 9.3.2 Login Request Schema

```json
{
  "email": "string",
  "password": "string"
}
```

#### 9.3.3 Authenticated User Response Schema

```json
{
  "user_id": 12345,
  "email": "user@example.com",
  "display_name": "Jane Doe",
  "created_at": "2026-01-15T14:30:00Z"
}
```

### 9.4 Weight Entry Endpoints (Milestone 2)

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| `POST` | `/api/v1/weight-entries` | Required | Create a weight entry |
| `GET` | `/api/v1/weight-entries` | Required | List weight entries (paginated) |
| `GET` | `/api/v1/weight-entries/{entry_id}` | Required | Retrieve a single weight entry |
| `PUT` | `/api/v1/weight-entries/{entry_id}` | Required | Update a weight entry |
| `DELETE` | `/api/v1/weight-entries/{entry_id}` | Required | Soft-delete a weight entry |

#### 9.4.1 Create Weight Entry Request Schema

```json
{
  "weight_value": 175.5,
  "weight_unit": "lbs",
  "observation_date": "2026-05-20",
  "notes": "Optional notes (max 500 chars)"
}
```

#### 9.4.2 Weight Entry Response Schema

```json
{
  "entry_id": 42,
  "weight_value": 175.5,
  "weight_unit": "lbs",
  "observation_date": "2026-05-20",
  "notes": "Optional notes",
  "created_at": "2026-05-20T08:15:30Z",
  "updated_at": "2026-05-20T08:15:30Z"
}
```

#### 9.4.3 List Weight Entries Response Schema

```json
{
  "items": [ /* array of weight entries */ ],
  "next_cursor": "opaque-base64-cursor-string-or-null"
}
```

### 9.5 Dashboard Endpoint (Milestone 2)

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/api/v1/dashboard/summary` | Required | Aggregated summary for the dashboard |

```json
{
  "latest_entry": { /* weight entry or null */ },
  "total_entries": 47,
  "active_goal": null
}
```

### 9.6 Goal Endpoints (Milestone 3)

Documented for completeness. Implementation deferred.

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/api/v1/goals` | Set a new active goal |
| `GET` | `/api/v1/goals/active` | Get the user's active goal with progress |
| `GET` | `/api/v1/goals` | List all goals (active and historical) |
| `PUT` | `/api/v1/goals/{goal_id}` | Update a goal |
| `DELETE` | `/api/v1/goals/{goal_id}` | Abandon a goal |

### 9.7 Achievement Endpoints (Milestone 3)

Documented for completeness. Implementation deferred.

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/api/v1/achievements` | List user's achievements |
| `GET` | `/api/v1/achievements/{achievement_id}` | Retrieve a specific achievement |

### 9.8 Preferences Endpoints (Milestone 3)

Documented for completeness. Implementation deferred.

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/api/v1/preferences` | Retrieve user preferences |
| `PUT` | `/api/v1/preferences/{key}` | Update a single preference value |

### 9.9 OpenAPI Documentation

FastAPI auto-generates the OpenAPI 3.1 schema from Pydantic models and route signatures. The schema is available at:

| Path | Purpose |
| --- | --- |
| `/api/v1/openapi.json` | Raw OpenAPI JSON document |
| `/api/docs` | Swagger UI for interactive exploration |
| `/api/redoc` | ReDoc rendering of the same schema |

A snapshot of the OpenAPI document is committed to `/docs/api/openapi-snapshot.json` after each milestone and reviewed for unintended schema changes.


---

## 10. Frontend Specification

### 10.1 Routing

The frontend uses React Router v7 with declarative route definitions and code-split routes. This design directly replaces the hardcoded if-elseif navigation chain in the Android predecessor (lines 311-333 of `MainActivity.java`), where adding a new screen required modifying the central dispatcher.

#### 10.1.1 Public Routes

| Path | Component | Description |
| --- | --- | --- |
| `/login` | `LoginPage` | Email and password authentication form |
| `/register` | `RegisterPage` | New user registration form |

#### 10.1.2 Protected Routes

Protected routes require authentication. An unauthenticated user attempting access is redirected to `/login` with the original destination preserved as a query parameter for post-login redirect.

| Path | Component | Milestone | Description |
| --- | --- | --- | --- |
| `/` | `DashboardPage` | M2 | Primary landing page after login |
| `/weight` | `WeightHistoryPage` | M2 | Full weight entry list with CRUD |
| `/weight/new` | `WeightEntryFormPage` | M2 | Create a new weight entry |
| `/weight/:entryId/edit` | `WeightEntryFormPage` | M2 | Edit an existing weight entry |
| `/goals` | `GoalsPlaceholderPage` | M2 (placeholder), M3 (full) | Goal management |
| `/achievements` | `AchievementsPlaceholderPage` | M2 (placeholder), M3 (full) | Achievement history |
| `/settings` | `SettingsPlaceholderPage` | M2 (placeholder), M3 (full) | User preferences |

#### 10.1.3 Placeholder Page Requirements

Each placeholder page (`GoalsPlaceholderPage`, `AchievementsPlaceholderPage`, `SettingsPlaceholderPage`) is fully accessible, auth-gated, and renders a clear "Coming in Milestone N" notice with a brief description of what the page will contain. Placeholders are not mocked-out stubs; they are real components that real users would see during the M2 demonstration.

### 10.2 Layouts and Navigation

The application has two layouts that wrap all routes:

| Layout | Used By | Composition |
| --- | --- | --- |
| `AuthLayout` | Public routes | Centered card with app branding, no nav |
| `AppLayout` | Protected routes | App bar, side navigation (collapsible on mobile), main outlet, footer |

The side navigation in `AppLayout` is a declarative list of route definitions consumed by a `NavList` component, not a series of hardcoded conditional branches. Adding a new top-level navigation item requires updating the list and adding the route definition; no central dispatcher edit is needed.

### 10.3 Forms and Validation

All forms use React Hook Form for state management combined with Zod schemas for validation. The same Zod schemas are used for TypeScript type derivation, providing a single source of truth.

#### 10.3.1 Form Pattern

```typescript
// Conceptual example only, not implementation
const WeightEntrySchema = z.object({
  weight_value: z.number().positive().max(1500),
  weight_unit: z.enum(['lbs', 'kg']),
  observation_date: z.string().refine(isNotFuture),
  notes: z.string().max(500).optional(),
});

type WeightEntryFormValues = z.infer<typeof WeightEntrySchema>;
```

#### 10.3.2 Validation Behavior

- Validation runs on blur for each field and on submit for the full form
- The first invalid field receives focus on submission attempt
- Server-side validation errors from 422 responses are mapped to field-level errors using the `errors[].field` mapping from the RFC 7807 response

### 10.4 State Management

The application uses React's built-in primitives. State is colocated with the component that owns it when possible, lifted to a Context provider when shared across siblings, and persisted to the backend when it represents domain data.

| State Category | Mechanism |
| --- | --- |
| Form state | React Hook Form (per-form) |
| Authentication state | `AuthContext` provider at the app root |
| Theme and preferences | `PreferencesContext` provider |
| Server data | Component-local state plus a small fetch helper; React Query is acceptable if complexity grows |
| Routing state | React Router |

Redux is not used in Milestone 2. The decision is revisited if cross-component state coordination becomes painful in later milestones.

### 10.5 Component Inventory

Each domain folder under `frontend/src/features/` contains the components, hooks, and types for one feature. Shared components live under `frontend/src/components/`. The structure parallels the backend's Screaming Architecture organization.

```
frontend/src/
├── features/
│   ├── auth/
│   │   ├── components/
│   │   │   ├── LoginForm.tsx
│   │   │   ├── RegisterForm.tsx
│   │   │   └── AuthLayout.tsx
│   │   ├── hooks/
│   │   │   └── useAuth.ts
│   │   ├── pages/
│   │   │   ├── LoginPage.tsx
│   │   │   └── RegisterPage.tsx
│   │   ├── schemas/
│   │   │   └── auth-schemas.ts
│   │   └── api/
│   │       └── auth-client.ts
│   ├── weight/
│   │   └── (parallel structure)
│   ├── dashboard/
│   │   └── (parallel structure)
│   └── placeholders/
│       └── (Goals, Achievements, Settings placeholder pages)
├── components/                  # Truly shared, generic components
│   ├── AppLayout.tsx
│   ├── NavList.tsx
│   ├── EmptyState.tsx
│   ├── LoadingSpinner.tsx
│   └── ErrorBoundary.tsx
├── lib/                         # Cross-cutting utilities
│   ├── api-client.ts
│   ├── error-mapping.ts
│   └── format.ts
├── contexts/
│   ├── AuthContext.tsx
│   └── PreferencesContext.tsx
├── theme/
│   └── (Material UI theme, palette inheriting from Figma specs)
├── App.tsx
├── main.tsx
└── routes.tsx
```

### 10.6 Styling

Material UI provides the component library and design tokens. The theme is configured at the app root using the color palette defined in `Weight_Tracker_Figma_Design_Specifications.md`:

| Token | Value |
| --- | --- |
| Primary | `#00897B` (Teal) |
| Primary Dark | `#00695C` |
| Primary Light | `#4DB6AC` |
| Success | `#4CAF50` |
| Warning | `#FF9800` |
| Error | `#F44336` |
| Background | `#F5F5F5` |
| Text Primary | `#212121` |
| Text Secondary | `#757575` |

Custom styling beyond the theme uses Material UI's `sx` prop or styled components. No CSS modules, no Tailwind, no global stylesheets beyond a normalize layer.

---

## 11. Quality Engineering

### 11.1 Test-Driven Development

Features are developed test-first. The intended cadence is red, green, refactor:

1. **Red.** Write a failing test that describes the desired behavior.
2. **Green.** Write the minimum production code that makes the test pass.
3. **Refactor.** Improve the code's design without changing behavior, with tests as the safety net.

Commits reflect this cadence. A single commit containing both test and implementation is acceptable when the increment is small, but the bias is toward separate commits for test and implementation when the change is nontrivial.

### 11.2 Test Pyramid

The test suite follows the standard pyramid shape with many fast tests at the base and few slow tests at the top.

```
                    +---------------+
                    |   E2E (slow)  |    Playwright, ~5-15 tests
                    +-------+-------+
                            |
                +-----------+-----------+
                |  Integration (medium) |  pytest + transactional DB
                +-----------+-----------+   ~50-100 tests
                            |
                +-----------+-------------------+
                |       Unit (fast)             |  Vitest + pytest
                +-------------------------------+  hundreds of tests
```

### 11.3 Backend Testing

#### 11.3.1 Unit Tests

Domain and application layers are tested without a database, network, or filesystem. Tests instantiate domain entities and use cases directly, passing in-memory fakes for repository interfaces. Tests run in milliseconds.

#### 11.3.2 Integration Tests

Integration tests verify the full stack from FastAPI router through SQLAlchemy to PostgreSQL using a real database in a transactional session that rolls back after each test. A test fixture provisions a fresh schema per test session.

#### 11.3.3 Test Organization

```
backend/tests/
├── unit/
│   ├── auth/
│   ├── weight/
│   └── shared/
├── integration/
│   ├── auth/
│   ├── weight/
│   └── api/
├── fixtures/
│   └── database.py
└── conftest.py
```

### 11.4 Frontend Testing

#### 11.4.1 Component Tests

React Testing Library tests verify component behavior from the user's perspective. Tests interact with components via accessible queries (role, label, text) rather than implementation details (CSS classes, internal state).

#### 11.4.2 Hook Tests

Custom hooks are tested in isolation using React Testing Library's `renderHook` utility.

#### 11.4.3 End-to-End Tests

Playwright tests cover happy-path user journeys across real browsers. End-to-end coverage targets are intentionally modest:

| Journey | Milestone |
| --- | --- |
| New user registration through first weight entry | M2 |
| Returning user login and dashboard view | M2 |
| Weight entry edit and delete | M2 |
| Goal creation and progress visualization | M3 |
| Achievement notification flow | M3 |

### 11.5 Coverage Thresholds

| Layer | Line Coverage | Branch Coverage |
| --- | --- | --- |
| Backend domain | 95% | 90% |
| Backend application | 90% | 85% |
| Backend infrastructure | 80% | 75% |
| Backend interface | 80% | 75% |
| Frontend components | 90% | 90% |
| Frontend hooks | 90% | 90% |
| Frontend utilities | 90% | 90% |

CI builds fail when coverage drops below threshold on any layer.

### 11.6 Static Analysis

| Tool | Stack | Purpose |
| --- | --- | --- |
| `ruff check` | Python | Linting |
| `ruff format` | Python | Formatting (replaces black) |
| `mypy --strict` | Python | Type checking |
| `ESLint` | TypeScript | Linting |
| `Prettier` | TypeScript | Formatting |
| `tsc --noEmit` | TypeScript | Type checking |
| `pip-audit` | Python | Dependency vulnerability scan |
| `npm audit` | Node | Dependency vulnerability scan |
| `axe-core` (via Playwright) | Frontend | Accessibility audit |

### 11.7 Code Review Practice

The artifact is a solo project so traditional peer review is not available. The author uses the CS 499 Code Review Checklist as a self-review tool against every pull request. The checklist findings are recorded as PR comments by the author and addressed before merge.

### 11.8 Documentation Standards

Every public class, function, and module includes documentation explaining intent and contracts. Python uses Google-style docstrings. TypeScript uses JSDoc with `@param`, `@returns`, and `@throws` tags. Inline comments explain why, not what.

---

## 12. DevOps and Tooling

### 12.1 Development Environment

The application runs locally with the following dependencies:

| Tool | Version | Purpose |
| --- | --- | --- |
| Node.js | 20 LTS or 22 LTS | Frontend runtime |
| Python | 3.12+ | Backend runtime |
| Docker Desktop | Recent | PostgreSQL container |
| Git | 2.40+ | Version control |
| direnv (optional) | Recent | Auto-loading `.env` per directory |

### 12.2 Local Setup Procedure

A new contributor should be able to clone, set up, and run the application in under 15 minutes following the README. The high-level steps:

1. Clone the repository
2. Copy `.env.example` to `.env` in both `web/frontend/` and `web/backend/`, populate values
3. Start the PostgreSQL container via `docker compose up -d` in `web/backend/`
4. In `web/backend/`, install Python dependencies via Poetry or uv
5. Run `alembic upgrade head` to apply migrations
6. Start the backend via `uvicorn weighttogo.main:app --reload`
7. In `web/frontend/`, install Node dependencies via `npm install` or `pnpm install`
8. Start the frontend via `npm run dev`
9. Open `http://localhost:5173` (Vite default)

### 12.3 Build and Package Management

#### 12.3.1 Backend Commands

| Command | Purpose |
| --- | --- |
| `uv run uvicorn weighttogo.main:app --reload` | Development server with auto-reload |
| `uv run pytest` | Run all backend tests |
| `uv run pytest --cov=weighttogo --cov-report=html` | Run tests with coverage report |
| `uv run ruff check .` | Lint check |
| `uv run ruff format .` | Apply formatting |
| `uv run mypy src` | Type check |
| `uv run alembic upgrade head` | Apply all pending migrations |
| `uv run alembic revision --autogenerate -m "message"` | Generate a new migration |

#### 12.3.2 Frontend Commands

| Command | Purpose |
| --- | --- |
| `npm run dev` | Vite development server |
| `npm run build` | Production bundle |
| `npm run preview` | Preview production bundle locally |
| `npm run test` | Run Vitest in watch mode |
| `npm run test:ci` | Run Vitest once with coverage |
| `npm run test:e2e` | Run Playwright tests |
| `npm run lint` | ESLint check |
| `npm run format` | Prettier write |
| `npm run typecheck` | `tsc --noEmit` |

### 12.4 CI/CD Pipelines

Three GitHub Actions workflows run in parallel on every push and pull request:

| Workflow | Trigger | Purpose |
| --- | --- | --- |
| `android-ci.yml` | Changes under `/android/` | Existing Android workflow, working directory updated |
| `backend-ci.yml` | Changes under `/web/backend/` | Lint, type check, unit and integration tests, coverage |
| `frontend-ci.yml` | Changes under `/web/frontend/` | Lint, type check, component and hook tests, coverage |
| `e2e.yml` | Pull request | Playwright end-to-end tests across browsers |
| `security-audit.yml` | Daily and on PR | `pip-audit` and `npm audit` |

A pull request cannot merge unless all relevant workflows pass.

### 12.5 Secrets Management

Secrets are managed via environment variables loaded from `.env` files in development and from GitHub Actions secrets in CI.

#### 12.5.1 Backend `.env` Variables

| Variable | Purpose | Example |
| --- | --- | --- |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+psycopg://user:pass@localhost:5432/weighttogo_dev?sslmode=require` |
| `JWT_SECRET_KEY` | JWT signing key (256-bit minimum) | Generated via `openssl rand -base64 32` |
| `JWT_ACCESS_TOKEN_TTL_SECONDS` | Access token lifetime | `900` (15 minutes) |
| `JWT_REFRESH_TOKEN_TTL_DAYS` | Refresh token lifetime | `7` |
| `BCRYPT_COST_FACTOR` | bcrypt cost | `12` |
| `CORS_ALLOWED_ORIGINS` | Comma-separated allowlist | `http://localhost:5173` |
| `LOG_LEVEL` | Backend log verbosity | `INFO` |
| `ENVIRONMENT` | `development`, `test`, `production` | `development` |

#### 12.5.2 Frontend `.env` Variables

| Variable | Purpose | Example |
| --- | --- | --- |
| `VITE_API_BASE_URL` | Backend base URL | `http://localhost:8000/api/v1` |
| `VITE_ENABLE_DEVTOOLS` | Toggle dev-only UI | `true` |

### 12.6 Database in Docker Compose

The repository ships a `docker-compose.yml` under `web/backend/` that provisions PostgreSQL only. The application itself is not containerized in Milestone 2.

```yaml
# Conceptual only, not the literal file
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: weighttogo
      POSTGRES_PASSWORD: <from .env>
      POSTGRES_DB: weighttogo_dev
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
volumes:
  postgres_data:
```

### 12.7 Conventions

#### 12.7.1 Commit Messages

The repository uses Conventional Commits (`feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:`, `perf:`, `ci:`). This convention is already established in the Android codebase and is carried forward.

#### 12.7.2 File Naming

| Stack | Convention | Example |
| --- | --- | --- |
| Python | `snake_case.py` | `weight_repository.py` |
| Python class names | `PascalCase` | `WeightRepository` |
| TypeScript components | `PascalCase.tsx` | `WeightEntryForm.tsx` |
| TypeScript utilities | `kebab-case.ts` | `format-date.ts` |
| TypeScript hooks | `useCamelCase.ts` | `useAuth.ts` |

---

## 13. Milestone Roadmap

### 13.1 Milestone 2: Software Design and Engineering (Primary Focus)

Milestone 2 delivers the architectural foundation and a single vertical slice that exercises every layer. The deliverable is a working application demonstrating the rebuild's design patterns end-to-end on authentication and weight entry CRUD.

#### 13.1.1 Deliverables

1. **Repository restructure complete.** All Android code moved under `/android/`, web folders created, ADR-0007 and ADR-0008 documenting the web rebuild and polyglot monorepo decisions committed.
2. **Backend skeleton with auth and weight entry CRUD.** FastAPI application running locally with all endpoints from sections 9.3 and 9.4 implemented and tested.
3. **Frontend skeleton with auth and weight entry CRUD.** React application running locally with all routes from section 10.1 implemented, including placeholder pages for deferred features.
4. **PostgreSQL schema for M2 entities.** Alembic migrations `0001` and `0002` applied, tables verified against the spec.
5. **Full CI pipeline.** GitHub Actions workflows for backend, frontend, and the preserved Android workflow all green.
6. **Test coverage at thresholds.** Backend domain at 95%, frontend at 90% lines and branches.
7. **ADRs 0007 through 0013 committed.** Web rebuild rationale, polyglot monorepo, email as identifier, generic auth errors, PII masking in logs, three-pattern backend architecture, refresh token rotation.
8. **README rewritten.** Tells the mobile-to-web story, includes setup instructions, links to ADRs and this SRS.

#### 13.1.2 In-Scope Functional Requirements

All `[M2]`-tagged requirements from section 6:

- FR-A-1 through FR-A-5, FR-A-9, FR-A-10 (Authentication)
- FR-W-1 through FR-W-5 (Weight Entry CRUD)
- FR-D-1 (Dashboard summary, with goal section as placeholder)

#### 13.1.3 In-Scope Non-Functional Requirements

All `[M2]`-tagged requirements from section 7. The security, accessibility, maintainability, testability, observability, and privacy baselines must be in place from the first feature delivered.

#### 13.1.4 Mock and Defer Policy

The following are not implemented in Milestone 2:

| Item | Treatment |
| --- | --- |
| Goal management | Placeholder page at `/goals` with "Coming in Milestone 3" message |
| Achievement display | Placeholder page at `/achievements` |
| User preferences | Placeholder page at `/settings` |
| SMS notifications | Not present; design preserved for later |
| Weekly rate of change | Not computed |
| Charting | Not present; dashboard shows tabular summary |
| Caching layer | Not present; queries are direct |
| Composite indexes for trend queries | Deferred to M3 migration |
| Audit log table | Deferred to M4 |

### 13.2 Milestone 3: Algorithms and Data Structures

Milestone 3 introduces algorithmic complexity that the architecture is designed to host. Domain logic appears here, not in M2.

#### 13.2.1 Deliverables

1. **Goal management.** All FR-G requirements implemented with database persistence.
2. **Achievement detection.** All FR-Ach requirements with milestone detection running on every weight entry.
3. **Streak detection.** FR-Ach-3 with an efficient single-pass longest-run scan over a set-backed sorted date sequence (see ADR-0022 for the algorithm choice and the longest-run vs. rolling-window rationale).
4. **Cursor-based pagination.** FR-W-2 upgraded from naive to cursor-based with full ADR documentation.
5. **TTL-based caching layer.** NFR-P-5 implemented for rate-of-change calculations.
6. **Weekly rate of change.** FR-D-3 using two indexed lookups against composite indexes.
7. **Charts on dashboard.** FR-D-2 with Recharts or equivalent.
8. **ADRs covering algorithmic choices.** Pagination strategy, caching strategy, milestone detection algorithm, streak detection algorithm.

### 13.3 Milestone 4: Databases

Milestone 4 enhances the persistence layer with constraints, indexes, and operational concerns that demonstrate database engineering competency.

#### 13.3.1 Deliverables

1. **Audit log.** Table and write paths implemented per section 8.2.7.
2. **Constraint hardening.** Additional CHECK constraints and column-type tightening.
3. **Performance indexes.** Composite and partial indexes for all read paths.
4. **Migration discipline review.** All Alembic migrations reviewed and rationalized; rollback paths verified.
5. **Database documentation.** Updated database architecture document reflecting the final schema and rationale for each constraint and index.
6. **Backup and restore procedure.** Documented but not necessarily automated (scope-appropriate).
7. **ADRs covering database engineering decisions.** Constraint strategy, indexing strategy, audit log structure.

### 13.4 Final Polish

The final submission window addresses anything deferred, polishes the narrative, and prepares the ePortfolio.

#### 13.4.1 Deliverables

1. **Code review video.** Already completed in Milestone 1.
2. **Three narrative documents.** One per category, written as the milestones complete.
3. **ePortfolio.** Hosted on GitHub Pages, links the artifact and all narratives.
4. **Self-assessment.** Required by capstone rubric.
5. **Final README pass.** Ensures top-level narrative is coherent across the full mobile-to-web evolution.
6. **Optional stretch items.** Password reset, email notifications, SMS notifications, dark theme, weight data export.

---

## 14. Acceptance Criteria and Definition of Done

### 14.1 Definition of Done (Per Pull Request)

A pull request is ready to merge only when all of the following hold:

- [ ] All new and changed functionality is covered by tests written test-first
- [ ] All CI workflows pass (lint, type check, tests, coverage, security audit)
- [ ] Coverage thresholds are met or exceeded
- [ ] Any new architectural decision is documented in an ADR
- [ ] Any new public API is documented (docstrings, JSDoc, or OpenAPI)
- [ ] User-facing changes maintain accessibility conformance (verified by axe-core)
- [ ] No PII appears in logs added by the change
- [ ] No secrets are committed
- [ ] Commit messages follow Conventional Commits
- [ ] The branch is up to date with `main`

### 14.2 Definition of Done (Milestone 2)

Milestone 2 is complete when all of the following hold:

- [ ] Every deliverable in section 13.1.1 is present and merged to `main`
- [ ] Every `[M2]` functional requirement from section 6 passes its acceptance criteria
- [ ] Every `[M2]` non-functional requirement from section 7 is verifiable
- [ ] The application can be cloned, set up, and run by following the README in under 15 minutes on a clean machine
- [ ] The narrative document is written and reviewed against the rubric
- [ ] The repository is tagged `v0.1.0`

### 14.3 Definition of Done (Final Project)

The final project is complete when:

- [ ] Every functional requirement (not just M2 ones) is either implemented or deliberately deferred with documented rationale
- [ ] The ePortfolio is live, complete, and reviewed
- [ ] All three narrative documents are present and submitted
- [ ] The repository is tagged `v1.0.0`

---

## 15. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| Repo restructure breaks the Android build | Medium | High | Test the restructure on a branch with all 373 Android tests run before merge |
| PostgreSQL setup friction slows M2 start | Medium | Medium | Provide working docker-compose.yml from day one; document the setup in the README |
| Coverage thresholds prove impractical in early commits | Low | Medium | Apply thresholds only after the first feature is complete; ratchet up over time |
| TDD discipline slips under deadline pressure | Medium | Medium | Use ADRs to capture deviations; document any test-after work in the narrative |
| ADR practice becomes paperwork rather than reasoning | Low | Low | Write ADRs only for decisions with viable alternatives, not for forced moves |
| Material UI version churn breaks UI mid-project | Low | Medium | Pin Material UI minor version in lockfile; upgrade deliberately between milestones |
| Authentication implementation has a subtle bug | Medium | High | Use established libraries; cover refresh rotation, token reuse detection, and lockout with explicit tests |
| Frontend and backend Pydantic-Zod schemas drift | Medium | Medium | Generate TypeScript types from the OpenAPI snapshot in CI and fail on drift |

---

## 16. Glossary

| Term | Definition |
| --- | --- |
| Access Token | Short-lived JWT used to authenticate API requests, delivered in an HTTP-only cookie |
| Adapter | A concrete implementation of a domain port, typically wrapping a framework or external system |
| Architecture Decision Record (ADR) | A short markdown document recording a single architectural decision and the alternatives considered |
| Backend | The FastAPI Python application that exposes the REST API |
| Bcrypt | Industry-standard password hashing algorithm with adjustable cost factor |
| Capstone | The CS 499 final course where students integrate program-wide skills |
| Cursor-Based Pagination | Pagination strategy where the client passes an opaque cursor token instead of an offset, enabling stable iteration under concurrent writes |
| Frontend | The React TypeScript browser application |
| FastAPI | A modern Python web framework with first-class async and OpenAPI support |
| JWT | JSON Web Token; a signed, self-contained token format |
| Material UI (MUI) | A React component library implementing the Material Design specification |
| Polyglot Monorepo | A single source repository containing multiple language stacks |
| Port | An interface defined by the domain that an adapter implements |
| Refresh Token | Longer-lived token used to obtain new access tokens without re-authentication |
| Soft Delete | Marking a row as deleted via a flag rather than removing it, enabling recovery and audit |
| Vite | A fast frontend build tool used in this project |

---

## 17. Appendix A: ADR Index

### 17.1 Existing ADRs (from Android Artifact)

The original six ADRs in `/docs/adr/` remain in place and continue to inform the web rebuild.

| ID | Title | Status |
| --- | --- | --- |
| ADR-0001 | Initial Database Architecture (SQLite) | Accepted |
| ADR-0002 | Database Versioning Strategy (Manual SQL Migrations) | Accepted |
| ADR-0003 | Overall Application Architecture (MVC) | Accepted |
| ADR-0004 | Global Weight Unit Preference Architecture | Accepted |
| ADR-0005 | Dependency Injection for Testing (Package-Private Setter Injection) | Accepted |
| ADR-0006 | Emulator SMS Testing | Accepted |

### 17.2 Web Rebuild ADRs

The following ADRs are written as their decisions are made. They build on the existing six, with cross-references where the web decision supersedes or extends a mobile one.

| ID | Title | Milestone |
| --- | --- | --- |
| ADR-0007 | Rebuild Weigh to Go! as a Full-Stack Web Application | M2 |
| ADR-0008 | Polyglot Monorepo for the Mobile-Web Artifact | M2 |
| ADR-0009 | Email as Primary User Identifier (Supersedes Username Primary from Android) | M2 |
| ADR-0010 | Generic Authentication Error Policy | M2 |
| ADR-0011 | PII Masking Strategy in Logs | M2 |
| ADR-0012 | Three-Pattern Backend Architecture (Screaming + Clean + Hexagonal) | M2 |
| ADR-0013 | Refresh Token Rotation with Family-Based Revocation | M2 |
| ADR-0014 | TanStack Query for Server State | M2 |
| ADR-0015 | Opaque Compound Cursor for Weight-Entry Pagination | M2 |
| ADR-0016 | TTL-Based Server-Side Caching Strategy | M3 (planned) |
| ADR-0017 | Milestone Detection Algorithm | M3 (planned) |
| ADR-0018 | Composite Index Strategy for Trend Queries | M3 (planned) |
| ADR-0019 | Audit Log Schema and Write Strategy | M4 (planned) |
| ADR-0020 | CHECK Constraint Inventory and Database-Level Validation Policy | M4 (planned) |

---

## 18. Appendix B: Course Outcome Alignment

The CS 499 capstone evaluates five program outcomes. The web rebuild touches each outcome through the deliverables described in this document.

| Course Outcome (paraphrased from CS 499 syllabus) | Where Demonstrated in the Web Rebuild |
| --- | --- |
| Employ strategies for building collaborative environments that enable diverse audiences to support organizational decision making | ADRs in `/docs/adr/`, code review checklist self-application, README written for external readers |
| Design and evaluate computing solutions using algorithmic principles and computer science practices and standards appropriate to its solution while managing trade-offs involved in design choices | Three-pattern architecture, cursor-based pagination, milestone detection, composite indexes, all with documented trade-offs |
| Design, develop, and deliver professional-quality oral, written, and visual communications that are coherent, technically sound, and appropriately adapted to specific audiences and contexts | This SRS, ADRs, narrative documents, OpenAPI auto-documentation, README |
| Demonstrate an ability to use well-founded and innovative techniques, skills, and tools in computing practices for the purpose of implementing computer solutions that deliver value and accomplish industry-specific goals | React, TypeScript, FastAPI, Pydantic, SQLAlchemy, PostgreSQL, Vite, ruff, all current and industry-standard |
| Develop a security mindset that anticipates adversarial exploits in software architecture and designs to expose potential vulnerabilities, mitigate design flaws, and ensure privacy and enhanced security of data and resources | Bcrypt password hashing, refresh token rotation, generic error messages, PII masking, rate limiting, account lockout, strict CORS, security headers, dependency auditing |

---

## 19. Appendix C: Source Document References

This SRS draws on the following source documents from the existing artifact and the capstone curriculum.

| Source | Location |
| --- | --- |
| CS 499 Milestone One Code Review Script (v7) | `/CS_499_Milestone_One_Code_Review_Script_v7.docx` |
| CS 499 Milestone Two Guidelines and Rubric | `/CS_499_Milestone_Two_Guidelines_and_Rubric.md` |
| CS 499 Module One Assignment (v6) | `/CS_499_Module_One_Assignment_v6.docx` |
| CS 499 Final Project Guidelines and Rubric | `/CS_499_Final_Project_Guidelines_and_Rubric.md` |
| CS 499 Code Review Checklist | `/cs499_code_review_checklist.md` |
| Android Weight Tracking App Requirements (v2) | `WeighToGo:/docs/requirements/Weight_Tracking_App_Requirements_v2.md` |
| Android Database Architecture | `WeighToGo:/docs/architecture/WeighToGo_Database_Architecture.md` |
| Figma Design Specifications | `WeighToGo:/docs/design/Weight_Tracker_Figma_Design_Specifications.md` |
| Figma Quick Start Guide | `WeighToGo:/docs/design/Weight_Tracker_Figma_Quick_Start_Guide.md` |
| ADR-0001 through ADR-0006 | `WeighToGo:/docs/adr/` |

---

**End of Document**

