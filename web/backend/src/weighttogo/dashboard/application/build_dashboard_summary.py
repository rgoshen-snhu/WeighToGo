"""BuildDashboardSummary use case for the dashboard read model.

Covers FR-D-1 (summary), FR-D-4 (goal progress), FR-D-3 (weekly rate of
change), and FR-D-2 (trend series).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from weighttogo.goals.application.get_active_goal_with_progress import (
    GetActiveGoalWithProgress,
    GetActiveGoalWithProgressCommand,
    GoalWithProgress,
)
from weighttogo.weight_tracking.application.get_rate_of_change import GetRateOfChange
from weighttogo.weight_tracking.domain.entities import WeightEntry
from weighttogo.weight_tracking.domain.ports import IWeightEntryRepository
from weighttogo.weight_tracking.domain.rate_of_change import RateOfChange


@dataclass(frozen=True)
class TrendPoint:
    """A single point in the weight trend series (FR-D-2).

    Attributes:
        observation_date: Calendar date of the measurement.
        weight_value: Recorded weight.
        weight_unit: Either ``'lbs'`` or ``'kg'``.
    """

    observation_date: date
    weight_value: Decimal
    weight_unit: str


@dataclass(frozen=True)
class DashboardSummary:
    """Read-model returned by BuildDashboardSummary.

    Attributes:
        latest_entry: The most recent active weight entry, or ``None``.
        total_entries: Count of non-deleted weight entries.
        active_goal: The active goal with progress. ``goal`` within it is
            ``None`` when the user has no active goal.
        rate_of_change: The weekly rate of weight change (FR-D-3);
            ``weekly_rate`` is ``None`` when there is insufficient data.
        trend: The full weight series, oldest first, for the trend chart
            (FR-D-2). Empty when the user has no entries.
    """

    latest_entry: WeightEntry | None
    total_entries: int
    active_goal: GoalWithProgress
    rate_of_change: RateOfChange
    trend: list[TrendPoint]


class BuildDashboardSummary:
    """Assemble the dashboard read model for the requesting user.

    Composes the ``weight_tracking`` and ``goals`` bounded contexts. Goal
    progress is delegated to ``GetActiveGoalWithProgress`` and the weekly rate
    to ``GetRateOfChange`` (both reused, not reimplemented). The trend series is
    read once via the indexed range read and reused for every chart range.

    Args:
        weight_repo: The weight entry repository port.
        get_active_goal_with_progress: The goals use case that returns the
            active goal and its progress.
        get_rate_of_change: The use case that computes the weekly rate of
            change (FR-D-3).
    """

    def __init__(
        self,
        weight_repo: IWeightEntryRepository,
        get_active_goal_with_progress: GetActiveGoalWithProgress,
        get_rate_of_change: GetRateOfChange,
    ) -> None:
        """Initialise with the weight repository and the composed use cases."""
        self._repo = weight_repo
        self._get_active_goal = get_active_goal_with_progress
        self._get_rate_of_change = get_rate_of_change

    def execute(self, user_id: int, today: date | None = None) -> DashboardSummary:
        """Build the dashboard summary for *user_id*.

        Args:
            user_id: The requesting user's surrogate ID.
            today: Reference date for the rate-of-change window. Defaults to the
                server's current date; passed explicitly by tests for
                determinism.

        Returns:
            A ``DashboardSummary``; ``active_goal.goal`` is ``None`` when the
            user has no active goal, and ``trend`` is empty when the user has no
            entries.
        """
        reference_date = today if today is not None else date.today()

        latest_entry = self._repo.get_latest_for_user(user_id)
        total_entries = self._repo.count_for_user(user_id)
        goal_with_progress = self._get_active_goal.execute(
            GetActiveGoalWithProgressCommand(
                user_id=user_id,
                latest_weight_value=latest_entry.weight_value if latest_entry else None,
                latest_weight_unit=latest_entry.weight_unit if latest_entry else None,
                readonly=True,
            )
        )
        rate_of_change = self._get_rate_of_change.execute(user_id=user_id, today=reference_date)

        # "All time" trend: the full closed date range. The repository returns
        # entries oldest-first via the (user_id, observation_date) index.
        entries = self._repo.list_for_user_in_range(user_id, date.min, date.max)
        trend = [
            TrendPoint(
                observation_date=e.observation_date,
                weight_value=e.weight_value,
                weight_unit=e.weight_unit,
            )
            for e in entries
        ]

        return DashboardSummary(
            latest_entry=latest_entry,
            total_entries=total_entries,
            active_goal=goal_with_progress,
            rate_of_change=rate_of_change,
            trend=trend,
        )
