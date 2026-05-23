"""Unit tests for GetWeightEntry use case (subtask 10)."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from weighttogo.weight_tracking.domain.entities import WeightEntry
from weighttogo.weight_tracking.domain.exceptions import WeightEntryNotFoundError


def _make_entry(user_id: int = 1) -> WeightEntry:
    return WeightEntry(
        entry_id=1,
        user_id=user_id,
        weight_value=Decimal("175.50"),
        weight_unit="lbs",
        observation_date=date(2026, 5, 20),
        notes=None,
        created_at=datetime(2026, 5, 20, tzinfo=UTC),
        updated_at=datetime(2026, 5, 20, tzinfo=UTC),
    )


def _run(repo: MagicMock, user_id: int = 1, entry_id: int = 1) -> WeightEntry:
    from weighttogo.weight_tracking.application.get_weight_entry import (
        GetWeightEntry,
        GetWeightEntryCommand,
    )

    uc = GetWeightEntry(weight_repo=repo)
    return uc.execute(GetWeightEntryCommand(user_id=user_id, entry_id=entry_id))


def test_get_weight_entry_happy_path_returns_entry() -> None:
    repo = MagicMock()
    repo.get_by_id.return_value = _make_entry()
    result = _run(repo)
    assert result.entry_id == 1


def test_get_weight_entry_not_found_raises_not_found_error() -> None:
    repo = MagicMock()
    repo.get_by_id.return_value = None
    with pytest.raises(WeightEntryNotFoundError):
        _run(repo)


def test_get_weight_entry_calls_repo_with_user_scope() -> None:
    repo = MagicMock()
    repo.get_by_id.return_value = _make_entry()
    _run(repo, user_id=42, entry_id=7)
    repo.get_by_id.assert_called_once_with(entry_id=7, user_id=42)
