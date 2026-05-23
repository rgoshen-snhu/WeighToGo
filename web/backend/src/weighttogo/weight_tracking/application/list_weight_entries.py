"""ListWeightEntries use case (FR-W-2)."""

from __future__ import annotations

from dataclasses import dataclass

from weighttogo.weight_tracking.domain.entities import WeightEntry
from weighttogo.weight_tracking.domain.ports import IWeightEntryRepository


@dataclass(frozen=True)
class ListWeightEntriesCommand:
    """Input for the ListWeightEntries use case."""

    user_id: int
    limit: int
    cursor: int | None


@dataclass(frozen=True)
class WeightEntryPage:
    """Output envelope for a paginated list of weight entries.

    ``next_cursor`` is the ``entry_id`` of the first entry on the next page,
    or ``None`` when no further pages exist.  The M3 cursor encoding will
    replace the raw ID with an opaque string without breaking this shape.
    """

    items: list[WeightEntry]
    next_cursor: int | None


class ListWeightEntries:
    """Return a paginated page of active weight entries for a user.

    Args:
        weight_repo: The weight entry repository port.
    """

    def __init__(self, weight_repo: IWeightEntryRepository) -> None:
        """Initialise with the weight entry repository port."""
        self._repo = weight_repo

    def execute(self, command: ListWeightEntriesCommand) -> WeightEntryPage:
        """Execute the use case.

        Fetches ``limit + 1`` rows from the repository to determine whether a
        next page exists, then trims the result to *limit* entries.

        Args:
            command: The list command with pagination parameters.

        Returns:
            A ``WeightEntryPage`` with ``items`` and ``next_cursor``.
        """
        rows = self._repo.list_for_user(
            user_id=command.user_id,
            limit=command.limit + 1,
            before_id=command.cursor,
        )

        if len(rows) > command.limit:
            items = rows[: command.limit]
            # next_cursor is the entry_id of the first entry on the next page
            next_cursor = rows[command.limit].entry_id
        else:
            items = rows
            next_cursor = None

        return WeightEntryPage(items=items, next_cursor=next_cursor)
