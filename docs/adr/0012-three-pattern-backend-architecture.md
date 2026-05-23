# ADR-0012: Three-Pattern Backend Architecture (Screaming + Clean + Hexagonal)

- **Date**: 2026-05-22
- **Status**: Accepted

## Context

When designing the web backend's module structure the team had to choose an
architectural style that satisfied three constraints simultaneously:

1. **Legibility.** A new engineer reading the file tree should understand what
   the application *does* before understanding what framework it uses.
2. **Framework independence at the core.** Domain and application logic must
   not import FastAPI, SQLAlchemy, or any other infrastructure framework.
   Swapping the web framework or the ORM must require changes only in the
   outermost layer.
3. **Testability.** The domain and application layers must be testable without
   a running database, a live HTTP server, or any I/O.

No single canonical pattern addresses all three equally. The team evaluated
three complementary patterns and chose to combine them.

## Decision

The backend uses a deliberate combination of three architectural patterns:

**Screaming Architecture** (folder organisation):
Top-level packages reflect business domains, not technical roles. The file tree
reads `auth/`, `weight_tracking/`, `goals/`, `notifications/`, `preferences/`
— not `controllers/`, `services/`, `models/`.

**Clean Architecture** (dependency rule):
Within each domain folder, dependencies flow inward only:

```
interface/ → infrastructure/ → application/ → domain/
```

The `domain/` layer contains entities, value objects, domain exceptions, and
repository port interfaces. It has no knowledge of any framework. The
`application/` layer contains use cases that depend on port interfaces, never
on concrete adapters. The `infrastructure/` layer provides SQLAlchemy
repositories, bcrypt adapters, JWT adapters. The `interface/` layer contains
FastAPI routers.

**Hexagonal Architecture** (ports and adapters):
The domain defines ports (Python Protocol classes) for every external dependency
it needs. Infrastructure provides adapters that implement those protocols.
Swapping PostgreSQL for another database, or FastAPI for another framework,
requires changes only in `infrastructure/` and `interface/` respectively.

The dependency rule is enforced at CI time by `import-linter` contracts in
`pyproject.toml`. A green CI build guarantees no layer inversion exists.

## Rationale

- **Screaming Architecture alone** solves legibility but says nothing about
  coupling. Without a dependency rule, a domain module can freely import
  SQLAlchemy and the folder names become decorative.
- **Clean Architecture alone** enforces coupling but does not prescribe folder
  organisation. The canonical `layers/` folder structure places technical roles
  at the top, which hides the domain and makes the codebase harder to navigate
  for anyone unfamiliar with the project.
- **Hexagonal Architecture alone** provides the ports-and-adapters mechanism but
  is silent on both folder organisation and the specific layering rule between
  application and domain.

The three patterns are complementary: Screaming Architecture organises by domain,
Clean Architecture enforces the dependency rule, and Hexagonal Architecture
provides the port/adapter vocabulary for describing how the core connects to the
outside world. Together they satisfy all three constraints.

`import-linter` makes the dependency rule machine-verifiable rather than
aspirational. A PR that accidentally imports SQLAlchemy in the domain layer will
fail CI rather than quietly violating the architecture.

## Alternatives Considered

- **Layered MVC (controllers / services / repositories)** — The most common
  pattern in tutorial material. Rejected because it puts technical roles at the
  top of the folder tree (hides the domain) and does not prevent domain code
  from importing framework code without additional linting.
- **Feature-Sliced Design** — Organises by feature slice rather than domain
  layer. Better suited to very large frontend codebases; at the backend scale of
  this project it adds indirection without benefit.
- **Clean Architecture without Hexagonal ports** — Enforces layering but
  couples the application layer to concrete infrastructure classes through direct
  type references. Rejected because it makes unit-testing use cases harder —
  tests must construct real infrastructure objects or reach for complex mocking.
- **Modular monolith with shared ORM models** — Simpler to start but makes it
  difficult to test application logic in isolation and easy for cross-domain
  coupling to accumulate through shared model imports.

## Consequences

- **Positive**: Domain and application logic is testable with in-memory stubs,
  no database required. The dependency rule is enforced by tooling, not
  convention. A new engineer reading the file tree immediately understands the
  business domains. Swapping infrastructure adapters is localised.
- **Negative**: More boilerplate than a simple MVC structure — each domain
  requires port interfaces, separate entity and model classes, and mapping
  functions between them. The volume of files per domain is higher.
- **Follow-ups**: Each new bounded context (`notifications/`, `preferences/`)
  must be added to the `import-linter` contracts. The deferred contexts should
  have their contracts added before their implementation begins.

## References

- SRS §4.2 (architecture specification).
- Robert C. Martin, *Clean Architecture* (2017).
- Alistair Cockburn, "Hexagonal Architecture" (2005).
- Screaming Architecture: Robert C. Martin blog post, 2011.
- Implementation: `web/backend/pyproject.toml` (import-linter contracts).

## Related ADRs

- **ADR-0007** — Rebuild as Web Application: the higher-level decision that
  chose the platform on which this architecture is applied.
- **ADR-0009, ADR-0010, ADR-0011, ADR-0013** — the security decisions that are
  made possible by the framework-independent domain layer.

---

**Last Updated**: 2026-05-22
**Author**: Rick Goshen
**Approved By**: Technical Lead
