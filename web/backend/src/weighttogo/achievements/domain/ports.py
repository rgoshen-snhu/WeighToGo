"""Repository port interfaces for the achievements bounded context.

Ports are defined in the domain layer.  Infrastructure adapters implement
them.  Use cases depend only on these abstractions — never on SQLAlchemy or
any persistence detail (SRS §4.2.3, ADR-0012).
"""

from __future__ import annotations

from decimal import Decimal
from typing import Protocol, runtime_checkable

from weighttogo.achievements.domain.entities import Achievement


@runtime_checkable
class IAchievementRepository(Protocol):
    """Read/write port for the ``achievements`` table."""

    def save(self, achievement: Achievement) -> Achievement | None:
        """Persist *achievement* and return it with ``achievement_id`` set.

        Returns ``None`` when the insert duplicates an existing idempotent
        achievement (the unique-index conflict is swallowed as a no-op), so a
        concurrent duplicate never rolls back achievements earned alongside it.

        Args:
            achievement: The entity to persist.

        Returns:
            The persisted entity with its ``achievement_id``, or ``None`` when
            an equivalent row already existed.
        """
        ...

    def get_recorded_thresholds(self, goal_id: int) -> frozenset[Decimal]:
        """Return the set of milestone thresholds already recorded for *goal_id*.

        Used by ``DetectAchievements`` to build the idempotency guard before
        running ``detect_milestones``.

        Args:
            goal_id: The goal's primary key.

        Returns:
            A frozenset of ``Decimal`` threshold values already persisted.
            Empty frozenset when no milestones have been recorded yet.
        """
        ...

    def get_recorded_streak_thresholds(self, goal_id: int) -> frozenset[Decimal]:
        """Return the set of streak thresholds already recorded for *goal_id*.

        Used by ``DetectAchievements`` to build the idempotency guard before
        running ``detect_streaks``.

        Args:
            goal_id: The goal's primary key.

        Returns:
            A frozenset of ``Decimal`` streak thresholds already persisted.
            Empty frozenset when no streaks have been recorded yet.
        """
        ...

    def get_by_id(self, achievement_id: int, user_id: int) -> Achievement | None:
        """Look up an achievement by primary key, scoped to *user_id*.

        Returns ``None`` when the achievement does not exist or belongs to
        another user (IDOR guard).

        Args:
            achievement_id: The surrogate primary key.
            user_id: The requesting user's ID.

        Returns:
            The matching entity, or ``None``.
        """
        ...

    def has_goal_reached_been_recorded(self, goal_id: int) -> bool:
        """Return ``True`` when a goal_reached achievement exists for *goal_id*.

        Used by ``DetectAchievements`` as the in-memory idempotency guard for
        the ``goal_reached`` achievement type, complementing the DB partial
        unique index backstop (ADR-0019).

        Args:
            goal_id: The goal's primary key.

        Returns:
            ``True`` if a ``goal_reached`` achievement row exists for this goal.
        """
        ...

    def list_for_user(self, user_id: int, *, limit: int) -> list[Achievement]:
        """Return the most recent achievements for *user_id*, newest first.

        Args:
            user_id: The owning user's ID.
            limit: Maximum number of achievements to return.

        Returns:
            At most *limit* ``Achievement`` entities, ordered by
            ``earned_at DESC``.
        """
        ...
