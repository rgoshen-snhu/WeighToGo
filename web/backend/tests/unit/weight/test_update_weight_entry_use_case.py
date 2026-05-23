"""Unit tests for UpdateWeightEntry use case (subtask 11)."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from weighttogo.weight_tracking.domain.entities import WeightEntry
from weighttogo.weight_tracking.domain.exceptions import (
    DuplicateObservationDateError,
    ObservationDateInFutureError,
    WeightEntryNotFoundError,
)


def _make_entry(
    entry_id: int = 1,
    user_id: int = 1,
    observation_date: date = date(2026, 5, 20),
) -> WeightEntry:
    return WeightEntry(
        entry_id=entry_id,
        user_id=user_id,
        weight_value=Decimal("175.50"),
        weight_unit="lbs",
        observation_date=observation_date,
        notes=None,
        created_at=datetime(2026, 5, 20, tzinfo=UTC),
        updated_at=datetime(2026, 5, 20, tzinfo=UTC),
    )


def _run(
    repo: MagicMock,
    user_id: int = 1,
    entry_id: int = 1,
    weight_value: Decimal = Decimal("180.00"),
    weight_unit: str = "lbs",
    observation_date: date = date(2026, 5, 20),
    notes: str | None = None,
) -> WeightEntry:
    from weighttogo.weight_tracking.application.update_weight_entry import (
        UpdateWeightEntry,
        UpdateWeightEntryCommand,
    )

    uc = UpdateWeightEntry(weight_repo=repo)
    return uc.execute(
        UpdateWeightEntryCommand(
            user_id=user_id,
            entry_id=entry_id,
            weight_value=weight_value,
            weight_unit=weight_unit,
            observation_date=observation_date,
            notes=notes,
        )
    )


def test_update_weight_entry_happy_path_saves_new_value() -> None:
    repo = MagicMock()
    repo.get_by_id.return_value = _make_entry()
    repo.exists_for_user_on_date.return_value = False
    repo.save.side_effect = lambda e: e
    result = _run(repo, weight_value=Decimal("180.00"))
    assert result.weight_value == Decimal("180.00")


def test_update_weight_entry_not_found_raises_not_found() -> None:
    repo = MagicMock()
    repo.get_by_id.return_value = None
    with pytest.raises(WeightEntryNotFoundError):
        _run(repo)


def test_update_weight_entry_date_conflict_raises_duplicate() -> None:
    repo = MagicMock()
    repo.get_by_id.return_value = _make_entry(observation_date=date(2026, 5, 20))
    repo.exists_for_user_on_date.return_value = True
    with pytest.raises(DuplicateObservationDateError):
        _run(repo, observation_date=date(2026, 5, 21))


def test_update_weight_entry_same_date_allowed() -> None:
    repo = MagicMock()
    entry = _make_entry(observation_date=date(2026, 5, 20))
    repo.get_by_id.return_value = entry
    # The exists check excludes the current entry_id, so returns False
    repo.exists_for_user_on_date.return_value = False
    repo.save.side_effect = lambda e: e
    result = _run(repo, observation_date=date(2026, 5, 20))
    assert result.observation_date == date(2026, 5, 20)


def test_update_weight_entry_future_date_raises_future_error() -> None:
    from datetime import timedelta

    repo = MagicMock()
    repo.get_by_id.return_value = _make_entry()
    repo.exists_for_user_on_date.return_value = False
    future = date.today() + timedelta(days=1)
    with pytest.raises(ObservationDateInFutureError):
        _run(repo, observation_date=future)


def test_update_weight_entry_advances_updated_at() -> None:
    before = datetime.now(UTC)
    repo = MagicMock()
    repo.get_by_id.return_value = _make_entry()
    repo.exists_for_user_on_date.return_value = False
    repo.save.side_effect = lambda e: e
    result = _run(repo)
    assert result.updated_at >= before
