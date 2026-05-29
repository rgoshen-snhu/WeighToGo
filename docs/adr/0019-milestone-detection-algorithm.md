# ADR-0019: Milestone Detection Algorithm

- **Date**: 2026-05-29
- **Status**: Accepted

## Context

FR-Ach-2 requires detecting when a user crosses weight-loss/gain milestones at
5, 10, 25, and 50 lb thresholds from the goal's starting weight.  Detection
must be idempotent — each threshold fires exactly once per goal.  The algorithm
is the primary "algorithms and data structures" showcase for the CS 499 rubric.

Two architectural choices shape the design:

1. **When to run:** synchronous-on-write (each POST /weight-entries triggers
   detection) vs. event-driven (an async worker consumes a domain event).
2. **How to enforce idempotency:** in-memory guard vs. DB-only constraint.

## Decision

**Threshold-crossing scan with frozenset idempotency guard, synchronous on write.**

```
detect_milestones(goal: GoalSnapshot, current_weight: Decimal,
                  already_recorded: frozenset[Decimal]) -> list[Decimal]

Algorithm:
  delta = start_value - current_weight   (for 'lose' goals)
        = current_weight - start_value   (for 'gain' goals)
  for T in (5, 10, 25, 50):
      if delta >= T and T not in already_recorded:
          yield T
```

`already_recorded` is loaded from the database once per request as a
`frozenset` before detection runs.  A DB unique constraint (two partial
indexes — one for milestone rows, one for goal_reached rows) is the race-
condition backstop.

Detection runs synchronously inside the weight-entry POST handler at the
interface/composition-root layer.  `weight_tracking` never imports
`achievements`; the router imports both and orchestrates.

## Rationale

**Synchronous vs event-driven:** Synchronous detection lets the API response
include `newly_earned_achievements` so the frontend can show an immediate
notification without a polling round-trip.  Event-driven would require the
frontend to poll or use WebSockets — added complexity with no benefit at this
scale.  Downside: each POST that has an active goal pays one extra DB read
(`get_recorded_thresholds`).  Acceptable: k=4 thresholds, O(1) frozenset
lookup, single indexed DB read.

**frozenset guard:** Loading recorded thresholds into a `frozenset` before
calling the pure function keeps `detect_milestones` framework-free and
independently testable.  The in-memory set is the fast guard; the DB
constraint is the race-condition backstop.

**Pure function:** `detect_milestones` has no side effects and no imports from
frameworks.  This satisfies the import-linter contract that domain code never
imports infrastructure and makes the algorithm trivially unit-testable.

**Two partial unique indexes:** `NULL != NULL` in PostgreSQL and SQLite unique
indexes, so a single `UNIQUE (goal_id, achievement_type, threshold)` would
allow duplicate `goal_reached` rows (both have `threshold = NULL`).  Two
partial indexes are used:
- `idx_achievements_unique_milestone WHERE threshold IS NOT NULL`
- `idx_achievements_unique_goal_reached WHERE threshold IS NULL`

## Consequences

- **Positive:** O(k) per entry (k=4), O(1) in practice.  Pure function is
  easily unit-tested with no mocking.  Synchronous response includes
  achievements.  Idempotency defended at two layers.
- **Negative:** One extra DB read per POST when an active goal exists.
  Synchronous detection adds latency proportional to one indexed read —
  negligible at this scale.
- **Follow-ups:** ADR-0021 (streak detection algorithm) before Phase 5.

## Alternatives Considered

- **Event-driven detection** — Decoupled but prevents including achievements in
  the same HTTP response.  Requires an event bus or background worker.
  Over-engineered for current scale.  Rejected.
- **DB-only idempotency (no frozenset)** — Requires catching `IntegrityError`
  on every INSERT.  Exception-as-flow-control is harder to test.  Rejected.
