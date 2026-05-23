# ADR 0007: Rebuild Weigh to Go! as a Full-Stack Web Application

## Status
Accepted

## Context

Weigh to Go! began as a native Android application written in Java. A structured
engineering code review of that codebase surfaced technical debt that is
architectural rather than incidental:

- Activity classes carrying too many responsibilities (single-responsibility
  violations) and model-view-controller drift.
- Database writes executed on the UI thread, plus an `ExecutorService` lifecycle
  defect.
- Personally identifiable information written to logs without masking.
- Username enumeration made possible by distinguishable exception messages.
- A hardcoded `if`/`else-if` navigation chain in place of a declarative routing
  model.
- Accessibility gaps in the user interface.

These findings are about how the system is *structured*, not about isolated
bugs. The project had to decide whether to remediate the Android application in
place or rebuild the artifact on a different platform.

## Decision

Rebuild Weigh to Go! as a full-stack web application:

- A React + TypeScript single-page frontend.
- A FastAPI + Python backend exposing a documented HTTP API.
- PostgreSQL for persistence.

The original Android codebase is preserved unchanged for reference rather than
deleted (see ADR-0008). The pre-rebuild state is marked by the `v1.0.0-android`
tag.

## Rationale

### Why this approach over the alternatives

- **Separation of concerns at scale.** A web architecture splits presentation,
  application logic, and persistence across process boundaries
  (browser ↔ HTTP API ↔ database). That structure makes the layering violations
  the review found — UI-thread database access, MVC drift — difficult to
  reintroduce. A clean rebuild lets the layering be designed deliberately
  instead of retrofitted into a shipped app.
- **API-first design.** A documented HTTP API decouples clients from the
  server. A future native mobile client can consume the same API with no second
  backend — something a single-process Android app cannot offer.
- **Modern, well-supported ecosystem.** The React + FastAPI stack has mature
  tooling for static typing, testing, linting, and dependency management, which
  directly enables the strict-typing and test-driven-development discipline the
  project targets.
- **Findings addressed at design time.** The rebuild applies a security baseline
  (PII masking, generic authentication errors, hashed credentials, rate
  limiting) and an enforced architecture from the first commit, rather than
  patching a deployed application after the fact.
- **Broader, more transferable surface.** A full-stack web artifact exercises a
  wider range of engineering concerns than a single-platform mobile app.

### Alternatives considered

1. **Remediate the Android app in place.** Rejected. The review findings are
   architectural; fixing them properly would amount to a near-rewrite while
   still bound to a single-platform, single-process design. The accessibility
   and security gaps would remain retrofits rather than designed-in properties.
2. **Rebuild as a second native mobile app (Kotlin or Flutter).** Rejected.
   Retains the single-client, no-API limitation, exercises the
   separation-of-concerns goals less fully, and demonstrates a narrower surface.
3. **Web frontend over a backend-as-a-service (e.g., Firebase).** Rejected.
   Outsources exactly the backend architecture, data modeling, and security work
   that is the substance of this enhancement, and gives up control over the
   intended layered backend design.

## Consequences

### Positive

- Layered architecture can be designed deliberately and enforced.
- A security baseline is present from the first commit instead of bolted on.
- The HTTP API is reusable by future clients, including a native mobile client.
- Modern testing, linting, and type-checking tooling is available on both
  stacks.
- The artifact demonstrates a broader, more transferable set of engineering
  skills.

### Negative

- A full rebuild is more effort than targeted fixes to the Android app.
- The repository becomes polyglot, mixing toolchains (mitigated by ADR-0008).
- New infrastructure must be stood up: a database, and CI for an additional
  stack.

### Technical debt

The rebuilt web application intentionally does not reach feature parity with the
Android app within this milestone. Goal management, achievements, and
preferences ship as accessible placeholder screens and are scheduled for later
milestones. This is a deliberate, scoped deferral rather than unmanaged debt.

## References

- Project Software Requirements Specification — `docs/specs/WeighToGo_Web_SRS_v1.md`
  (§4 architecture, §6/§7 functional and non-functional requirements).
- OWASP Authentication guidance (informs the generic-error and credential
  decisions captured in ADR-0010 and ADR-0013).
- Android-era decision records — `docs/adr/0001`–`0006`.

## Related ADRs

- **ADR-0008** — Polyglot Monorepo: how the original and rebuilt artifacts
  coexist in one repository.
- **ADR-0012** — Three-Pattern Backend Architecture: how the rebuilt backend's
  layering is structured and enforced.
- **ADR-0009, ADR-0010, ADR-0011, ADR-0013** — the security-baseline decisions
  that close the authentication and PII findings from the code review.

## Future Considerations

- A native mobile client consuming the same HTTP API.
- Deployment and hosting strategy for the web application.
- Feature parity for goals, achievements, and preferences in later milestones.

---

**Last Updated**: 2026-05-21
**Author**: Rick Goshen
**Approved By**: Technical Lead
