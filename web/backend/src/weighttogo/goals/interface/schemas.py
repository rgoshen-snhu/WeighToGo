"""Pydantic request and response schemas for the goals API endpoints.

Validates inputs at the API boundary before any domain logic runs (SRS §NFR-S-4).
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from weighttogo.goals.application.get_active_goal_with_progress import GoalWithProgress


class GoalCreateRequest(BaseModel):
    """Request body for POST /api/v1/goals (SRS §9.6).

    Attributes:
        target_value: Target weight; positive, ≤ 1500.
        target_unit: Weight unit — ``'lbs'`` or ``'kg'``.
        start_value: Starting weight reference; positive, ≤ 1500.
        goal_type: Either ``'lose'`` or ``'gain'``.
        target_date: Optional date by which to reach the goal.
    """

    target_value: Decimal = Field(gt=Decimal("0"), le=Decimal("1500"))
    target_unit: Literal["lbs", "kg"]
    start_value: Decimal = Field(gt=Decimal("0"), le=Decimal("1500"))
    goal_type: Literal["lose", "gain"]
    target_date: date | None = None

    @model_validator(mode="after")
    def validate_direction(self) -> GoalCreateRequest:
        """Ensure target_value is in the correct direction relative to start_value."""
        if self.target_value == self.start_value:
            raise ValueError("target_value must differ from start_value.")
        if self.goal_type == "lose" and self.target_value >= self.start_value:
            raise ValueError("For a lose goal, target_value must be less than start_value.")
        if self.goal_type == "gain" and self.target_value <= self.start_value:
            raise ValueError("For a gain goal, target_value must be greater than start_value.")
        return self


class GoalUpdateRequest(BaseModel):
    """Request body for PUT /api/v1/goals/{goal_id} (FR-G-3).

    Only ``target_value`` and ``target_date`` are mutable; goal_type and
    start_value are immutable once set (SRS §6.3 FR-G-3).

    Attributes:
        target_value: New target weight; positive, ≤ 1500.
        target_date: New target date, or ``None`` to clear it.
    """

    target_value: Decimal = Field(gt=Decimal("0"), le=Decimal("1500"))
    target_date: date | None = None


class GoalResponse(BaseModel):
    """Response body for a single goal (SRS §9.6).

    Attributes:
        goal_id: Surrogate primary key.
        user_id: The owning user's ID.
        target_value: Target weight as a JSON number.
        target_unit: Weight unit.
        start_value: Starting weight.
        goal_type: ``'lose'`` or ``'gain'``.
        target_date: Optional target date.
        is_active: Whether the goal is currently in progress.
        is_achieved: Whether the goal has been reached.
        achieved_at: UTC timestamp of achievement, or ``None``.
        created_at: UTC timestamp of creation.
        updated_at: UTC timestamp of last update.
    """

    goal_id: int
    user_id: int
    target_value: float
    target_unit: str
    start_value: float
    goal_type: str
    target_date: date | None
    is_active: bool
    is_achieved: bool
    achieved_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ActiveGoalResponse(BaseModel):
    """Response body for GET /api/v1/goals/active (SRS §9.6).

    The ``goal`` field is ``None`` when no active goal exists (200 is still
    returned — 404 is reserved for IDOR on /{goal_id}).

    Attributes:
        goal: The active goal, or ``None``.
        progress_percent: Progress toward the goal in [0, 100], or ``None``
            when there is no active goal or no weight entries yet.
        current_value: The latest weight entry value in the goal's unit,
            or ``None`` when no entries exist.
    """

    goal: GoalResponse | None
    progress_percent: float | None
    current_value: float | None


class GoalListResponse(BaseModel):
    """Response body for GET /api/v1/goals.

    Attributes:
        goals: All goals (active and historical), newest first.
    """

    goals: list[GoalResponse]


def to_active_goal_response(result: GoalWithProgress) -> ActiveGoalResponse:
    """Map a ``GoalWithProgress`` application result to the ``ActiveGoalResponse`` DTO.

    Args:
        result: A non-``None`` ``GoalWithProgress`` from the use case. The
            ``goal`` field within it may be ``None`` (no active goal).

    Returns:
        An ``ActiveGoalResponse`` envelope; ``goal=None`` when no active goal.
    """
    if result.goal is None:
        return ActiveGoalResponse(goal=None, progress_percent=None, current_value=None)
    return ActiveGoalResponse(
        goal=GoalResponse.model_validate(result.goal),
        progress_percent=result.progress.percent if result.progress else None,
        current_value=float(result.current_value) if result.current_value is not None else None,
    )
