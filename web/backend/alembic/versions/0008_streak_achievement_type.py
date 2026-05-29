"""Allow 'streak' achievement_type (FR-Ach-3).

Revision ID: 0008
Revises: 0007
Create Date: 2026-05-29

Widens the achievements_type_valid CHECK constraint to permit the new
'streak' achievement type.  Streak achievements reuse the existing partial
unique index idx_achievements_unique_milestone (UNIQUE(goal_id,
achievement_type, threshold) WHERE threshold IS NOT NULL) for idempotency —
no new index is required.

The integration-test harness builds schema via Base.metadata.create_all (the
achievements ORM model declares no CheckConstraint), so this migration only
materialises on PostgreSQL/production; SQLite test inserts are unaffected.

Uses the direct op.create_check_constraint/op.drop_constraint form to match the
only prior CHECK migration (0004_goals_direction_check) — PostgreSQL supports
ALTER TABLE ... DROP CONSTRAINT directly and migrations never run on SQLite.
"""

from __future__ import annotations

from alembic import op

revision: str = "0008"
down_revision: str = "0007"
branch_labels: str | None = None
depends_on: str | None = None

_OLD = "achievement_type IN ('goal_reached', 'milestone')"
_NEW = "achievement_type IN ('goal_reached', 'milestone', 'streak')"


def upgrade() -> None:
    """Recreate the CHECK constraint to allow 'streak'."""
    op.drop_constraint("achievements_type_valid", "achievements", type_="check")
    op.create_check_constraint("achievements_type_valid", "achievements", _NEW)


def downgrade() -> None:
    """Revert the CHECK constraint to the original two types."""
    op.drop_constraint("achievements_type_valid", "achievements", type_="check")
    op.create_check_constraint("achievements_type_valid", "achievements", _OLD)
