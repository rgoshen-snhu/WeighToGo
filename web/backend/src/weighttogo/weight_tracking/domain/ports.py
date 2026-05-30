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

        Soft-deleted entries are excluded — callers that need to inspect a
        deleted row (e.g. delete idempotency) must use
        ``get_by_id_including_deleted``.

        Args:
            entry_id: The surrogate primary key.
            user_id: The requesting user's ID (ownership check).

        Returns:
            The matching active entity, or ``None`` if not found, owned by
            another user, or soft-deleted.
        """
        ...

    def get_by_id_including_deleted(self, entry_id: int, user_id: int) -> WeightEntry | None:
        """Look up an entry by primary key including soft-deleted rows.

        Exists to support the idempotent re-delete path in ``DeleteWeightEntry``,
        which must distinguish "already deleted" from "never existed".  All
        other read paths must use ``get_by_id``.

        Args:
            entry_id: The surrogate primary key.
            user_id: The requesting user's ID (ownership check).

        Returns:
            The matching entity (active or soft-deleted), or ``None`` if not
            found or owned by another user.
        """
        ...

    def list_for_user(
        self,
        user_id: int,
        limit: int,
        before: tuple[date, int] | None,
    ) -> list[WeightEntry]:
        """Return a page of active weight entries for *user_id*.

        Results are ordered ``(observation_date DESC, entry_id DESC)``. The
        page contains at most *limit* items strictly less than *before*
        under the same lexicographic ordering — i.e. when ``before`` is
        ``(d, i)``, the filter is
        ``(observation_date, entry_id) < (d, i)``. Encoding the full sort
        key in the cursor avoids the skip-and-repeat defects that arise
        when the cursor key is narrower than the sort key (ADR-0015).

        Args:
            user_id: The owning user's ID.
            limit: Maximum number of entries to return.
            before: Exclusive upper bound on the ``(observation_date,
                entry_id)`` compound sort key, or ``None`` for the first
                page.

        Returns:
            A list of active ``WeightEntry`` entities, newest first.
        """
        ...

    def list_for_user_in_range(
        self,
        user_id: int,
        start: date,
        end: date,
    ) -> list[WeightEntry]:
        """Return active entries with ``start <= observation_date <= end``.

        Results are ordered ``(observation_date ASC, entry_id ASC)`` — oldest
        first — which is the order the trend chart and the rate-of-change
        windows consume.  Backs the trend read paths (FR-D-2, FR-D-3) and uses
        the ``(user_id, observation_date)`` composite index (ADR-0021).

        Args:
            user_id: The owning user's ID.
            start: Inclusive lower bound on ``observation_date``.
            end: Inclusive upper bound on ``observation_date``.

        Returns:
            A list of active ``WeightEntry`` entities, oldest first.
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

    def list_observation_dates(self, user_id: int) -> set[date]:
        """Return the set of distinct active observation dates for *user_id*.

        Duplicate same-day entries collapse to one date via set semantics; this
        feeds streak detection (FR-Ach-3). Soft-deleted entries are excluded.

        Args:
            user_id: The owning user's ID.

        Returns:
            A set of distinct ``date`` values for non-deleted entries.
        """
        ...
