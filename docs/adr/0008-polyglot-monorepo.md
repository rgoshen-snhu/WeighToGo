# ADR 0008: Polyglot Monorepo for the Mobile-Web Artifact

## Status
Accepted

## Context

ADR-0007 establishes that Weigh to Go! is being rebuilt as a web application
while the original Android codebase is kept for reference. That decision raises
a repository-structure question: where do the two codebases live?

Two codebases now exist for the same product — a Java/Gradle Android app and a
Python + TypeScript web app — along with documentation (the SRS, ADRs, design
records) that applies across both. The structure chosen has to keep the two
stacks from interfering with each other while keeping the relationship between
them visible.

## Decision

Keep both codebases in a single **polyglot monorepo**:

```
repository root
├── android/          Preserved Android application (Java / Gradle)
├── web/              Rebuilt web application
│   ├── frontend/     React + TypeScript
│   └── backend/      FastAPI + Python
├── docs/             Shared documentation (SRS, ADRs, design records)
└── README, CONTRIBUTING, SUMMARY, LICENSE   Repository-level docs
```

The Android project moves from the repository root into `android/`. The web
project is built under `web/`. Shared documentation stays at the root and under
`docs/`.

## Rationale

### Why this approach over the alternatives

- **The original artifact is preserved next to its successor.** The Android app
  stays buildable and inspectable in the same repository, so the mobile-to-web
  evolution reads as one continuous history rather than a discontinuity.
- **Single source of truth for project history.** One commit graph, one set of
  release tags (`v1.0.0-android` and onward), and one issue
  tracker and board span both eras of the project.
- **Shared documentation and decision records.** ADRs, the SRS, and design
  records describe the project as a whole. In one repository they are written
  and versioned once instead of being duplicated or split.
- **Atomic cross-cutting changes.** A change that touches shared documentation
  together with either stack is a single commit and a single pull request.
- **Stack independence through path-scoped tooling.** CI workflows are
  path-filtered (`android/**`, `web/**`) so each stack builds only when its own
  files change. The shared repository does not couple the two build pipelines.

### Alternatives considered

1. **Two separate repositories.** Rejected. Splitting the codebases also splits
   history and documentation; the relationship between the original and the
   rebuild becomes implicit, and any change spanning shared docs plus a stack
   has to be coordinated across repositories.
2. **Replace the Android code outright (delete it).** Rejected. This loses the
   original artifact, which is valuable as the concrete reference point that the
   rebuild's rationale (ADR-0007) is argued against.
3. **Archive the Android code in a branch or tag only.** Rejected. This makes
   the original code second-class and awkward to browse. The `v1.0.0-android`
   tag already marks that point in history; the code itself should remain on the
   main line so it stays easy to inspect.

## Consequences

### Positive

- Project history, documentation, and issue tracking are unified.
- The mobile-to-web evolution story is self-contained in one repository.
- Path-filtered CI keeps each stack's builds fast and independently scoped.

### Negative

- A polyglot repository is larger and mixes three toolchains (Java/Gradle,
  Python, Node).
- Contributors must know which subtree they are working in. Mitigated by
  stack-scoped tooling, a clear root README describing the layout, and per-stack
  contribution guidance.
- `.gitignore` must cover all three ecosystems.

### Technical debt

None structural. The `android/` subtree is in maintenance-only status: it stays
buildable and tested, but receives no new features.

## References

- Project Software Requirements Specification — `docs/specs/WeighToGo_Web_SRS_v1.md`
  (§5 restructure plan).
- ADR-0007 — Rebuild Weigh to Go! as a Full-Stack Web Application.

## Related ADRs

- **ADR-0007** — Rebuild as a Full-Stack Web Application: the decision this
  repository structure exists to support.
- **ADR-0012** — Three-Pattern Backend Architecture: the structure of the web
  backend that lives under `web/backend/`.

## Future Considerations

- If the Android artifact is eventually retired from active reference, the
  `android/` subtree could be split out to an archive repository. This is not
  currently planned.

---

**Last Updated**: 2026-05-21
**Author**: Rick Goshen
**Approved By**: Technical Lead
