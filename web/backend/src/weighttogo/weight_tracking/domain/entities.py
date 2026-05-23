"""Domain entities for the weight_tracking bounded context.

Entities have identity and encapsulate domain behaviour. They have no
dependency on any framework or persistence technology.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from decimal import Decimal


@dataclass
class WeightEntry:
    """A single user weight observation.

    Attributes:
        entry_id: Surrogate primary key. ``None`` for unsaved entries.
        user_id: FK to the owning user.
        weight_value: Recorded weight as a Decimal preserving two decimal
            places of precision (SRS §3.2 micro-decision 1).
        weight_unit: Either ``'lbs'`` or ``'kg'``.
        observation_date: Calendar date of the measurement.
        notes: Optional free-text note (max 500 chars).
        created_at: UTC datetime the record was first persisted.
        updated_at: UTC datetime of the most recent update.
        is_deleted: Soft-delete flag; ``True`` once ``soft_delete()`` is called.
        deleted_at: UTC datetime of the soft-delete, or ``None`` if active.
    """

    entry_id: int | None
    user_id: int
    weight_value: Decimal
    weight_unit: str
    observation_date: date
    notes: str | None
    created_at: datetime
    updated_at: datetime
    is_deleted: bool = field(default=False)
    deleted_at: datetime | None = field(default=None)

    def soft_delete(self) -> None:
        """Mark this entry as deleted.

        Idempotent: calling this method more than once leaves ``deleted_at``
        unchanged after the first call (SRS §FR-W-4 idempotency requirement).
        """
        if self.is_deleted:
            return
        self.is_deleted = True
        self.deleted_at = datetime.now(UTC)
