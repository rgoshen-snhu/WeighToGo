"""Pydantic response schema for the dashboard API endpoint (response-only)."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel

from weighttogo.goals.interface.schemas import ActiveGoalResponse
from weighttogo.weight_tracking.interface.schemas import WeightEntryResponse


class RateOfChangeResponse(BaseModel):
    """Weekly rate of weight change (SRS §6.7, FR-D-3).

    Attributes:
        weekly_rate: Signed weight change per week as a JSON number (SRS §3.2
            micro-decision 1), or ``None`` when there is insufficient data.
        unit: The weight unit of ``weekly_rate``, or ``None``.
        reason: A short reason when ``weekly_rate`` is ``None`` (e.g.
            ``'insufficient_data'``); ``None`` otherwise.
    """

    weekly_rate: float | None
    unit: str | None
    reason: str | None


class TrendPointResponse(BaseModel):
    """A single point in the weight trend series (SRS §6.7, FR-D-2).

    Attributes:
        observation_date: Calendar date of the measurement.
        weight_value: Recorded weight as a JSON number (SRS §3.2 micro-decision 1).
        weight_unit: Either ``'lbs'`` or ``'kg'``.
    """

    observation_date: date
    weight_value: float
    weight_unit: str


class DashboardSummaryResponse(BaseModel):
    """Response body for GET /api/v1/dashboard/summary (SRS §9.5).

    Covers FR-D-1 (summary), FR-D-4 (goal progress), FR-D-3 (rate of change),
    and FR-D-2 (trend series).

    Attributes:
        latest_entry: The user's most recent active weight entry, or ``None``.
        total_entries: Count of non-deleted weight entries.
        active_goal: The active goal with progress, or ``None`` when no active
            goal exists.
        rate_of_change: The weekly rate of weight change.
        trend: The full weight series, oldest first, for the trend chart.
    """

    latest_entry: WeightEntryResponse | None
    total_entries: int
    active_goal: ActiveGoalResponse | None = None
    rate_of_change: RateOfChangeResponse
    trend: list[TrendPointResponse] = []
