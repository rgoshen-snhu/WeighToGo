"""Domain entities for the achievements bounded context.

Entities have identity and encapsulate domain behaviour. They carry no
dependency on any framework or persistence technology.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum


class AchievementType(StrEnum):
    """Categorises an achievement record."""

    GOAL_REACHED = "goal_reached"
    MILESTONE = "milestone"
    STREAK = "streak"


@dataclass
class Achievement:
    """A single achievement earned by a user.

    Attributes:
        achievement_id: Surrogate primary key. ``None`` for unsaved records.
        user_id: FK to the owning user.
        goal_id: FK to the goal this achievement belongs to.
        achievement_type: ``goal_reached``, ``milestone``, or ``streak``.
        threshold: The lb threshold crossed for milestones (5/10/25/50), the
            day count for streaks (7/30), or ``None`` for ``goal_reached``
            achievements.
        earned_at: UTC datetime when the achievement was first recorded.
    """

    achievement_id: int | None
    user_id: int
    goal_id: int
    achievement_type: AchievementType
    threshold: Decimal | None
    earned_at: datetime
