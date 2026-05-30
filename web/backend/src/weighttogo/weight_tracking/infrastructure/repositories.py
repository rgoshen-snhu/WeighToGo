"""SQLAlchemy repository adapter for the weight_tracking bounded context.

This adapter implements ``IWeightEntryRepository`` using an SQLAlchemy ORM
session.  It is the only component in the weight_tracking slice that may
import SQLAlchemy (enforced by the import-linter contract).
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from weighttogo.weight_tracking.domain.entities import WeightEntry
from weighttogo.weight_tracking.infrastructure.models import WeightEntryModel


def _entry_to_domain(row: WeightEntryModel) -> WeightEntry:
    """Convert a ``WeightEntryModel`` ORM row to a domain ``WeightEntry`` entity.

    Args:
        row: A fully-loaded ``WeightEntryModel`` ORM instance.

    Returns:
        The equivalent domain entity.
    """
    return WeightEntry(
        entry_id=row.entry_id,
        user_id=row.user_id,
        weight_value=Decimal(str(row.weight_value)),
        weight_unit=row.weight_unit,
        observation_date=row.observation_date,
        notes=row.notes,
        created_at=row.created_at,
        updated_at=row.updated_at,
        is_deleted=row.is_deleted,
        deleted_at=row.deleted_at,
    )


class SqlAlchemyWeightEntryRepository:
    """SQLAlchemy implementation of ``IWeightEntryRepository``.

    Args:
        session: An active SQLAlchemy ``Session``.
    """

    def __init__(self, session: Session) -> None:
        """Initialise with an active SQLAlchemy session."""
        self._session = session

    def save(self, entry: WeightEntry) -> WeightEntry:
        """Persist *entry* and return it with ``entry_id`` populated.

        Performs an INSERT for new entities (``entry_id`` is ``None``) or an
        UPDATE for existing ones.

        Args:
            entry: The domain entity to persist.

        Returns:
            The same entity with the database-assigned ``entry_id``.
        """
        if entry.entry_id is None:
            row = WeightEntryModel(
                user_id=entry.user_id,
                weight_value=entry.weight_value,
                weight_unit=entry.weight_unit,
                observation_date=entry.observation_date,
                notes=entry.notes,
                created_at=entry.created_at,
                updated_at=entry.updated_at,
                is_deleted=entry.is_deleted,
                deleted_at=entry.deleted_at,
            )
            self._session.add(row)
            self._session.flush()
        else:
            row_or_none = self._session.get(WeightEntryModel, entry.entry_id)
            if row_or_none is None:
                raise ValueError(f"WeightEntry {entry.entry_id} not found in database.")
            row = row_or_none
            row.weight_value = entry.weight_value
            row.weight_unit = entry.weight_unit
            row.observation_date = entry.observation_date
            row.notes = entry.notes
            row.updated_at = entry.updated_at
            row.is_deleted = entry.is_deleted
            row.deleted_at = entry.deleted_at
            self._session.flush()

        return _entry_to_domain(row)

    def get_by_id(self, entry_id: int, user_id: int) -> WeightEntry | None:
        """Look up an active entry by primary key, scoped to *user_id*.

        Soft-deleted rows are excluded per the port contract.

        Args:
            entry_id: The surrogate primary key.
            user_id: The requesting user's ID.

        Returns:
            The matching active domain entity, or ``None`` if not found, owned
            by another user, or soft-deleted.
        """
        row = (
            self._session.query(WeightEntryModel)
            .filter_by(entry_id=entry_id, user_id=user_id, is_deleted=False)
            .first()
        )
        return _entry_to_domain(row) if row else None

    def get_by_id_including_deleted(self, entry_id: int, user_id: int) -> WeightEntry | None:
        """Look up an entry by primary key including soft-deleted rows.

        Used by ``DeleteWeightEntry`` to support idempotent re-delete.

        Args:
            entry_id: The surrogate primary key.
            user_id: The requesting user's ID.

        Returns:
            The matching domain entity (active or soft-deleted), or ``None`` if
            not found or owned by another user.
        """
        row = (
            self._session.query(WeightEntryModel)
            .filter_by(entry_id=entry_id, user_id=user_id)
            .first()
        )
        return _entry_to_domain(row) if row else None

    def list_for_user(
        self,
        user_id: int,
        limit: int,
        before: tuple[date, int] | None,
    ) -> list[WeightEntry]:
        """Return a page of active entries for *user_id* (ADR-0015).

        The filter is lexicographic on ``(observation_date, entry_id)`` to
        match the sort key — an entry_id-only filter would skip or repeat
        rows whenever date ordering disagrees with insertion ordering
        (e.g. user backfills an older date).

        Args:
            user_id: The owning user's ID.
            limit: Maximum number of entries to return.
            before: Exclusive upper bound on ``(observation_date, entry_id)``
                for cursor pagination, or ``None`` for the first page.

        Returns:
            A list of active ``WeightEntry`` entities ordered by
            ``(observation_date DESC, entry_id DESC)``.
        """
        q = (
            self._session.query(WeightEntryModel)
            .filter_by(user_id=user_id, is_deleted=False)
            .order_by(
                WeightEntryModel.observation_date.desc(),
                WeightEntryModel.entry_id.desc(),
            )
        )
        if before is not None:
            before_date, before_id = before
            # Use the explicit OR form rather than ``tuple_(...) < tuple_(...)``
            # because SQLite (used by the integration test harness) does not
            # implement row-value comparisons.
            q = q.filter(
                or_(
                    WeightEntryModel.observation_date < before_date,
                    and_(
                        WeightEntryModel.observation_date == before_date,
                        WeightEntryModel.entry_id < before_id,
                    ),
                )
            )
        rows = q.limit(limit).all()
        return [_entry_to_domain(r) for r in rows]

    def list_for_user_in_range(
        self,
        user_id: int,
        start: date,
        end: date,
    ) -> list[WeightEntry]:
        """Return active entries with ``start <= observation_date <= end``.

        Ordered oldest-first to match the trend chart and rate-of-change window
        consumers.  The ``user_id`` equality plus the ``observation_date`` range
        are served by the ``(user_id, observation_date)`` composite index
        (ADR-0021).

        Args:
            user_id: The owning user's ID.
            start: Inclusive lower bound on ``observation_date``.
            end: Inclusive upper bound on ``observation_date``.

        Returns:
            A list of active ``WeightEntry`` entities, oldest first.
        """
        rows = (
            self._session.query(WeightEntryModel)
            .filter_by(user_id=user_id, is_deleted=False)
            .filter(
                WeightEntryModel.observation_date >= start,
                WeightEntryModel.observation_date <= end,
            )
            .order_by(
                WeightEntryModel.observation_date.asc(),
                WeightEntryModel.entry_id.asc(),
            )
            .all()
        )
        return [_entry_to_domain(r) for r in rows]

    def count_for_user(self, user_id: int) -> int:
        """Return the count of active (non-deleted) entries for *user_id*.

        Args:
            user_id: The owning user's ID.

        Returns:
            Integer count.
        """
        return (
            self._session.query(WeightEntryModel)
            .filter_by(user_id=user_id, is_deleted=False)
            .count()
        )

    def list_observation_dates(self, user_id: int) -> set[date]:
        """Return the set of distinct active observation dates for *user_id*.

        Duplicate same-day entries collapse to one date via set semantics; this
        feeds the streak detector (FR-Ach-3).  Soft-deleted entries are excluded.

        Args:
            user_id: The owning user's ID.

        Returns:
            A set of distinct ``date`` values for non-deleted entries.
        """
        rows = (
            self._session.query(WeightEntryModel.observation_date)
            .filter_by(user_id=user_id, is_deleted=False)
            .all()
        )
        return {r.observation_date for r in rows}

    def get_latest_for_user(self, user_id: int) -> WeightEntry | None:
        """Return the most recent active entry for *user_id* by observation_date.

        Args:
            user_id: The owning user's ID.

        Returns:
            The most recent active ``WeightEntry``, or ``None``.
        """
        row = (
            self._session.query(WeightEntryModel)
            .filter_by(user_id=user_id, is_deleted=False)
            .order_by(
                WeightEntryModel.observation_date.desc(),
                WeightEntryModel.entry_id.desc(),
            )
            .first()
        )
        return _entry_to_domain(row) if row else None

    def exists_for_user_on_date(
        self,
        user_id: int,
        observation_date: date,
        exclude_entry_id: int | None = None,
    ) -> bool:
        """Check whether a non-deleted entry exists for *(user_id, observation_date)*.

        Args:
            user_id: The owning user's ID.
            observation_date: The date to check.
            exclude_entry_id: When provided, exclude this entry from the check.

        Returns:
            ``True`` when a conflicting non-deleted entry exists.
        """
        q = self._session.query(WeightEntryModel).filter(
            WeightEntryModel.user_id == user_id,
            WeightEntryModel.observation_date == observation_date,
            WeightEntryModel.is_deleted.is_(False),
        )
        if exclude_entry_id is not None:
            q = q.filter(WeightEntryModel.entry_id != exclude_entry_id)
        return self._session.query(q.exists()).scalar() or False
