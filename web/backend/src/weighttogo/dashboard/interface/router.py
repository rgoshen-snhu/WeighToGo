"""FastAPI router for the GET /api/v1/dashboard/summary endpoint.

Implements FR-D-1, FR-D-2, FR-D-3, and FR-D-4 per SRS §9.5.  The endpoint is
read-only and has no rate limit.  Auth is enforced via ``get_current_user_id``
from the auth interface.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from weighttogo.auth.interface.router import get_current_user_id
from weighttogo.dashboard.application.build_dashboard_summary import BuildDashboardSummary
from weighttogo.dashboard.interface.schemas import (
    DashboardSummaryResponse,
    RateOfChangeResponse,
    TrendPointResponse,
)
from weighttogo.goals.application.get_active_goal_with_progress import GetActiveGoalWithProgress
from weighttogo.goals.infrastructure.repositories import SqlAlchemyGoalRepository
from weighttogo.goals.interface.schemas import to_active_goal_response
from weighttogo.shared.db import get_db_session
from weighttogo.weight_tracking.application.get_rate_of_change import GetRateOfChange
from weighttogo.weight_tracking.infrastructure.repositories import (
    SqlAlchemyWeightEntryRepository,
)
from weighttogo.weight_tracking.interface.schemas import WeightEntryResponse

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get(
    "/summary",
    status_code=status.HTTP_200_OK,
    response_model=DashboardSummaryResponse,
    summary="Dashboard summary (FR-D-1, FR-D-2, FR-D-3, FR-D-4)",
)
def get_dashboard_summary(
    session: Session = Depends(get_db_session),
    current_user_id: int = Depends(get_current_user_id),
) -> DashboardSummaryResponse:
    """Return the dashboard summary for the authenticated user.

    Args:
        session: The active database session.
        current_user_id: The authenticated user's ID.

    Returns:
        ``DashboardSummaryResponse`` with latest entry, entry count, active goal
        progress, the weekly rate of change, and the trend series.

    Raises:
        HTTPException: 401 when no valid access token is present.
    """
    weight_repo = SqlAlchemyWeightEntryRepository(session)
    goal_repo = SqlAlchemyGoalRepository(session)
    get_active_goal = GetActiveGoalWithProgress(goal_repo=goal_repo)
    get_rate_of_change = GetRateOfChange(weight_repo=weight_repo)
    uc = BuildDashboardSummary(
        weight_repo=weight_repo,
        get_active_goal_with_progress=get_active_goal,
        get_rate_of_change=get_rate_of_change,
    )
    summary = uc.execute(user_id=current_user_id)

    latest = (
        WeightEntryResponse.model_validate(summary.latest_entry)
        if summary.latest_entry is not None
        else None
    )
    active_goal = (
        to_active_goal_response(summary.active_goal)
        if summary.active_goal.goal is not None
        else None
    )
    weekly_rate = summary.rate_of_change.weekly_rate
    rate_of_change = RateOfChangeResponse(
        weekly_rate=float(weekly_rate) if weekly_rate is not None else None,
        unit=summary.rate_of_change.unit,
        reason=summary.rate_of_change.reason,
    )
    trend = [
        TrendPointResponse(
            observation_date=point.observation_date,
            weight_value=float(point.weight_value),
            weight_unit=point.weight_unit,
        )
        for point in summary.trend
    ]
    return DashboardSummaryResponse(
        latest_entry=latest,
        total_entries=summary.total_entries,
        active_goal=active_goal,
        rate_of_change=rate_of_change,
        trend=trend,
    )
