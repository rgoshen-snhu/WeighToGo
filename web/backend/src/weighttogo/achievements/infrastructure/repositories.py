"""SQLAlchemy repository adapter for the achievements bounded context.

This adapter implements ``IAchievementRepository`` using an SQLAlchemy ORM
session.  It is the only component in the achievements slice that may import
SQLAlchemy (enforced by the import-linter contract).
"""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from weighttogo.achievements.domain.entities import Achievement, AchievementType
from weighttogo.achievements.infrastructure.models import AchievementModel


def _to_domain(row: AchievementModel) -> Achievement:
    """Convert an ``AchievementModel`` ORM row to a domain ``Achievement``.

    Args:
        row: A fully-loaded ``AchievementModel`` ORM instance.

    Returns:
        The equivalent domain entity.
    """
    return Achievement(
        achievement_id=row.id,
        user_id=row.user_id,
        goal_id=row.goal_id,
        achievement_type=AchievementType(row.achievement_type),
        threshold=Decimal(str(row.threshold)) if row.threshold is not None else None,
        earned_at=row.earned_at,
    )


class SqlAlchemyAchievementRepository:
    """SQLAlchemy implementation of ``IAchievementRepository``.

    Args:
        session: An active SQLAlchemy ``Session``.
    """

    def __init__(self, session: Session) -> None:
        """Initialise with an active SQLAlchemy session."""
        self._session = session

    def save(self, achievement: Achievement) -> Achievement | None:
        """Persist *achievement*, or return ``None`` if it already exists.

        The INSERT runs in its own SAVEPOINT so a unique-index conflict (a
        concurrent duplicate of an idempotent milestone/streak row) rolls back
        only this insert — not sibling achievements earned in the same request —
        and surfaces as an idempotent no-op rather than aborting the surrounding
        transaction.

        Args:
            achievement: The domain entity to persist.

        Returns:
            The same entity with its ``achievement_id``, or ``None`` when an
            equivalent row already existed.
        """
        row = AchievementModel(
            user_id=achievement.user_id,
            goal_id=achievement.goal_id,
            achievement_type=achievement.achievement_type,
            threshold=achievement.threshold,
            earned_at=achievement.earned_at,
        )
        try:
            with self._session.begin_nested():
                self._session.add(row)
                self._session.flush()
        except IntegrityError:
            return None
        return _to_domain(row)

    def _recorded_thresholds_for(
        self, goal_id: int, achievement_type: AchievementType
    ) -> frozenset[Decimal]:
        """Return recorded thresholds for *goal_id* of the given *achievement_type*.

        Shared by the milestone and streak idempotency reads so the Decimal
        coercion and the None-filtering can never diverge between them.

        Args:
            goal_id: The goal's primary key.
            achievement_type: The achievement type to filter on.

        Returns:
            A frozenset of ``Decimal`` threshold values.  Empty when none recorded.
        """
        rows = (
            self._session.query(AchievementModel)
            .filter_by(goal_id=goal_id, achievement_type=achievement_type)
            .with_entities(AchievementModel.threshold)
            .all()
        )
        return frozenset(Decimal(str(r.threshold)) for r in rows if r.threshold is not None)

    def get_recorded_thresholds(self, goal_id: int) -> frozenset[Decimal]:
        """Return the set of milestone thresholds already recorded for *goal_id*.

        Args:
            goal_id: The goal's primary key.

        Returns:
            A frozenset of ``Decimal`` threshold values.  Empty when none recorded.
        """
        return self._recorded_thresholds_for(goal_id, AchievementType.MILESTONE)

    def get_recorded_streak_thresholds(self, goal_id: int) -> frozenset[Decimal]:
        """Return the set of streak thresholds already recorded for *goal_id*.

        Args:
            goal_id: The goal's primary key.

        Returns:
            A frozenset of ``Decimal`` streak thresholds.  Empty when none recorded.
        """
        return self._recorded_thresholds_for(goal_id, AchievementType.STREAK)

    def get_by_id(self, achievement_id: int, user_id: int) -> Achievement | None:
        """Look up by primary key, scoped to *user_id* (IDOR guard).

        Args:
            achievement_id: The surrogate primary key.
            user_id: The requesting user's ID.

        Returns:
            The matching entity, or ``None`` if not found or owned by another user.
        """
        row = (
            self._session.query(AchievementModel)
            .filter_by(id=achievement_id, user_id=user_id)
            .first()
        )
        return _to_domain(row) if row else None

    def has_goal_reached_been_recorded(self, goal_id: int) -> bool:
        """Return ``True`` when a goal_reached achievement exists for *goal_id*.

        Args:
            goal_id: The goal's primary key.

        Returns:
            ``True`` if a ``goal_reached`` row exists for this goal.
        """
        return (
            self._session.query(AchievementModel)
            .filter_by(goal_id=goal_id, achievement_type=AchievementType.GOAL_REACHED)
            .first()
        ) is not None

    def list_for_user(self, user_id: int, *, limit: int) -> list[Achievement]:
        """Return the most recent achievements for *user_id*, newest first.

        Args:
            user_id: The owning user's ID.
            limit: Maximum number of achievements to return.

        Returns:
            At most *limit* ``Achievement`` entities, ordered by ``earned_at DESC``.
        """
        rows = (
            self._session.query(AchievementModel)
            .filter_by(user_id=user_id)
            .order_by(AchievementModel.earned_at.desc())
            .limit(limit)
            .all()
        )
        return [_to_domain(r) for r in rows]
