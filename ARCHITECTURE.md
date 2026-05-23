# Architecture

This file is a 30-second orientation. The **authoritative architecture
specification** for the web rebuild is [SRS §4 — Architecture](docs/specs/WeighToGo_Web_SRS_v1.md#4-architecture).
When this file and the SRS disagree, the SRS wins.

## Two stacks, one repository

WeighToGo is a polyglot monorepo:

```
                ┌──────────────────────────────────────────────┐
                │              WeighToGo monorepo              │
                ├──────────────────────┬───────────────────────┤
                │      android/        │         web/          │
                │   (preserved Java    │  (active Python +     │
                │    artifact, CS 360) │   TypeScript rebuild) │
                └──────────────────────┴───────────────────────┘
                  Maintenance-only         Active development
                  Original architecture    Three-pattern backend
                  (MVC, SQLite)            (Screaming + Clean + Hexagonal)
                                           React/MUI frontend
                                           PostgreSQL
```

Decision context:

- [ADR-0007 — Rebuild as a Full-Stack Web Application](docs/adr/0007-rebuild-as-full-stack-web-application.md)
- [ADR-0008 — Polyglot Monorepo](docs/adr/0008-polyglot-monorepo.md)

## Web rebuild — three-pattern backend

The backend at `web/backend/src/weighttogo/` combines three patterns. Each
pattern owns a distinct concern; together they make the dependency direction
visible and enforceable.

| Pattern | Concern | Where it shows up |
| --- | --- | --- |
| **Screaming Architecture** | Folder structure that "screams" the domain | Top-level packages named after bounded contexts (`auth/`, `weight_tracking/`, `goals/`, `users/`) rather than after frameworks |
| **Clean Architecture** | Dependency rule — outer layers depend on inner | `domain/` has zero framework imports; `application/` depends on `domain/`; `infrastructure/` depends on both |
| **Hexagonal Architecture** | Ports and adapters | Domain defines a `Port` (interface); infrastructure provides an `Adapter` (concrete impl wrapping FastAPI / SQLAlchemy / Argon2) |

The dependency rule is enforced in CI by `import-linter` — domain code that
imports a framework breaks the build.

Decision context: [ADR-0012 — Three-Pattern Backend Architecture](docs/adr/0012-three-pattern-backend-architecture.md).

## Web rebuild — frontend

The frontend at `web/frontend/src/` mirrors the backend bounded contexts. Server
state is managed by TanStack Query (no ad-hoc `useEffect` fetches), forms by
React Hook Form + Zod, UI by Material UI v9, routing by React Router 6.

Decision context: [ADR-0014 — TanStack Query for Server State](docs/adr/0014-tanstack-query-for-server-state.md).

## Where to read next

- **Full architecture spec:** [SRS §4](docs/specs/WeighToGo_Web_SRS_v1.md#4-architecture) — high-level diagram, component diagrams, technology stack, pattern definitions
- **All architecture decisions:** [`docs/adr/README.md`](docs/adr/README.md)
- **Android-era architecture (historical):** [`docs/architecture/WeighToGo_Database_Architecture.md`](docs/architecture/WeighToGo_Database_Architecture.md)
