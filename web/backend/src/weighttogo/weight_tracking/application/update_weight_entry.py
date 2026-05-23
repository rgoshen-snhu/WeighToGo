"""UpdateWeightEntry use case (FR-W-3)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import Decimal

from weighttogo.weight_tracking.domain.entities import WeightEntry
from weighttogo.weight_tracking.domain.exceptions import (
    DuplicateObservationDateError,
    ObservationDateInFutureError,
    WeightEntryNotFoundError,
)
from weighttogo.weight_tracking.domain.ports import IWeightEntryRepository


@dataclass(frozen=True)
class UpdateWeightEntryCommand:
    """Input for the UpdateWeightEntry use case."""

    user_id: int
    entry_id: int
    weight_value: Decimal
    weight_unit: str
    observation_date: date
    notes: str | None


class UpdateWeightEntry:
    """Update an existing weight entry owned by the requesting user.

    Args:
        weight_repo: The weight entry repository port.
    """

    def __init__(self, weight_repo: IWeightEntryRepository) -> None:
        """Initialise with the weight entry repository port."""
        self._repo = weight_repo

    def execute(self, command: UpdateWeightEntryCommand) -> WeightEntry:
        """Execute the use case.

        Args:
            command: The update command with the new field values.

        Returns:
            The updated and persisted ``WeightEntry``.

        Raises:
            WeightEntryNotFoundError: When the entry does not exist or belongs
                to a different user.
            ObservationDateInFutureError: When ``observation_date`` is after today.
            DuplicateObservationDateError: When changing the date would conflict
                with another active entry.
        """
        entry = self._repo.get_by_id(entry_id=command.entry_id, user_id=command.user_id)
        if entry is None:
            raise WeightEntryNotFoundError()

        if command.observation_date > date.today():
            raise ObservationDateInFutureError()

        if self._repo.exists_for_user_on_date(
            command.user_id,
            command.observation_date,
            exclude_entry_id=command.entry_id,
        ):
            raise DuplicateObservationDateError()

        entry.weight_value = command.weight_value
        entry.weight_unit = command.weight_unit
        entry.observation_date = command.observation_date
        entry.notes = command.notes
        entry.updated_at = datetime.now(UTC)

        return self._repo.save(entry)
