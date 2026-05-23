"""CreateWeightEntry use case (FR-W-1)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import Decimal

from weighttogo.weight_tracking.domain.entities import WeightEntry
from weighttogo.weight_tracking.domain.exceptions import (
    DuplicateObservationDateError,
    ObservationDateInFutureError,
)
from weighttogo.weight_tracking.domain.ports import IWeightEntryRepository


@dataclass(frozen=True)
class CreateWeightEntryCommand:
    """Input for the CreateWeightEntry use case."""

    user_id: int
    weight_value: Decimal
    weight_unit: str
    observation_date: date
    notes: str | None


class CreateWeightEntry:
    """Create a new weight entry for a user.

    Args:
        weight_repo: The weight entry repository port.
    """

    def __init__(self, weight_repo: IWeightEntryRepository) -> None:
        """Initialise with the weight entry repository port."""
        self._repo = weight_repo

    def execute(self, command: CreateWeightEntryCommand) -> WeightEntry:
        """Execute the use case.

        Args:
            command: The create command with all required fields.

        Returns:
            The persisted ``WeightEntry`` with a database-assigned ``entry_id``.

        Raises:
            ObservationDateInFutureError: When ``observation_date`` is after today.
            DuplicateObservationDateError: When a non-deleted entry already exists
                for ``(user_id, observation_date)``.
        """
        if command.observation_date > date.today():
            raise ObservationDateInFutureError()

        if self._repo.exists_for_user_on_date(command.user_id, command.observation_date):
            raise DuplicateObservationDateError()

        now = datetime.now(UTC)
        entry = WeightEntry(
            entry_id=None,
            user_id=command.user_id,
            weight_value=command.weight_value,
            weight_unit=command.weight_unit,
            observation_date=command.observation_date,
            notes=command.notes,
            created_at=now,
            updated_at=now,
            is_deleted=False,
            deleted_at=None,
        )
        return self._repo.save(entry)
