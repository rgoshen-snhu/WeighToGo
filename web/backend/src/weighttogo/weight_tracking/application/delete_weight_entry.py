"""DeleteWeightEntry use case (FR-W-4)."""

from __future__ import annotations

from dataclasses import dataclass

from weighttogo.weight_tracking.domain.exceptions import WeightEntryNotFoundError
from weighttogo.weight_tracking.domain.ports import IWeightEntryRepository


@dataclass(frozen=True)
class DeleteWeightEntryCommand:
    """Input for the DeleteWeightEntry use case."""

    user_id: int
    entry_id: int


class DeleteWeightEntry:
    """Soft-delete a weight entry owned by the requesting user.

    Re-deleting an already-deleted entry is idempotent — it returns without
    error and does not perform an extra DB write (SRS §FR-W-4).

    Args:
        weight_repo: The weight entry repository port.
    """

    def __init__(self, weight_repo: IWeightEntryRepository) -> None:
        """Initialise with the weight entry repository port."""
        self._repo = weight_repo

    def execute(self, command: DeleteWeightEntryCommand) -> None:
        """Execute the use case.

        Args:
            command: The delete command with the entry and user IDs.

        Raises:
            WeightEntryNotFoundError: When the entry does not exist or belongs
                to a different user (not raised for already-deleted entries).
        """
        entry = self._repo.get_by_id(entry_id=command.entry_id, user_id=command.user_id)
        if entry is None:
            raise WeightEntryNotFoundError()

        if entry.is_deleted:
            # Idempotent re-delete: succeed without an extra DB write.
            return

        entry.soft_delete()
        self._repo.save(entry)
