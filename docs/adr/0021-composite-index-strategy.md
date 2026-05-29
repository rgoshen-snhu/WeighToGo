# ADR-0021: Composite Index Strategy for Weight-History Reads

- **Date**: 2026-05-29
- **Status**: Accepted

## Context

NFR-P-3 mandates indexed weight-history reads with zero full table scans over 100 rows. The SRS names two composite indexes that must back these read paths: `(user_id, observation_date)` and `(user_id, created_at)`, both scoped `WHERE is_deleted = FALSE` to exclude soft-deleted tombstones.

Migration `0002` already creates two partial indexes on `(user_id, observation_date) WHERE is_deleted = FALSE` — a UNIQUE partial index (enforcing one entry per user per date) and a non-unique DESC partial index (backing ordered list/latest/history reads). These are confirmed in place and satisfy the `observation_date` requirement completely.

No current query path orders by `created_at`. However, the forthcoming rate-of-change path (GitHub issue #59) will require insertion-order access, and NFR-P-3 is a core `[MUST]` requirement that cannot be deferred to depend on a stretch feature landing.

The `created_at` index is therefore provisioned now to satisfy NFR-P-3 unconditionally, not reactively. Per project convention, indexes live in migrations; the ORM model (`WeightEntryModel`) does not declare indexes in its `__table_args__`.

## Decision

Add exactly one new index — `idx_weight_entries_user_created_at` on `(user_id, created_at) WHERE is_deleted = FALSE` — in migration `0007_performance_indexes`. Do not create any additional `observation_date` index; the two already created in migration `0002` are sufficient.

The partial predicate `WHERE is_deleted = FALSE` is emitted via `postgresql_where` (PostgreSQL production path). Under SQLite (integration-test path) the `WHERE` clause is not supported natively and the index degrades to a full index over all rows — which is wider than needed but functionally correct. NFR-P-3 compliance is therefore verified against PostgreSQL (Task 6 integration tests), not SQLite.

Index name follows the existing convention: `idx_<table>_<columns>`.

## Rationale

**Why a partial index?** Soft deletes leave tombstone rows in the table. A full index over all rows indexes tombstones that no live query ever seeks. A partial index scoped to `is_deleted = FALSE` restricts the B-tree to live rows, matching the `WHERE is_deleted = FALSE` predicate emitted by every active read query. The smaller index fits in fewer pages, reduces write amplification, and the planner can use it without a residual filter step.

**Why provision `created_at` now?** NFR-P-3 is a `[MUST]` with no conditionality on stretch features. The rate-of-change path (#59) is planned stretch work. Gating a `[MUST]` NFR on a deferred feature landing is a delivery risk. Provisioning the index in this migration (a) satisfies the NFR on merge, (b) costs one small B-tree maintained on writes, and (c) is immediately available to the rate-of-change path when #59 lands without a follow-up migration.

**Why not duplicate the `observation_date` indexes?** They already exist in migration `0002`. Duplicating them would create redundant index pages, double the write overhead for those columns, and confuse future readers about which migration owns which index. The correct posture is to document their presence and confirm they satisfy the requirement.

**Complexity:**

- Seek cost: O(log m) B-tree descent to the first matching row (m = live row count).
- Range scan: O(k) sequential page reads for k returned rows.
- Write cost: O(log m) per insert or update that touches `user_id`, `created_at`, or `is_deleted`.
- Space: O(m) over m live rows (tombstones excluded by the partial predicate).

Trade-off versus no index: a sequential scan over the full table is O(n) per read (n = all rows including deleted) plus O(n log n) for an in-DB sort if ordered output is needed. At 100+ rows the indexed path is materially faster, satisfying the NFR.

**Side-effect note:** `GetActiveGoalWithProgress` is reused in the dashboard summary, which inherits the goal's mark-achieved write on progress check. This is consistent with the existing `GET /goals/active` behavior and is accepted without a separate ADR.

## Consequences

- **Positive**: NFR-P-3 is satisfied unconditionally on merge; the `created_at` index is ready for the rate-of-change path (#59) when it lands; write queries remain simple (no index hints needed); index naming is consistent with existing convention.
- **Negative**: One additional B-tree is maintained on every insert and update to `weight_entries`. At expected data volumes this overhead is negligible but is not zero. Under SQLite integration tests the index is wider than the partial index would be on PostgreSQL.
- **Follow-ups**: Task 6 integration tests must verify the `created_at` index is used (EXPLAIN or row-count guard per NFR-P-3). When the rate-of-change path (#59) lands, confirm it routes through this index. If a `INCLUDE`-column covering index becomes warranted after measurement, a follow-up ADR should capture that decision.

## Alternatives Considered

- **Covering index with `INCLUDE` columns** — A single index with included payload columns (e.g., `weight_value`, `unit`) would avoid a table heap fetch for covered queries. Rejected: no measured read-latency problem exists yet that would justify the additional index size and write overhead. This is a YAGNI violation at this stage; a follow-up ADR can revisit after profiling.
- **Non-partial (full) index on `(user_id, created_at)`** — Would index tombstone rows that no live query seeks. Rejected: larger index footprint for the same functional outcome; the partial predicate aligns the index precisely with the query filter, which is both more efficient and more explicit about intent.
- **Defer the `created_at` index to issue #59** — The rate-of-change feature is the primary consumer of this index. However, NFR-P-3 is a `[MUST]` that cannot depend on a stretch feature landing. Deferring the index defers NFR compliance and creates a follow-up migration that could be missed. Rejected in favor of provisioning now.
