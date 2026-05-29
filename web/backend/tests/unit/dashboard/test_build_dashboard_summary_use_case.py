"""Unit tests for BuildDashboardSummary use case (subtask 20)."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from unittest.mock import MagicMock

from weighttogo.goals.application.get_active_goal_with_progress import GoalWithProgress
from weighttogo.weight_tracking.domain.entities import WeightEntry
from weighttogo.weight_tracking.domain.rate_of_change import RateOfChange


def _make_entry(entry_id: int = 1) -> WeightEntry:
    return WeightEntry(
        entry_id=entry_id,
        user_id=1,
        weight_value=Decimal("175.50"),
        weight_unit="lbs",
        observation_date=date(2026, 5, 20),
        notes=None,
        created_at=datetime(2026, 5, 20, tzinfo=UTC),
        updated_at=datetime(2026, 5, 20, tzinfo=UTC),
    )


def _run(repo: MagicMock, gag: MagicMock | None = None, user_id: int = 1) -> object:
    from weighttogo.dashboard.application.build_dashboard_summary import (
        BuildDashboardSummary,
    )

    if gag is None:
        gag = MagicMock()
        gag.execute.return_value = GoalWithProgress(goal=None, progress=None, current_value=None)
    grc = MagicMock()
    grc.execute.return_value = RateOfChange(weekly_rate=None, unit=None, reason="insufficient_data")
    repo.list_for_user_in_range.return_value = []
    uc = BuildDashboardSummary(
        weight_repo=repo,
        get_active_goal_with_progress=gag,
        get_rate_of_change=grc,
    )
    return uc.execute(user_id=user_id, today=date(2026, 5, 29))


def test_empty_user_returns_null_latest_entry() -> None:
    repo = MagicMock()
    repo.get_latest_for_user.return_value = None
    repo.count_for_user.return_value = 0
    result = _run(repo)
    assert result.latest_entry is None  # type: ignore[attr-defined]


def test_empty_user_returns_zero_total_entries() -> None:
    repo = MagicMock()
    repo.get_latest_for_user.return_value = None
    repo.count_for_user.return_value = 0
    result = _run(repo)
    assert result.total_entries == 0  # type: ignore[attr-defined]


def test_empty_user_returns_null_active_goal() -> None:
    repo = MagicMock()
    repo.get_latest_for_user.return_value = None
    repo.count_for_user.return_value = 0
    result = _run(repo)
    assert result.active_goal.goal is None  # type: ignore[attr-defined]


def test_populated_user_returns_latest_entry() -> None:
    repo = MagicMock()
    entry = _make_entry()
    repo.get_latest_for_user.return_value = entry
    repo.count_for_user.return_value = 5
    result = _run(repo)
    assert result.latest_entry == entry  # type: ignore[attr-defined]


def test_populated_user_returns_correct_count() -> None:
    repo = MagicMock()
    repo.get_latest_for_user.return_value = _make_entry()
    repo.count_for_user.return_value = 5
    result = _run(repo)
    assert result.total_entries == 5  # type: ignore[attr-defined]


def test_soft_deleted_entries_excluded_from_count() -> None:
    """count_for_user excludes soft-deleted entries (repository responsibility)."""
    repo = MagicMock()
    repo.get_latest_for_user.return_value = _make_entry()
    # repo.count_for_user already filters is_deleted=False by contract
    repo.count_for_user.return_value = 3
    result = _run(repo)
    assert result.total_entries == 3  # type: ignore[attr-defined]


def test_active_goal_populated_when_goal_exists() -> None:
    repo = MagicMock()
    repo.get_latest_for_user.return_value = _make_entry()
    repo.count_for_user.return_value = 1
    gag = MagicMock()
    gag.execute.return_value = GoalWithProgress(
        goal=MagicMock(), progress=MagicMock(), current_value=Decimal("170")
    )
    result = _run(repo, gag=gag)
    assert result.active_goal.goal is not None  # type: ignore[attr-defined]


def test_latest_entry_value_and_unit_passed_to_goal_use_case() -> None:
    repo = MagicMock()
    entry = _make_entry()
    repo.get_latest_for_user.return_value = entry
    repo.count_for_user.return_value = 1
    gag = MagicMock()
    gag.execute.return_value = GoalWithProgress(goal=None, progress=None, current_value=None)
    _run(repo, gag=gag)
    cmd = gag.execute.call_args.args[0]
    assert cmd.latest_weight_value == entry.weight_value
    assert cmd.latest_weight_unit == entry.weight_unit


def test_no_entry_passes_none_to_goal_use_case() -> None:
    repo = MagicMock()
    repo.get_latest_for_user.return_value = None
    repo.count_for_user.return_value = 0
    gag = MagicMock()
    gag.execute.return_value = GoalWithProgress(goal=None, progress=None, current_value=None)
    _run(repo, gag=gag)
    cmd = gag.execute.call_args.args[0]
    assert cmd.latest_weight_value is None
    assert cmd.latest_weight_unit is None


def test_goal_exists_with_no_entries_sets_active_goal_with_null_progress() -> None:
    """active_goal.goal is non-None when a goal exists even if progress is None (no entries)."""
    repo = MagicMock()
    repo.get_latest_for_user.return_value = None
    repo.count_for_user.return_value = 0
    gag = MagicMock()
    gag.execute.return_value = GoalWithProgress(goal=MagicMock(), progress=None, current_value=None)
    result = _run(repo, gag=gag)
    assert result.active_goal.goal is not None  # type: ignore[attr-defined]
    assert result.active_goal.progress is None  # type: ignore[attr-defined]


def test_summary_includes_rate_of_change() -> None:
    repo = MagicMock()
    repo.get_latest_for_user.return_value = _make_entry()
    repo.count_for_user.return_value = 5
    repo.list_for_user_in_range.return_value = []
    gag = MagicMock()
    gag.execute.return_value = GoalWithProgress(goal=None, progress=None, current_value=None)
    grc = MagicMock()
    grc.execute.return_value = RateOfChange(weekly_rate=Decimal("-1.5"), unit="lbs", reason=None)
    from weighttogo.dashboard.application.build_dashboard_summary import BuildDashboardSummary

    uc = BuildDashboardSummary(
        weight_repo=repo, get_active_goal_with_progress=gag, get_rate_of_change=grc
    )
    result = uc.execute(user_id=1, today=date(2026, 5, 29))
    assert result.rate_of_change.weekly_rate == Decimal("-1.5")
    assert result.rate_of_change.unit == "lbs"


def test_summary_includes_trend_series_oldest_first() -> None:
    repo = MagicMock()
    older = _make_entry(entry_id=1)
    newer = WeightEntry(
        entry_id=2,
        user_id=1,
        weight_value=Decimal("170.00"),
        weight_unit="lbs",
        observation_date=date(2026, 5, 25),
        notes=None,
        created_at=datetime(2026, 5, 25, tzinfo=UTC),
        updated_at=datetime(2026, 5, 25, tzinfo=UTC),
    )
    repo.get_latest_for_user.return_value = newer
    repo.count_for_user.return_value = 2
    # repository returns oldest-first per its contract
    repo.list_for_user_in_range.return_value = [older, newer]
    gag = MagicMock()
    gag.execute.return_value = GoalWithProgress(goal=None, progress=None, current_value=None)
    grc = MagicMock()
    grc.execute.return_value = RateOfChange(weekly_rate=None, unit=None, reason="insufficient_data")
    from weighttogo.dashboard.application.build_dashboard_summary import BuildDashboardSummary

    uc = BuildDashboardSummary(
        weight_repo=repo, get_active_goal_with_progress=gag, get_rate_of_change=grc
    )
    result = uc.execute(user_id=1, today=date(2026, 5, 29))
    assert [p.observation_date for p in result.trend] == [date(2026, 5, 20), date(2026, 5, 25)]
    assert result.trend[0].weight_value == Decimal("175.50")


def test_dashboard_does_not_write_when_goal_at_100_percent() -> None:
    """Dashboard summary must not trigger mark_achieved (readonly GET path)."""
    repo = MagicMock()
    repo.get_latest_for_user.return_value = _make_entry()
    repo.count_for_user.return_value = 1
    gag = MagicMock()
    gag.execute.return_value = GoalWithProgress(
        goal=MagicMock(), progress=MagicMock(), current_value=Decimal("150")
    )
    _run(repo, gag=gag)
    # The dashboard must pass readonly=True — verify via the command argument
    cmd = gag.execute.call_args.args[0]
    assert cmd.readonly is True
