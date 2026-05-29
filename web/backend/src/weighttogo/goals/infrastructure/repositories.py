"""SQLAlchemy repository adapter for the goals bounded context.

This adapter implements ``IGoalRepository`` using an SQLAlchemy ORM session.
It is the only component in the goals slice that may import SQLAlchemy
(enforced by the import-linter contract).
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from weighttogo.goals.domain.entities import Goal, GoalType
from weighttogo.goals.domain.exceptions import ActiveGoalAlreadyExistsError
from weighttogo.goals.infrastructure.models import GoalModel


def _goal_to_domain(row: GoalModel) -> Goal:
    """Convert a ``GoalModel`` ORM row to a domain ``Goal`` entity.

    Args:
        row: A fully-loaded ``GoalModel`` ORM instance.

    Returns:
        The equivalent domain entity.
    """
    return Goal(
        goal_id=row.goal_id,
        user_id=row.user_id,
        target_value=Decimal(str(row.target_value)),
        target_unit=row.target_unit,
        start_value=Decimal(str(row.start_value)),
        goal_type=GoalType(row.goal_type),
        target_date=row.target_date,
        is_active=row.is_active,
        is_achieved=row.is_achieved,
        achieved_at=row.achieved_at,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


class SqlAlchemyGoalRepository:
    """SQLAlchemy implementation of ``IGoalRepository``.

    Args:
        session: An active SQLAlchemy ``Session``.
    """

    def __init__(self, session: Session) -> None:
        """Initialise with an active SQLAlchemy session."""
        self._session = session

    def save(self, goal: Goal) -> Goal:
        """Persist *goal* and return it with ``goal_id`` populated.

        Args:
            goal: The domain entity to persist.

        Returns:
            The same entity with the database-assigned ``goal_id``.

        Raises:
            ActiveGoalAlreadyExistsError: When the unique partial index is
                violated — a second active goal for the same user (race
                condition backstop).
        """
        try:
            if goal.goal_id is None:
                row = GoalModel(
                    user_id=goal.user_id,
                    target_value=goal.target_value,
                    target_unit=goal.target_unit,
                    start_value=goal.start_value,
                    goal_type=goal.goal_type,
                    target_date=goal.target_date,
                    is_active=goal.is_active,
                    is_achieved=goal.is_achieved,
                    achieved_at=goal.achieved_at,
                    created_at=goal.created_at,
                    updated_at=goal.updated_at,
                )
                self._session.add(row)
                self._session.flush()
            else:
                row_or_none = self._session.get(GoalModel, goal.goal_id)
                if row_or_none is None:
                    raise ValueError(f"Goal {goal.goal_id} not found in database.")
                row = row_or_none
                # Mutable fields only — start_value, goal_type, and target_unit
                # are immutable once set (FR-G-3) and intentionally excluded.
                row.target_value = goal.target_value
                row.target_date = goal.target_date
                row.is_active = goal.is_active
                row.is_achieved = goal.is_achieved
                row.achieved_at = goal.achieved_at
                row.updated_at = datetime.now(UTC)
                self._session.flush()
        except IntegrityError as exc:
            self._session.rollback()
            raise ActiveGoalAlreadyExistsError() from exc

        return _goal_to_domain(row)

    def get_by_id(self, goal_id: int, user_id: int) -> Goal | None:
        """Look up a goal by primary key, scoped to *user_id*.

        Args:
            goal_id: The surrogate primary key.
            user_id: The requesting user's ID.

        Returns:
            The matching domain entity, or ``None`` if not found or owned by
            another user.
        """
        row = self._session.query(GoalModel).filter_by(goal_id=goal_id, user_id=user_id).first()
        return _goal_to_domain(row) if row else None

    def get_active_for_user(self, user_id: int) -> Goal | None:
        """Return the currently active goal for *user_id*, if any.

        Args:
            user_id: The owning user's ID.

        Returns:
            The active ``Goal``, or ``None`` if no active goal exists.
        """
        row = self._session.query(GoalModel).filter_by(user_id=user_id, is_active=True).first()
        return _goal_to_domain(row) if row else None

    def list_for_user(self, user_id: int, *, limit: int) -> list[Goal]:
        """Return the most recent goals (active and historical) for *user_id*.

        Results are ordered by ``created_at DESC``.

        Args:
            user_id: The owning user's ID.
            limit: Maximum number of goals to materialise.

        Returns:
            At most *limit* ``Goal`` entities for the user, newest first.
        """
        rows = (
            self._session.query(GoalModel)
            .filter_by(user_id=user_id)
            .order_by(GoalModel.created_at.desc())
            .limit(limit)
            .all()
        )
        return [_goal_to_domain(r) for r in rows]
