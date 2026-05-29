# ADR-0020: Preferences Storage Data Structure

- **Date**: 2026-05-29
- **Status**: Accepted

## Context

Issue #55 (Phase 3 — User Preferences) introduces user preferences: a global weight-unit
preference (`lbs` | `kg`) and three notification toggles (achievement, milestone, streak).
The system must persist these per user, read them as a complete set on every authenticated
request, and write one key at a time (idempotent toggles).

Two structural choices were evaluated: an **EAV key-value table** (matching SRS §8.2.6 and
Android ADR-0004) and a **typed columnar table** (one row per user, one column per preference).

SRS §8.2.6 sketches a `(user_id, pref_key, pref_value)` key-value table; Android ADR-0004
used the same pattern in the original SQLite DAO.

The upsert algorithm for writes is a related implementation concern resolved alongside the
storage-shape decision: atomic `INSERT … ON CONFLICT DO UPDATE` (PostgreSQL dialect,
mirrored by `sqlalchemy.dialects.postgresql.insert`) rather than the read-modify-write
catch-`IntegrityError` pattern used elsewhere in the codebase.

## Decision

**Option A — EAV key-value table.** Selected.

Schema: `(id PK, user_id FK, pref_key VARCHAR(40), pref_value VARCHAR(40), updated_at)` with
a `UNIQUE(user_id, pref_key)` constraint, a `CHECK` on `pref_key` domain, and a conditional
`CHECK` on `pref_value` (value valid relative to its key).

Upsert algorithm: `pg_insert(UserPreferenceModel).on_conflict_do_update(index_elements=["user_id","pref_key"], set_={...})` — atomic, race-free single statement, `updated_at` re-stamped on every update.

## Rationale

**Why EAV over columnar for this codebase:**

- **SRS alignment.** SRS §8.2.6 defines a key-value table. Selecting Option A avoids a
  divergence that would require a reconciliation note in Step 6.
- **Android ADR-0004 continuity.** The original Android codebase used a key-value
  `PreferenceDao`; this mirrors that pattern in the web layer and keeps the cross-platform
  mental model consistent for reviewers familiar with the Android artifact.
- **Open-ended extension path.** If future preferences (FR-P-2 theme, additional toggles)
  are added, no schema migration is needed — only a new `pref_key` value and updated
  `CHECK` constraints.
- **Milestone algorithm artifact.** The conditional CHECK (`pref_key = 'weight_unit' AND
  pref_value IN ('lbs','kg') OR pref_key LIKE 'notify_%' AND pref_value IN ('true','false')`)
  demonstrates a non-trivial DB constraint design — an intentional data-structures artifact
  for CS 499 Milestone 3.

**Why the `ON CONFLICT DO UPDATE` upsert:**

Setting a preference is idempotent and can be high-churn (every toggle press). A single
atomic `INSERT … ON CONFLICT DO UPDATE` eliminates any read-modify-write window, is one
network round-trip, and is self-describing for the "set this preference to this value"
semantics. This is the first upsert in the codebase, introduced deliberately on the
Algorithms and Data Structures milestone.

DRY/SOLID: the `(user_id, pref_key)` unique index is the single source of uniqueness
enforcement; the `UNIQUE` constraint in the migration and the `index_elements` in the
repository are the only two places it is referenced.

## Consequences

- **Positive**:
  - Matches SRS §8.2.6 verbatim; no reconciliation needed in Step 6.
  - Cross-platform continuity with Android ADR-0004.
  - Adding future preferences requires no migration.
  - Single atomic upsert; no race window.
  - Demonstrable data-structure and algorithm choices for the milestone.

- **Negative**:
  - All values are stored as `VARCHAR` strings; `notify_*` booleans require string↔bool
    marshalling in the application layer and mapper.
  - Reading all preferences returns N rows that must be pivoted into an object (vs. a
    single typed row under the columnar option).
  - The conditional `CHECK` constraint is more complex than per-column defaults under
    Option B.

- **Follow-ups**:
  - Step 6 (SRS drift reconciliation): migration numbering in SRS §8.3 is stale by one
    (`0005` → actually `0006`); reconcile in the Step 6 documentation pass.
  - FR-W-6 (lbs↔kg value conversion) lands in Step 5; the `Numeric(6,2)` precision and
    float-equality safety concerns flagged in the design spec §13 become live at that point.

## Alternatives Considered

- **Option B — Typed columnar** (`user_id` PK, `weight_unit VARCHAR(3)`, `notify_* BOOLEAN`,
  per-column `server_default`, single-line `CHECK`).
  - Pros: real types; no string↔bool dance; single-row read with no pivot; self-validating
    schema; simpler CHECK.
  - Cons: adding a 5th preference needs a migration; deviates from SRS §8.2.6 literal (would
    require a Step 6 reconciliation note); deviates from Android ADR-0004 EAV pattern.
  - **Not selected** because SRS alignment and Android ADR-0004 continuity were weighted
    higher, and the string-marshalling cost is bounded (four fixed keys, handled once in the
    mapper).
