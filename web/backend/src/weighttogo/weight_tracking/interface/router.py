"""FastAPI router for the /api/v1/weight-entries endpoints.

Implements FR-W-1 through FR-W-5 per SRS §9.4.  Every endpoint requires a
valid access-token cookie via the ``get_current_user_id`` dependency imported
from the auth interface (NFR-S-3, NFR-S-4).

Rate limiting (NFR-S-5) is applied to write endpoints at 30 requests/minute
per user.  The limiter is shared via the application's ``app.state.limiter``
so that slowapi can track buckets centrally.

Domain exceptions translate to HTTP responses at the router edge, following
the same try/except pattern as the auth router.
"""

from __future__ import annotations

import structlog
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from weighttogo.auth.interface.router import get_current_user_id, limiter
from weighttogo.shared.db import get_db_session
from weighttogo.weight_tracking.application.create_weight_entry import (
    CreateWeightEntry,
    CreateWeightEntryCommand,
)
from weighttogo.weight_tracking.application.delete_weight_entry import (
    DeleteWeightEntry,
    DeleteWeightEntryCommand,
)
from weighttogo.weight_tracking.application.get_weight_entry import (
    GetWeightEntry,
    GetWeightEntryCommand,
)
from weighttogo.weight_tracking.application.list_weight_entries import (
    ListWeightEntries,
    ListWeightEntriesCommand,
)
from weighttogo.weight_tracking.application.update_weight_entry import (
    UpdateWeightEntry,
    UpdateWeightEntryCommand,
)
from weighttogo.weight_tracking.domain.exceptions import (
    DuplicateObservationDateError,
    ObservationDateInFutureError,
    WeightEntryNotFoundError,
)
from weighttogo.weight_tracking.infrastructure.repositories import (
    SqlAlchemyWeightEntryRepository,
)
from weighttogo.weight_tracking.interface.schemas import (
    WeightEntryListResponse,
    WeightEntryRequest,
    WeightEntryResponse,
)

logger = structlog.stdlib.get_logger(__name__)

router = APIRouter(prefix="/weight-entries", tags=["weight"])

_DEFAULT_PAGE_SIZE = 20
_MAX_PAGE_SIZE = 100


def _weight_repo(session: Session) -> SqlAlchemyWeightEntryRepository:
    """Construct the repository for the current request."""
    return SqlAlchemyWeightEntryRepository(session)


# ── POST /weight-entries ──────────────────────────────────────────────────────


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=WeightEntryResponse,
    summary="Create a new weight entry (FR-W-1)",
)
@limiter.limit("30/minute")
def create_weight_entry(
    request: Request,
    payload: WeightEntryRequest,
    session: Session = Depends(get_db_session),
    current_user_id: int = Depends(get_current_user_id),
) -> WeightEntryResponse:
    """Create a weight entry for the authenticated user.

    Args:
        request: The incoming HTTP request (required by slowapi).
        payload: Validated request body.
        session: The active database session.
        current_user_id: The authenticated user's ID.

    Returns:
        The newly created weight entry.

    Raises:
        HTTPException: 409 when a non-deleted entry already exists for the date.
        HTTPException: 422 when the observation date is in the future.
    """
    repo = _weight_repo(session)
    uc = CreateWeightEntry(weight_repo=repo)

    try:
        entry = uc.execute(
            CreateWeightEntryCommand(
                user_id=current_user_id,
                weight_value=payload.weight_value,
                weight_unit=payload.weight_unit,
                observation_date=payload.observation_date,
                notes=payload.notes,
            )
        )
    except DuplicateObservationDateError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An entry already exists for this date.",
        ) from exc
    except ObservationDateInFutureError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Observation date cannot be in the future.",
        ) from exc

    logger.info("weight_entry_created", entry_id=entry.entry_id, user_id=current_user_id)
    return WeightEntryResponse.model_validate(entry)


# ── GET /weight-entries ───────────────────────────────────────────────────────


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=WeightEntryListResponse,
    summary="List weight entries (FR-W-2)",
)
def list_weight_entries(
    request: Request,
    limit: int = _DEFAULT_PAGE_SIZE,
    cursor: int | None = None,
    session: Session = Depends(get_db_session),
    current_user_id: int = Depends(get_current_user_id),
) -> WeightEntryListResponse:
    """Return a paginated list of weight entries for the authenticated user.

    Args:
        request: The incoming HTTP request.
        limit: Maximum number of entries per page (default 20, max 100).
        cursor: Pagination cursor (entry_id of the last item on the previous page).
        session: The active database session.
        current_user_id: The authenticated user's ID.

    Returns:
        A paginated envelope with ``items`` and ``next_cursor``.
    """
    effective_limit = min(limit, _MAX_PAGE_SIZE)
    repo = _weight_repo(session)
    uc = ListWeightEntries(weight_repo=repo)

    page = uc.execute(
        ListWeightEntriesCommand(
            user_id=current_user_id,
            limit=effective_limit,
            cursor=cursor,
        )
    )

    return WeightEntryListResponse(
        items=[WeightEntryResponse.model_validate(e) for e in page.items],
        next_cursor=page.next_cursor,
    )


# ── GET /weight-entries/{entry_id} ────────────────────────────────────────────


@router.get(
    "/{entry_id}",
    status_code=status.HTTP_200_OK,
    response_model=WeightEntryResponse,
    summary="Get a single weight entry (FR-W-5)",
)
def get_weight_entry(
    entry_id: int,
    session: Session = Depends(get_db_session),
    current_user_id: int = Depends(get_current_user_id),
) -> WeightEntryResponse:
    """Retrieve a single weight entry by ID for the authenticated user.

    Args:
        entry_id: The entry primary key.
        session: The active database session.
        current_user_id: The authenticated user's ID.

    Returns:
        The matching weight entry.

    Raises:
        HTTPException: 404 when the entry does not exist or belongs to another user.
    """
    repo = _weight_repo(session)
    uc = GetWeightEntry(weight_repo=repo)

    try:
        entry = uc.execute(GetWeightEntryCommand(user_id=current_user_id, entry_id=entry_id))
    except WeightEntryNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Weight entry not found.",
        ) from exc

    return WeightEntryResponse.model_validate(entry)


# ── PUT /weight-entries/{entry_id} ────────────────────────────────────────────


@router.put(
    "/{entry_id}",
    status_code=status.HTTP_200_OK,
    response_model=WeightEntryResponse,
    summary="Update a weight entry (FR-W-3)",
)
@limiter.limit("30/minute")
def update_weight_entry(
    request: Request,
    entry_id: int,
    payload: WeightEntryRequest,
    session: Session = Depends(get_db_session),
    current_user_id: int = Depends(get_current_user_id),
) -> WeightEntryResponse:
    """Update a weight entry owned by the authenticated user.

    Args:
        request: The incoming HTTP request (required by slowapi).
        entry_id: The entry primary key.
        payload: Validated request body.
        session: The active database session.
        current_user_id: The authenticated user's ID.

    Returns:
        The updated weight entry.

    Raises:
        HTTPException: 404 when the entry does not exist or belongs to another user.
        HTTPException: 409 when the new date conflicts with another active entry.
        HTTPException: 422 when the observation date is in the future.
    """
    repo = _weight_repo(session)
    uc = UpdateWeightEntry(weight_repo=repo)

    try:
        entry = uc.execute(
            UpdateWeightEntryCommand(
                user_id=current_user_id,
                entry_id=entry_id,
                weight_value=payload.weight_value,
                weight_unit=payload.weight_unit,
                observation_date=payload.observation_date,
                notes=payload.notes,
            )
        )
    except WeightEntryNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Weight entry not found.",
        ) from exc
    except DuplicateObservationDateError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An entry already exists for this date.",
        ) from exc
    except ObservationDateInFutureError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Observation date cannot be in the future.",
        ) from exc

    logger.info("weight_entry_updated", entry_id=entry.entry_id, user_id=current_user_id)
    return WeightEntryResponse.model_validate(entry)


# ── DELETE /weight-entries/{entry_id} ────────────────────────────────────────


@router.delete(
    "/{entry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft-delete a weight entry (FR-W-4)",
)
@limiter.limit("30/minute")
def delete_weight_entry(
    request: Request,
    entry_id: int,
    session: Session = Depends(get_db_session),
    current_user_id: int = Depends(get_current_user_id),
) -> Response:
    """Soft-delete a weight entry owned by the authenticated user.

    Idempotent: re-deleting an already-deleted entry returns 204.

    Args:
        request: The incoming HTTP request (required by slowapi).
        entry_id: The entry primary key.
        session: The active database session.
        current_user_id: The authenticated user's ID.

    Returns:
        Empty 204 response on success.

    Raises:
        HTTPException: 404 when the entry does not exist or belongs to another user.
    """
    repo = _weight_repo(session)
    uc = DeleteWeightEntry(weight_repo=repo)

    try:
        uc.execute(DeleteWeightEntryCommand(user_id=current_user_id, entry_id=entry_id))
    except WeightEntryNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Weight entry not found.",
        ) from exc

    logger.info("weight_entry_deleted", entry_id=entry_id, user_id=current_user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
