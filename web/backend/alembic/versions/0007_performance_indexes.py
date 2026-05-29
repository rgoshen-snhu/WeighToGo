"""Add composite/partial index for weight-history trend reads (NFR-P-3).

Revision ID: 0007
Revises: 0006
Create Date: 2026-05-29

Adds ``(user_id, created_at)`` scoped ``WHERE is_deleted = FALSE`` to satisfy
SRS §7.2 NFR-P-3. The ``(user_id, observation_date)`` requirement is already
met by migration 0002 (a UNIQUE partial index and a DESC partial index); this
migration does not duplicate them. ``postgresql_where`` emits the predicate on
PostgreSQL only; SQLite falls back to a full index. See ADR-0021.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision: str = "0007"
down_revision: str = "0006"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    """Create the (user_id, created_at) partial index for live rows."""
    op.create_index(
        "idx_weight_entries_user_created_at",
        "weight_entries",
        ["user_id", "created_at"],
        postgresql_where=sa.text("is_deleted = FALSE"),
    )
    # Non-unique: SQLite fallback to a full index is acceptable (same precedent as 0002).


def downgrade() -> None:
    """Drop the (user_id, created_at) index."""
    op.drop_index("idx_weight_entries_user_created_at", table_name="weight_entries")
