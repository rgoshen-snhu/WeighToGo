# ADR-0023: TTL-Based Server-Side Caching Strategy

- **Date**: 2026-05-29
- **Updated**: 2026-05-30 — issue #77 resolved: weight-entry update and delete
  are now invalidation triggers, and the cross-worker strategy is decided (see
  *Update (2026-05-30)* below).
- **Status**: Accepted

## Context

NFR-P-5 (SRS v2 §7.2) calls for computed values that are expensive and stable —
the recent rate-of-change and milestone counters — to be cached server-side with
a documented TTL.

The expensive read in the web rebuild is the dashboard summary. Every load of
`GET /api/v1/dashboard/summary` runs `BuildDashboardSummary.execute`, which:

- reads the user's full active weight series over the `(user_id,
  observation_date)` index,
- normalises every entry to a canonical unit,
- computes the weekly rate of change, and
- materialises the full trend series.

The `DashboardSummary` read model already carries the two values NFR-P-5 names:
`rate_of_change` (the weekly rate) and `total_entries` (the count, plus the
trend length — the "counter"-style figures). These figures are stable between
weight-entry writes: they only change when the user adds, edits, or removes an
entry.

Constraints shaping the design:

- The cache must respect the `shared` import contract
  (`pyproject.toml`): a module under `weighttogo.shared` may not import any
  bounded context (`auth`, `goals`, `weight_tracking`, `achievements`,
  `preferences`) and the inner layers may not import frameworks. The cache must
  therefore be a pure, generic, framework-free data structure.
- It must be a Milestone Three "algorithms and data structure" artifact: a small,
  fully unit-tested structure with documented time and space complexity, mirroring
  the existing `shared/units.py` pure-function pattern.
- Staleness must be bounded and documented.

## Decision

Add a generic in-memory TTL cache, `TTLCache[K, V]`, in
`weighttogo/shared/cache.py`, and use it to memoize the per-user
`DashboardSummary`.

**What is cached.** The whole `DashboardSummary` value object, keyed by the
integer `user_id`. Caching the composed summary — rather than the rate and the
counter separately — is DRY: one entry covers both NFR-P-5 named values *and*
the trend computation that dominates the cost, with one invalidation point.

**TTL value.** **30 seconds**, exposed as the named constant
`DEFAULT_TTL_SECONDS = 30.0` (no magic number). Thirty seconds bounds any stale
read to seconds — short enough that the value is genuinely "stable" within the
window — while absorbing the burst of repeated dashboard reads a single page
session produces. It is a `[SHOULD]` performance optimisation, so a small bounded
staleness is an acceptable trade for avoiding repeated full-series reads.

**Expiry data structure.** A `dict` mapping `key -> _Entry(value, expires_at)`,
where `expires_at` is a `float` deadline taken from `time.monotonic()` at write
time plus the TTL. Expiry is **lazy**: a `get` that finds an entry past its
deadline removes it (via `pop`, see below) and reports a miss. There is no
background sweeper (YAGNI). A monotonic clock is used, not wall-clock time, so
the TTL is immune to system clock adjustments. The `now` source is injectable,
which makes expiry tests deterministic without sleeping.

Lazy eviction uses `dict.pop(key, None)`, not `del`. The sync dashboard endpoint
runs in Starlette's AnyIO threadpool, so two threads can read the same expired
entry and both attempt eviction; `del` would raise `KeyError` on the loser (a
500), whereas `pop` is an idempotent no-op. This mirrors `invalidate`.

**Bounded size.** The cache is capped at `maxsize` entries
(`DEFAULT_MAX_SIZE = 1024`, one entry per active user in a worker process). An
unbounded `dict` keyed by `user_id` is a memory-DoS surface: a flood of distinct
keys grows it without limit. When a `set` would insert a *new* key into a full
cache, the cache first evicts one entry — an **expired** entry if any exists
(reclaiming it loses no useful data), otherwise the **oldest insertion** (`dict`
preserves insertion order, so the first key is the oldest). Overwriting an
existing key never grows the store and so skips eviction.

The expiry comparison uses `now >= deadline` — a magnitude comparison, never a
float-equality test. Because the deadline was derived by adding the TTL to a
reading of the same monotonic clock, the comparison is exact at the boundary.

**Complexity.** `get` and `invalidate` are O(1) average — a single `dict`
operation each. `set` is O(1) average; when the cache is at `maxsize` it evicts
first, which is O(n) worst case (n = `maxsize`) to scan for an expired entry,
otherwise O(1) to drop the oldest insertion. Space is O(`maxsize`) — growth is
bounded by the cap, so a flood of distinct keys cannot exhaust memory.

**Invalidation triggers.** A successful **weight-entry create, update, or
delete** and a successful **goal create, update, or delete (abandon)** each
invalidate the requesting user's cache key. (Update and delete were added in
issue #77; see *Update (2026-05-30)*.) The cached `DashboardSummary` embeds active-goal progress, so
goal mutations must bust it or a read in the TTL window serves a stale summary.
Detection runs at the composition root: the weight-entries and goals routers
(interface layer) call `invalidate_dashboard_cache(user_id)` after a successful
mutation. The cache object and its accessors live in the dashboard interface
layer; all three are interface-layer modules, so these cross-context interface
imports respect the import contracts (verified by the import-linter architecture
test).

## Rationale

- **Cache the composed read model, not the parts.** One entry, one TTL, one
  invalidation point covers both NFR-P-5 figures and the trend. Splitting them
  would duplicate expiry bookkeeping for no benefit (DRY, KISS).
- **Pure, generic structure in `shared`.** Keeping `TTLCache` free of any
  bounded-context or framework import preserves the Clean Architecture contract
  and makes the structure the rubric's testable data-structure showcase.
- **Lazy expiry over a sweeper thread.** A background sweeper adds concurrency
  surface and lifecycle management for a `[SHOULD]` optimisation. Lazy eviction
  reclaims memory on the next access to an expired key and is O(1) (YAGNI).

Alternatives considered:

- **Recompute on every read (no cache).** Pros: always fresh, zero staleness,
  no new code. Cons: repeats the full-series read and rate computation on every
  dashboard load, which NFR-P-5 explicitly asks to avoid. Rejected — but its
  simplicity is why the TTL is short and invalidation is explicit, so the cache
  never drifts far from a recompute.
- **External cache (Redis / Memcached).** Pros: shared across worker processes,
  survives restarts, richer eviction. Cons: a new infrastructure dependency,
  network round-trip, and operational burden disproportionate to a single
  cached read model in a course artifact; cloud/infra tooling is explicitly out
  of scope for this milestone. Rejected as premature (YAGNI). The in-process
  cache is the right size now; the `TTLCache` interface (`get`/`set`/
  `invalidate`) is small enough to swap for a Redis-backed adapter later.
- **`functools.lru_cache` / `cachetools.TTLCache`.** Pros: no hand-written
  structure. Cons: `lru_cache` has no TTL and no targeted per-key invalidation;
  pulling in `cachetools` adds a dependency for ~40 lines of code and forfeits
  the rubric's hand-rolled data-structure evidence. Rejected.

DRY/SOLID: the cache is a single generic structure reused via two thin
accessors; the dashboard read-through and the weight-router invalidation each
touch it through a named function rather than a private attribute.

## Consequences

- **Positive**: O(1) cache `get`/`invalidate` (O(n) worst-case `set` only on
  eviction from a full cache); staleness bounded to ≤ 30 s; **memory bounded to
  O(`maxsize`)**, so a key flood cannot exhaust memory; idempotent lazy eviction
  safe under the AnyIO threadpool; a pure, fully unit-tested structure with
  documented complexity; no new runtime dependency; Clean Architecture isolation
  preserved (verified by the import-linter architecture test).
- **Negative** (accepted limitation for a `[SHOULD]` stretch optimisation,
  bounded by the ≤ 30 s TTL):
  - The cache is **per worker process** — it is not shared across uvicorn
    workers, so each worker warms its own copy and a write handled by one worker
    does not invalidate another worker's copy. This is now an explicitly
    **accepted** trade-off rather than an open question; see
    *Update (2026-05-30)*.
- **Resolved follow-ups** (issue #77, 2026-05-30): weight-entry update and delete
  are now invalidation triggers, and the cross-worker strategy is decided. See
  *Update (2026-05-30)*.

## Update (2026-05-30)

Issue #77 closed the two consequences this ADR deferred from #62 (PR #74).

**1. Weight-entry update and delete now invalidate the cache.** Both the PUT and
DELETE handlers in the weight-tracking router call
`invalidate_dashboard_cache(user_id)` after a successful mutation, mirroring the
create path. Integration tests assert that each mutation busts the cache (no
≤ 30 s stale read on the same worker). This was a one-line change at each router
edge — the named `invalidate_dashboard_cache` helper was already the abstraction;
no new structure was introduced.

**2. Cross-worker strategy: accept the per-process TTL bound (no shared backend
now).** We deliberately keep the in-process `TTLCache` and accept that staleness
across uvicorn workers is bounded only by the 30 s TTL.

Rationale:

- The dashboard summary is a `[SHOULD]` display-only optimisation. A ≤ 30 s
  cross-worker staleness on counters and a weekly rate is a tolerable trade for a
  course-scope deployment; it never affects correctness of writes, only the
  freshness of a cached read.
- A shared backend (Redis/Memcached) is a new infrastructure dependency, network
  round-trip, and operational burden disproportionate to a single cached read
  model. Cloud/infra tooling is out of scope for this milestone (consistent with
  the original *Alternatives Considered* rejection of an external cache as
  premature — YAGNI).
- The `TTLCache` interface (`get`/`set`/`invalidate`) is the designed swap point:
  if multi-worker (or multi-instance) deployment becomes real and the staleness
  bound becomes unacceptable, replace the in-process structure with a shared-cache
  adapter behind the same interface, with no change to the router call sites.

**Revisit trigger.** Reopen this decision if the app is deployed with more than
one worker/instance *and* user feedback or monitoring shows the ≤ 30 s
cross-worker staleness is observable and confusing.

## Alternatives Considered

- **Recompute on read (no cache)** — simplest and always fresh, but repeats the
  expensive full-series read NFR-P-5 asks to avoid; rejected.
- **External cache (Redis/Memcached)** — shared and durable, but a
  disproportionate infrastructure dependency for one cached read model and
  out of scope for this milestone; rejected as premature.
- **`functools.lru_cache` / `cachetools`** — no TTL with targeted invalidation
  (`lru_cache`) or an added dependency for a tiny structure (`cachetools`), and
  forfeits the hand-rolled data-structure evidence; rejected.
