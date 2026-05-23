"""Repository port interfaces for the weight_tracking bounded context.

Ports are defined in the domain layer. Infrastructure adapters implement them.
Use cases depend only on these abstractions — never on SQLAlchemy or any
persistence detail (SRS §4.2.3, ADR-0012).
"""

from __future__ import annotations

from datetime import date
from typing import Protocol, runtime_checkable

from weighttogo.weight_tracking.domain.entities import WeightEntry


@runtime_checkable
class IWeightEntryRepository(Protocol):
    """Read/write port for the ``weight_entries`` table."""

    def save(self, entry: WeightEntry) -> WeightEntry:
        """Persist *entry* and return it with ``entry_id`` populated.

        Performs an INSERT for new entities (``entry_id`` is ``None``) or an
        UPDATE for existing ones.

        Args:
            entry: The entity to persist.

        Returns:
            The same entity with the database-assigned ``entry_id``.
        """
        ...

    def get_by_id(self, entry_id: int, user_id: int) -> WeightEntry | None:
        """Look up an active entry by primary key, scoped to *user_id*.

        Args:
            entry_id: The surrogate primary key.
            user_id: The requesting user's ID (ownership check).

        Returns:
            The matching entity, or ``None`` if not found or owned by another user.
        """
        ...

    def list_for_user(self, user_id: int, limit: int, before_id: int | None) -> list[WeightEntry]:
        """Return a page of active weight entries for *user_id*.

        Results are ordered ``(observation_date DESC, entry_id DESC)``.  The
        page contains at most *limit* items starting after *before_id* (when
        provided).

        Args:
            user_id: The owning user's ID.
            limit: Maximum number of entries to return.
            before_id: Exclusive upper bound on entry_id for pagination.

        Returns:
            A list of active ``WeightEntry`` entities, newest first.
        """
        ...

    def count_for_user(self, user_id: int) -> int:
        """Return the count of active (non-deleted) entries for *user_id*.

        Args:
            user_id: The owning user's ID.

        Returns:
            Integer count of non-deleted weight entries.
        """
        ...

    def get_latest_for_user(self, user_id: int) -> WeightEntry | None:
        """Return the most recent active entry for *user_id* by observation_date.

        Args:
            user_id: The owning user's ID.

        Returns:
            The most recent active ``WeightEntry``, or ``None`` if none exist.
        """
        ...

    def exists_for_user_on_date(
        self,
        user_id: int,
        observation_date: date,
        exclude_entry_id: int | None = None,
    ) -> bool:
        """Check whether a non-deleted entry exists for *(user_id, observation_date)*.

        Used by create/update use cases to detect duplicate-date conflicts before
        attempting the write.

        Args:
            user_id: The owning user's ID.
            observation_date: The date to check.
            exclude_entry_id: When provided, this entry is excluded from the
                check (used by UpdateWeightEntry to allow same-date updates).

        Returns:
            ``True`` when a conflicting non-deleted entry exists.
        """
        ...
