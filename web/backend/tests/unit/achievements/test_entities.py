"""Unit tests for Achievement domain entities."""

from __future__ import annotations


def test_achievement_type_goal_reached_value() -> None:
    from weighttogo.achievements.domain.entities import AchievementType

    assert AchievementType.GOAL_REACHED.value == "goal_reached"


def test_achievement_type_milestone_value() -> None:
    from weighttogo.achievements.domain.entities import AchievementType

    assert AchievementType.MILESTONE.value == "milestone"


def test_achievement_type_streak_value() -> None:
    from weighttogo.achievements.domain.entities import AchievementType

    assert AchievementType.STREAK.value == "streak"


def test_achievement_dataclass_stores_milestone_threshold() -> None:
    from datetime import UTC, datetime
    from decimal import Decimal

    from weighttogo.achievements.domain.entities import Achievement, AchievementType

    # ARRANGE / ACT
    ach = Achievement(
        achievement_id=1,
        user_id=42,
        goal_id=7,
        achievement_type=AchievementType.MILESTONE,
        threshold=Decimal("5"),
        earned_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
    # ASSERT
    assert ach.threshold == Decimal("5")
    assert ach.achievement_type == AchievementType.MILESTONE


def test_achievement_goal_reached_has_null_threshold() -> None:
    from datetime import UTC, datetime

    from weighttogo.achievements.domain.entities import Achievement, AchievementType

    ach = Achievement(
        achievement_id=None,
        user_id=1,
        goal_id=1,
        achievement_type=AchievementType.GOAL_REACHED,
        threshold=None,
        earned_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
    assert ach.threshold is None
    assert ach.achievement_id is None
