"""Unit tests for CreateWeightEntry use case (subtask 6–8)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any
from unittest.mock import MagicMock

import pytest

from weighttogo.weight_tracking.domain.entities import WeightEntry
from weighttogo.weight_tracking.domain.exceptions import (
    DuplicateObservationDateError,
    ObservationDateInFutureError,
)


def _make_mock_repo(**overrides: Any) -> MagicMock:
    repo = MagicMock()
    repo.exists_for_user_on_date.return_value = overrides.get("exists", False)
    repo.save.side_effect = lambda e: e
    return repo


def _run(
    repo: Any,
    user_id: int = 1,
    weight_value: Decimal = Decimal("175.50"),
    weight_unit: str = "lbs",
    observation_date: date = date(2026, 5, 20),
    notes: str | None = None,
) -> WeightEntry:
    from weighttogo.weight_tracking.application.create_weight_entry import (
        CreateWeightEntry,
        CreateWeightEntryCommand,
    )

    uc = CreateWeightEntry(weight_repo=repo)
    return uc.execute(
        CreateWeightEntryCommand(
            user_id=user_id,
            weight_value=weight_value,
            weight_unit=weight_unit,
            observation_date=observation_date,
            notes=notes,
        )
    )


# ── Subtask 6: happy path ─────────────────────────────────────────────────────


def test_create_weight_entry_happy_path_calls_save() -> None:
    repo = _make_mock_repo()
    _run(repo)
    repo.save.assert_called_once()


def test_create_weight_entry_happy_path_sets_is_deleted_false() -> None:
    repo = _make_mock_repo()
    result = _run(repo)
    assert result.is_deleted is False


def test_create_weight_entry_happy_path_preserves_decimal_precision() -> None:
    repo = _make_mock_repo()
    result = _run(repo, weight_value=Decimal("175.50"))
    assert result.weight_value == Decimal("175.50")


# ── Subtask 7: duplicate date ─────────────────────────────────────────────────


def test_create_weight_entry_raises_duplicate_on_existing_date() -> None:
    repo = _make_mock_repo(exists=True)
    with pytest.raises(DuplicateObservationDateError):
        _run(repo)


# ── Subtask 8: future date ────────────────────────────────────────────────────


def test_create_weight_entry_raises_future_date_for_tomorrow() -> None:
    from datetime import timedelta

    future = date.today() + timedelta(days=1)
    repo = _make_mock_repo()
    with pytest.raises(ObservationDateInFutureError):
        _run(repo, observation_date=future)


def test_create_weight_entry_allows_today() -> None:
    repo = _make_mock_repo()
    result = _run(repo, observation_date=date.today())
    assert result.observation_date == date.today()
