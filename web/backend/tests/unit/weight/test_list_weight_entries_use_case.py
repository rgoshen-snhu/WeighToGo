"""Unit tests for ListWeightEntries use case (subtask 9)."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from unittest.mock import MagicMock

from weighttogo.weight_tracking.domain.entities import WeightEntry


def _make_entry(
    entry_id: int = 1,
    observation_date: date = date(2026, 5, 20),
) -> WeightEntry:
    return WeightEntry(
        entry_id=entry_id,
        user_id=1,
        weight_value=Decimal("175.00"),
        weight_unit="lbs",
        observation_date=observation_date,
        notes=None,
        created_at=datetime(2026, 5, 20, tzinfo=UTC),
        updated_at=datetime(2026, 5, 20, tzinfo=UTC),
    )


def _run(repo: MagicMock, user_id: int = 1, limit: int = 10, cursor: int | None = None) -> object:
    from weighttogo.weight_tracking.application.list_weight_entries import (
        ListWeightEntries,
        ListWeightEntriesCommand,
    )

    uc = ListWeightEntries(weight_repo=repo)
    return uc.execute(ListWeightEntriesCommand(user_id=user_id, limit=limit, cursor=cursor))


def test_list_weight_entries_empty_returns_empty_list() -> None:
    repo = MagicMock()
    repo.list_for_user.return_value = []
    result = _run(repo)
    assert result.items == []  # type: ignore[attr-defined]
    assert result.next_cursor is None  # type: ignore[attr-defined]


def test_list_weight_entries_calls_list_for_user_with_limit_plus_one() -> None:
    repo = MagicMock()
    repo.list_for_user.return_value = []
    _run(repo, limit=5)
    repo.list_for_user.assert_called_once_with(user_id=1, limit=6, before_id=None)


def test_list_weight_entries_sets_next_cursor_when_page_full() -> None:
    repo = MagicMock()
    entries = [_make_entry(entry_id=i) for i in range(11)]
    repo.list_for_user.return_value = entries
    result = _run(repo, limit=10)
    assert len(result.items) == 10  # type: ignore[attr-defined]
    assert result.next_cursor is not None  # type: ignore[attr-defined]


def test_list_weight_entries_no_cursor_when_fewer_results_than_limit() -> None:
    repo = MagicMock()
    entries = [_make_entry(entry_id=i) for i in range(5)]
    repo.list_for_user.return_value = entries
    result = _run(repo, limit=10)
    assert len(result.items) == 5  # type: ignore[attr-defined]
    assert result.next_cursor is None  # type: ignore[attr-defined]
