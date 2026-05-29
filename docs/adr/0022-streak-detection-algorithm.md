# ADR-0022: Streak Detection Algorithm

- **Date**: 2026-05-29
- **Status**: Accepted

## Context

FR-Ach-3 (SRS v2 §6.4) requires the system to detect logging streaks at 7 and 30
consecutive days and record them as achievements. The detection runs when a user
creates a weight entry, the same composition point that already drives milestone
and goal-reached detection.

Several constraints shape the design:

- A user logs at most one weight entry per calendar day, but the detector must
  still treat its input as a set of calendar days so that any duplicate or
  same-day data collapses to a single day.
- Achievements must be recorded **once** per threshold per goal. The achievements
  table already enforces idempotency for non-null thresholds via the partial
  unique index `idx_achievements_unique_milestone`
  (`UNIQUE(goal_id, achievement_type, threshold) WHERE threshold IS NOT NULL`,
  migration 0005).
- The algorithm is a Milestone Three rubric centerpiece, so it must be written
  as a pure domain function with zero framework imports and full unit-test
  coverage, mirroring the existing `detect_milestones` pattern.

## Decision

Implement a pure domain function in the achievements bounded context:

```
detect_streaks(observation_dates: set[date], today: date) -> list[Streak]
```

**Algorithm.** Build a sorted list from the set-backed observation dates, then
perform a single linear scan tracking the length of the current run of
consecutive calendar days: increment the run when the next date equals the
previous date plus one day, otherwise reset the run to one. Track the longest
run seen. Emit each streak threshold (7, then 30) whose longest run length is at
least the threshold.

Because the input is a `set`, duplicate same-day observations collapse to a
single calendar day automatically — set construction is O(1) per insert and
guarantees distinct days before the scan ever runs.

**Recording.** Streak achievements are stored with `achievement_type='streak'`
and `threshold = Decimal(7)` or `Decimal(30)`. This reuses the existing partial
unique index `idx_achievements_unique_milestone` (threshold is non-null) for
idempotency at the database level — **no new index is required**. The
application layer also reads `get_recorded_streak_thresholds(goal_id)` to skip
already-earned thresholds before writing, and the weight-entry router runs the
inserts inside a `SAVEPOINT` so a duplicate-constraint `IntegrityError` is an
idempotent no-op rather than an error.

`Decimal(7)` and `Decimal(30)` fit the existing `threshold Numeric(precision=6,
scale=2)` column without loss; the integer-to-`Decimal` conversion is exact and
introduces no rounding.

**End-anchoring.** The detector reports the **longest consecutive run anywhere
in the history**, not only a run ending today. Once a 7-day streak is achieved it
is permanently earned; anchoring detection to the current day would cause an
earned badge to disappear after a single missed day, contradicting the
"recorded once" requirement. The `today` parameter is retained (per the
FR-Ach-3 signature) and used defensively to ignore any future-dated input. In
the normal flow future dates cannot occur — the create endpoint rejects them
with `ObservationDateInFutureError` — so the `today` filter is defense in depth.

## Rationale

- **Set-backed input** gives O(1) duplicate-day collapse and is the
  data-structure exemplar for the rubric.
- **Sort + linear scan** is the simplest correct approach. The sort dominates at
  O(n log n); the scan is O(n); space is O(n) for the sorted list and output.
  For realistic logging cadence n is small, so the recompute-per-write cost is
  negligible.

Alternatives considered:

- **Bitset over a date range** — pros: O(1) per-day membership, O(range) scan.
  Cons: the date range between a user's first and last entries is unbounded and
  potentially sparse, wasting space; rejected as premature optimization (YAGNI).
- **SQL window functions (recompute in the database)** — pros: avoids loading
  dates into Python. Cons: pushes the algorithm into the infrastructure layer,
  loses the pure-domain TDD showcase the milestone the rubric rewards, and
  couples detection to a specific SQL dialect; rejected.
- **Anchoring to a current run ending today** — rejected for the
  badge-disappearance problem described above.

DRY/SOLID: the function lives beside `detect_milestones` in the domain layer,
is wired through the existing `DetectAchievements` use case rather than a
parallel orchestration, and reuses the existing idempotency index.

## Consequences

- **Positive**: Pure, fully unit-testable, fast (O(n log n)), reuses the existing
  unique index and orchestration, preserves Clean Architecture isolation
  (verified by the import-linter architecture test).
- **Negative**: Recomputes the longest run on every weight-entry write. This is
  O(n log n) where n is the user's distinct logging days — acceptable at
  realistic scale.
- **Follow-ups**: ADR-0023 (TTL-based server-side caching) may memoize streak
  results if n grows large enough to matter.

## Alternatives Considered

- **Bitset over date range** — O(1) membership but unbounded/sparse space; rejected.
- **SQL window-function recompute** — breaks domain purity and dialect-couples; rejected.
- **Current-run-only anchoring** — would revoke earned badges; rejected.
