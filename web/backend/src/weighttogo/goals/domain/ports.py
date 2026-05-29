"""Repository port interfaces for the goals bounded context.

Ports are defined in the domain layer. Infrastructure adapters implement them.
Use cases depend only on these abstractions — never on SQLAlchemy or any
persistence detail (SRS §4.2.3, ADR-0012).
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from weighttogo.goals.domain.entities import Goal


@runtime_checkable
class IGoalRepository(Protocol):
    """Read/write port for the ``goals`` table."""

    def save(self, goal: Goal) -> Goal:
        """Persist *goal* and return it with ``goal_id`` populated.

        Performs an INSERT for new entities (``goal_id`` is ``None``) or an
        UPDATE for existing ones.

        Args:
            goal: The entity to persist.

        Returns:
            The same entity with the database-assigned ``goal_id``.
        """
        ...

    def get_by_id(self, goal_id: int, user_id: int) -> Goal | None:
        """Look up a goal by primary key, scoped to *user_id*.

        Args:
            goal_id: The surrogate primary key.
            user_id: The requesting user's ID (ownership check).

        Returns:
            The matching goal, or ``None`` if not found or owned by another user.
        """
        ...

    def get_active_for_user(self, user_id: int) -> Goal | None:
        """Return the currently active goal for *user_id*, if any.

        Args:
            user_id: The owning user's ID.

        Returns:
            The active ``Goal``, or ``None`` if no active goal exists.
        """
        ...

    def list_for_user(self, user_id: int, *, limit: int) -> list[Goal]:
        """Return the most recent goals (active and historical) for *user_id*.

        Results are ordered by ``created_at DESC``.  The *limit* cap prevents
        unbounded DB reads on accounts that have created and abandoned many goals.

        Args:
            user_id: The owning user's ID.
            limit: Maximum number of goals to return (caller-supplied, 1 – 100).

        Returns:
            At most *limit* ``Goal`` entities for the user, newest first.
        """
        ...
