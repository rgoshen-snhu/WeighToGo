"""Unit tests for DeleteWeightEntry use case (subtask 12)."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from weighttogo.weight_tracking.domain.entities import WeightEntry
from weighttogo.weight_tracking.domain.exceptions import WeightEntryNotFoundError


def _make_entry(user_id: int = 1, is_deleted: bool = False) -> WeightEntry:
    return WeightEntry(
        entry_id=1,
        user_id=user_id,
        weight_value=Decimal("175.50"),
        weight_unit="lbs",
        observation_date=date(2026, 5, 20),
        notes=None,
        created_at=datetime(2026, 5, 20, tzinfo=UTC),
        updated_at=datetime(2026, 5, 20, tzinfo=UTC),
        is_deleted=is_deleted,
        deleted_at=datetime.now(UTC) if is_deleted else None,
    )


def _run(repo: MagicMock, user_id: int = 1, entry_id: int = 1) -> None:
    from weighttogo.weight_tracking.application.delete_weight_entry import (
        DeleteWeightEntry,
        DeleteWeightEntryCommand,
    )

    uc = DeleteWeightEntry(weight_repo=repo)
    uc.execute(DeleteWeightEntryCommand(user_id=user_id, entry_id=entry_id))


def test_delete_weight_entry_happy_path_calls_soft_delete_and_save() -> None:
    repo = MagicMock()
    repo.get_by_id.return_value = _make_entry()
    _run(repo)
    saved_entry: WeightEntry = repo.save.call_args[0][0]
    assert saved_entry.is_deleted is True
    assert saved_entry.deleted_at is not None


def test_delete_weight_entry_not_found_raises_not_found() -> None:
    repo = MagicMock()
    repo.get_by_id.return_value = None
    with pytest.raises(WeightEntryNotFoundError):
        _run(repo)


def test_delete_weight_entry_already_deleted_is_idempotent() -> None:
    """Re-deleting an already-deleted entry must succeed without an extra save."""
    repo = MagicMock()
    repo.get_by_id.return_value = _make_entry(is_deleted=True)
    _run(repo)  # must not raise
    repo.save.assert_not_called()
