"""FastAPI router for the /api/v1/goals endpoints.

Implements FR-G-1 through FR-G-3 and FR-D-4 per SRS §9.6. Every endpoint
requires a valid access-token cookie via ``get_current_user_id``.

Cross-domain coordination (Option B — progress never null due to unit
mismatch): ``GET /active`` fetches the latest weight entry at the
composition root (interface layer) and passes it into
``GetActiveGoalWithProgress``. The ``goals`` domain never imports
``weight_tracking`` — the wiring happens here, mirroring how the dashboard
aggregates data from multiple domains.

Domain exceptions translate to HTTP responses at the router edge, following
the same try/except pattern as the weight-entries router.
"""

from __future__ import annotations

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from weighttogo.auth.interface.router import get_current_user_id, limiter
from weighttogo.goals.application.abandon_goal import AbandonGoal, AbandonGoalCommand
from weighttogo.goals.application.get_active_goal_with_progress import (
    GetActiveGoalWithProgress,
    GetActiveGoalWithProgressCommand,
)
from weighttogo.goals.application.list_goals import ListGoals, ListGoalsCommand
from weighttogo.goals.application.set_active_goal import SetActiveGoal, SetActiveGoalCommand
from weighttogo.goals.application.update_goal import UpdateGoal, UpdateGoalCommand
from weighttogo.goals.domain.exceptions import (
    ActiveGoalAlreadyExistsError,
    GoalNotActiveError,
    GoalNotFoundError,
    InvalidGoalTargetError,
)
from weighttogo.goals.infrastructure.repositories import SqlAlchemyGoalRepository
from weighttogo.goals.interface.schemas import (
    ActiveGoalResponse,
    GoalCreateRequest,
    GoalListResponse,
    GoalResponse,
    GoalUpdateRequest,
)
from weighttogo.shared.db import get_db_session
from weighttogo.weight_tracking.infrastructure.repositories import SqlAlchemyWeightEntryRepository

logger = structlog.stdlib.get_logger(__name__)

router = APIRouter(prefix="/goals", tags=["goals"])


def _goal_repo(session: Session) -> SqlAlchemyGoalRepository:
    return SqlAlchemyGoalRepository(session)


def _weight_repo(session: Session) -> SqlAlchemyWeightEntryRepository:
    return SqlAlchemyWeightEntryRepository(session)


# ── POST /goals ───────────────────────────────────────────────────────────────


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=GoalResponse,
    summary="Set a new active goal (FR-G-1)",
)
@limiter.limit("30/minute")
def create_goal(
    request: Request,
    payload: GoalCreateRequest,
    session: Session = Depends(get_db_session),
    current_user_id: int = Depends(get_current_user_id),
) -> GoalResponse:
    """Create an active goal for the authenticated user.

    Args:
        request: The incoming HTTP request (required by slowapi).
        payload: Validated request body.
        session: The active database session.
        current_user_id: The authenticated user's ID.

    Returns:
        The newly created goal.

    Raises:
        HTTPException: 409 when the user already has an active goal.
    """
    repo = _goal_repo(session)
    uc = SetActiveGoal(goal_repo=repo)

    try:
        goal = uc.execute(
            SetActiveGoalCommand(
                user_id=current_user_id,
                target_value=payload.target_value,
                target_unit=payload.target_unit,
                start_value=payload.start_value,
                goal_type=payload.goal_type,
                target_date=payload.target_date,
            )
        )
    except ActiveGoalAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already has an active goal.",
        ) from exc

    logger.info("goal_created", goal_id=goal.goal_id, user_id=current_user_id)
    return GoalResponse.model_validate(goal)


# ── GET /goals/active ─────────────────────────────────────────────────────────


@router.get(
    "/active",
    status_code=status.HTTP_200_OK,
    response_model=ActiveGoalResponse,
    summary="Get the active goal with progress (FR-G-2, FR-D-4)",
)
def get_active_goal(
    session: Session = Depends(get_db_session),
    current_user_id: int = Depends(get_current_user_id),
) -> ActiveGoalResponse:
    """Return the authenticated user's active goal and progress.

    200 is returned even when no active goal exists — the ``goal`` field
    will be ``None``.  404 is reserved for IDOR on /{goal_id}.

    Args:
        session: The active database session.
        current_user_id: The authenticated user's ID.

    Returns:
        The active goal with progress, or a null-goal envelope.
    """
    latest = _weight_repo(session).get_latest_for_user(current_user_id)

    result = GetActiveGoalWithProgress(goal_repo=_goal_repo(session)).execute(
        GetActiveGoalWithProgressCommand(
            user_id=current_user_id,
            latest_weight_value=latest.weight_value if latest else None,
            latest_weight_unit=latest.weight_unit if latest else None,
        )
    )

    if result.goal is None:
        return ActiveGoalResponse(goal=None, progress_percent=None, current_value=None)

    return ActiveGoalResponse(
        goal=GoalResponse.model_validate(result.goal),
        progress_percent=result.progress.percent if result.progress else None,
        current_value=float(result.current_value) if result.current_value is not None else None,
    )


# ── GET /goals ────────────────────────────────────────────────────────────────


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=GoalListResponse,
    summary="List goals for the current user (capped at 100)",
)
@limiter.limit("30/minute")
def list_goals(
    request: Request,
    limit: int = Query(default=50, ge=1, le=100, description="Maximum goals to return (1–100)."),
    session: Session = Depends(get_db_session),
    current_user_id: int = Depends(get_current_user_id),
) -> GoalListResponse:
    """Return recent goals (active and historical) for the authenticated user.

    Results are ordered newest-first and capped at *limit* (max 100) to prevent
    unbounded DB reads and serialization cost on accounts with large goal histories.

    Args:
        request: The incoming HTTP request (required by slowapi).
        limit: Maximum number of goals to return (1 – 100, default 50).
        session: The active database session.
        current_user_id: The authenticated user's ID.

    Returns:
        A list of at most *limit* goals, newest first.
    """
    goals = ListGoals(goal_repo=_goal_repo(session)).execute(
        ListGoalsCommand(user_id=current_user_id, limit=limit)
    )
    return GoalListResponse(goals=[GoalResponse.model_validate(g) for g in goals])


# ── PUT /goals/{goal_id} ──────────────────────────────────────────────────────


@router.put(
    "/{goal_id}",
    status_code=status.HTTP_200_OK,
    response_model=GoalResponse,
    summary="Update a goal's target value or target date (FR-G-3)",
)
@limiter.limit("30/minute")
def update_goal(
    request: Request,
    goal_id: int,
    payload: GoalUpdateRequest,
    session: Session = Depends(get_db_session),
    current_user_id: int = Depends(get_current_user_id),
) -> GoalResponse | Response:
    """Update an active goal owned by the authenticated user.

    Only ``target_value`` and ``target_date`` are mutable (FR-G-3).

    Args:
        request: The incoming HTTP request (required by slowapi).
        goal_id: The goal's primary key.
        payload: Validated request body.
        session: The active database session.
        current_user_id: The authenticated user's ID.

    Returns:
        The updated goal.

    Raises:
        HTTPException: 404 when the goal does not exist or belongs to another user.
    """
    try:
        goal = UpdateGoal(goal_repo=_goal_repo(session)).execute(
            UpdateGoalCommand(
                user_id=current_user_id,
                goal_id=goal_id,
                target_value=payload.target_value,
                target_date=payload.target_date,
            )
        )
    except GoalNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found.",
        ) from exc
    except GoalNotActiveError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Goal is no longer active and cannot be modified.",
        ) from exc
    except InvalidGoalTargetError as exc:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "type": "about:blank",
                "title": "Validation failed",
                "status": 422,
                "detail": str(exc),
                "instance": request.url.path,
                "errors": [
                    {"field": "target_value", "code": "direction_error", "message": str(exc)}
                ],
            },
        )

    logger.info("goal_updated", goal_id=goal.goal_id, user_id=current_user_id)
    return GoalResponse.model_validate(goal)


# ── DELETE /goals/{goal_id} ───────────────────────────────────────────────────


@router.delete(
    "/{goal_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Abandon a goal (soft-deactivate)",
)
@limiter.limit("30/minute")
def abandon_goal(
    request: Request,
    goal_id: int,
    session: Session = Depends(get_db_session),
    current_user_id: int = Depends(get_current_user_id),
) -> Response:
    """Abandon a goal owned by the authenticated user.

    Idempotent at the domain level: abandoning an already-inactive goal
    succeeds.

    Args:
        request: The incoming HTTP request (required by slowapi).
        goal_id: The goal's primary key.
        session: The active database session.
        current_user_id: The authenticated user's ID.

    Returns:
        Empty 204 response on success.

    Raises:
        HTTPException: 404 when the goal does not exist or belongs to another user.
    """
    try:
        AbandonGoal(goal_repo=_goal_repo(session)).execute(
            AbandonGoalCommand(user_id=current_user_id, goal_id=goal_id)
        )
    except GoalNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found.",
        ) from exc

    logger.info("goal_abandoned", goal_id=goal_id, user_id=current_user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
