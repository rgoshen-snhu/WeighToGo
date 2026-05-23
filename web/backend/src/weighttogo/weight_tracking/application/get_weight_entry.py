"""GetWeightEntry use case (FR-W-5)."""

from __future__ import annotations

from dataclasses import dataclass

from weighttogo.weight_tracking.domain.entities import WeightEntry
from weighttogo.weight_tracking.domain.exceptions import WeightEntryNotFoundError
from weighttogo.weight_tracking.domain.ports import IWeightEntryRepository


@dataclass(frozen=True)
class GetWeightEntryCommand:
    """Input for the GetWeightEntry use case."""

    user_id: int
    entry_id: int


class GetWeightEntry:
    """Retrieve a single weight entry by ID, scoped to the requesting user.

    Args:
        weight_repo: The weight entry repository port.
    """

    def __init__(self, weight_repo: IWeightEntryRepository) -> None:
        """Initialise with the weight entry repository port."""
        self._repo = weight_repo

    def execute(self, command: GetWeightEntryCommand) -> WeightEntry:
        """Execute the use case.

        Args:
            command: The get command with the entry and user IDs.

        Returns:
            The matching ``WeightEntry``.

        Raises:
            WeightEntryNotFoundError: When the entry does not exist or belongs
                to a different user.
        """
        entry = self._repo.get_by_id(entry_id=command.entry_id, user_id=command.user_id)
        if entry is None:
            raise WeightEntryNotFoundError()
        return entry
