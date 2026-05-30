"""Unit tests for BuildDashboardSummary use case (subtask 20)."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from unittest.mock import MagicMock

from weighttogo.goals.application.get_active_goal_with_progress import GoalWithProgress
from weighttogo.shared.units import convert_weight
from weighttogo.weight_tracking.domain.entities import WeightEntry


def _make_entry(
    entry_id: int = 1,
    observation_date: date = date(2026, 5, 20),
    weight_value: Decimal = Decimal("175.50"),
    weight_unit: str = "lbs",
) -> WeightEntry:
    return WeightEntry(
        entry_id=entry_id,
        user_id=1,
        weight_value=weight_value,
        weight_unit=weight_unit,
        observation_date=observation_date,
        notes=None,
        created_at=datetime(2026, 5, 20, tzinfo=UTC),
        updated_at=datetime(2026, 5, 20, tzinfo=UTC),
    )


def _run(
    repo: MagicMock,
    gag: MagicMock | None = None,
    user_id: int = 1,
    today: date = date(2026, 5, 29),
) -> object:
    from weighttogo.dashboard.application.build_dashboard_summary import (
        BuildDashboardSummary,
    )

    if gag is None:
        gag = MagicMock()
        gag.execute.return_value = GoalWithProgress(goal=None, progress=None, current_value=None)
    uc = BuildDashboardSummary(
        weight_repo=repo,
        get_active_goal_with_progress=gag,
    )
    return uc.execute(user_id=user_id, today=today)


def test_empty_user_returns_null_latest_entry() -> None:
    repo = MagicMock()
    repo.list_for_user_in_range.return_value = []
    result = _run(repo)
    assert result.latest_entry is None  # type: ignore[attr-defined]


def test_empty_user_returns_zero_total_entries() -> None:
    repo = MagicMock()
    repo.list_for_user_in_range.return_value = []
    result = _run(repo)
    assert result.total_entries == 0  # type: ignore[attr-defined]


def test_empty_user_returns_null_active_goal() -> None:
    repo = MagicMock()
    repo.list_for_user_in_range.return_value = []
    result = _run(repo)
    assert result.active_goal.goal is None  # type: ignore[attr-defined]


def test_populated_user_returns_latest_entry_as_last_of_series() -> None:
    repo = MagicMock()
    older = _make_entry(entry_id=1, observation_date=date(2026, 5, 20))
    newer = _make_entry(entry_id=2, observation_date=date(2026, 5, 25))
    repo.list_for_user_in_range.return_value = [older, newer]
    result = _run(repo)
    assert result.latest_entry == newer  # type: ignore[attr-defined]


def test_populated_user_returns_total_entries_as_series_length() -> None:
    repo = MagicMock()
    repo.list_for_user_in_range.return_value = [_make_entry(entry_id=i) for i in range(1, 6)]
    result = _run(repo)
    assert result.total_entries == 5  # type: ignore[attr-defined]


def test_active_goal_populated_when_goal_exists() -> None:
    repo = MagicMock()
    repo.list_for_user_in_range.return_value = [_make_entry()]
    gag = MagicMock()
    gag.execute.return_value = GoalWithProgress(
        goal=MagicMock(), progress=MagicMock(), current_value=Decimal("170")
    )
    result = _run(repo, gag=gag)
    assert result.active_goal.goal is not None  # type: ignore[attr-defined]


def test_latest_entry_value_and_unit_passed_to_goal_use_case() -> None:
    repo = MagicMock()
    entry = _make_entry()
    repo.list_for_user_in_range.return_value = [entry]
    gag = MagicMock()
    gag.execute.return_value = GoalWithProgress(goal=None, progress=None, current_value=None)
    _run(repo, gag=gag)
    cmd = gag.execute.call_args.args[0]
    assert cmd.latest_weight_value == entry.weight_value
    assert cmd.latest_weight_unit == entry.weight_unit


def test_no_entry_passes_none_to_goal_use_case() -> None:
    repo = MagicMock()
    repo.list_for_user_in_range.return_value = []
    gag = MagicMock()
    gag.execute.return_value = GoalWithProgress(goal=None, progress=None, current_value=None)
    _run(repo, gag=gag)
    cmd = gag.execute.call_args.args[0]
    assert cmd.latest_weight_value is None
    assert cmd.latest_weight_unit is None


def test_goal_exists_with_no_entries_sets_active_goal_with_null_progress() -> None:
    """active_goal.goal is non-None when a goal exists even if progress is None (no entries)."""
    repo = MagicMock()
    repo.list_for_user_in_range.return_value = []
    gag = MagicMock()
    gag.execute.return_value = GoalWithProgress(goal=MagicMock(), progress=None, current_value=None)
    result = _run(repo, gag=gag)
    assert result.active_goal.goal is not None  # type: ignore[attr-defined]
    assert result.active_goal.progress is None  # type: ignore[attr-defined]


def test_latest_entry_keeps_stored_unit_when_kg() -> None:
    """latest_entry must remain in its stored unit; only rate/trend are lbs-normalized."""
    repo = MagicMock()
    entry = _make_entry(weight_value=Decimal("80.00"), weight_unit="kg")
    repo.list_for_user_in_range.return_value = [entry]
    result = _run(repo)
    assert result.latest_entry.weight_unit == "kg"  # type: ignore[attr-defined]
    assert result.latest_entry.weight_value == Decimal("80.00")  # type: ignore[attr-defined]


def test_rate_uses_full_series_anchor_when_latest_older_than_today() -> None:
    """The anchor is the latest observation in the series, not `today` (anchor fix)."""
    repo = MagicMock()
    # Latest entry is 2026-05-20, well before today (2026-05-29). Two 7-day
    # windows anchored on 2026-05-20 each contain one entry.
    recent = _make_entry(
        entry_id=2, observation_date=date(2026, 5, 18), weight_value=Decimal("180.00")
    )
    prior = _make_entry(
        entry_id=1, observation_date=date(2026, 5, 11), weight_value=Decimal("190.00")
    )
    repo.list_for_user_in_range.return_value = [prior, recent]
    result = _run(repo, today=date(2026, 5, 29))
    assert result.rate_of_change.weekly_rate == Decimal("-10")  # type: ignore[attr-defined]
    assert result.rate_of_change.unit == "lbs"  # type: ignore[attr-defined]


def test_rate_normalizes_mixed_units_to_lbs() -> None:
    """A kg entry in a window is converted to lbs before the rate is computed."""
    repo = MagicMock()
    # Anchor on 2026-05-20. Recent window (05-13, 05-20] has the kg entry;
    # prior window (05-06, 05-13] has an lbs entry.
    prior = _make_entry(
        entry_id=1,
        observation_date=date(2026, 5, 10),
        weight_value=Decimal("200.00"),
        weight_unit="lbs",
    )
    recent = _make_entry(
        entry_id=2,
        observation_date=date(2026, 5, 20),
        weight_value=Decimal("90.00"),
        weight_unit="kg",
    )
    repo.list_for_user_in_range.return_value = [prior, recent]
    result = _run(repo, today=date(2026, 5, 29))
    # 90 kg -> ~198.416 lbs; rate = 198.416... - 200.0
    assert result.rate_of_change.unit == "lbs"  # type: ignore[attr-defined]
    expected = convert_weight(Decimal("90.00"), "kg", "lbs") - Decimal("200.00")
    assert result.rate_of_change.weekly_rate == expected  # type: ignore[attr-defined]


def test_summary_includes_trend_series_oldest_first_normalized_to_lbs() -> None:
    repo = MagicMock()
    older = _make_entry(entry_id=1, observation_date=date(2026, 5, 20))
    newer = _make_entry(
        entry_id=2,
        observation_date=date(2026, 5, 25),
        weight_value=Decimal("80.00"),
        weight_unit="kg",
    )
    repo.list_for_user_in_range.return_value = [older, newer]
    result = _run(repo)
    assert [p.observation_date for p in result.trend] == [  # type: ignore[attr-defined]
        date(2026, 5, 20),
        date(2026, 5, 25),
    ]
    assert result.trend[0].weight_value == Decimal("175.50")  # type: ignore[attr-defined]
    assert result.trend[0].weight_unit == "lbs"  # type: ignore[attr-defined]
    # kg entry is normalized to lbs in the trend
    assert result.trend[1].weight_unit == "lbs"  # type: ignore[attr-defined]
    assert result.trend[1].weight_value == convert_weight(  # type: ignore[attr-defined]
        Decimal("80.00"), "kg", "lbs"
    )


def test_dashboard_does_not_write_when_goal_at_100_percent() -> None:
    """Dashboard summary must not trigger mark_achieved (readonly GET path)."""
    repo = MagicMock()
    repo.list_for_user_in_range.return_value = [_make_entry()]
    gag = MagicMock()
    gag.execute.return_value = GoalWithProgress(
        goal=MagicMock(), progress=MagicMock(), current_value=Decimal("150")
    )
    _run(repo, gag=gag)
    cmd = gag.execute.call_args.args[0]
    assert cmd.readonly is True
