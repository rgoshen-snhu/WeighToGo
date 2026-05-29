"""Add direction-invariant CHECK constraint to goals table.

Revision ID: 0004
Revises: 0003
Create Date: 2026-05-29

Adds a cross-column CHECK that enforces the goal direction invariant at the
database level:

  - LOSE goals: target_value < start_value
  - GAIN goals: target_value > start_value

The application layer (validate_target_direction in goals.domain.validation)
and the Pydantic model_validator in GoalCreateRequest already enforce this rule.
This constraint is a final safety net — it prevents a direct DB insert or a
future use-case bypass from silently persisting a goal where progress would be
permanently stuck at 0%.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: str = "0003"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    """Add direction-invariant CHECK constraint to the goals table."""
    op.create_check_constraint(
        "goals_direction_invariant",
        "goals",
        sa.text(
            "(goal_type = 'lose' AND target_value < start_value)"
            " OR (goal_type = 'gain' AND target_value > start_value)"
        ),
    )


def downgrade() -> None:
    """Remove direction-invariant CHECK constraint from the goals table."""
    op.drop_constraint("goals_direction_invariant", "goals", type_="check")
