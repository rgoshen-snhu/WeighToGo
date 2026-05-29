"""Unit tests for ListGoals use case."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import MagicMock

from weighttogo.goals.application.list_goals import ListGoals, ListGoalsCommand
from weighttogo.goals.domain.entities import Goal, GoalType


def _make_goal(goal_id: int = 1) -> Goal:
    now = datetime.now(UTC)
    return Goal(
        goal_id=goal_id,
        user_id=1,
        target_value=Decimal("150"),
        target_unit="lbs",
        start_value=Decimal("200"),
        goal_type=GoalType.LOSE,
        target_date=None,
        is_active=True,
        is_achieved=False,
        achieved_at=None,
        created_at=now,
        updated_at=now,
    )


def _make_repo(goals: list[Goal]) -> MagicMock:
    repo = MagicMock()
    repo.list_for_user.return_value = goals
    return repo


def test_list_goals_returns_all_user_goals() -> None:
    goals = [_make_goal(1), _make_goal(2)]
    repo = _make_repo(goals)
    uc = ListGoals(goal_repo=repo)
    result = uc.execute(ListGoalsCommand(user_id=1))
    assert result == goals
    repo.list_for_user.assert_called_once_with(1, limit=50)


def test_list_goals_returns_empty_list_when_none() -> None:
    repo = _make_repo([])
    uc = ListGoals(goal_repo=repo)
    result = uc.execute(ListGoalsCommand(user_id=1))
    assert result == []


def test_list_goals_respects_custom_limit() -> None:
    goals = [_make_goal(1)]
    repo = _make_repo(goals)
    uc = ListGoals(goal_repo=repo)
    uc.execute(ListGoalsCommand(user_id=1, limit=10))
    repo.list_for_user.assert_called_once_with(1, limit=10)


def test_list_goals_caps_limit_at_100() -> None:
    repo = _make_repo([])
    uc = ListGoals(goal_repo=repo)
    uc.execute(ListGoalsCommand(user_id=1, limit=999))
    repo.list_for_user.assert_called_once_with(1, limit=100)
