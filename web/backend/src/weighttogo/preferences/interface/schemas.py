"""Pydantic request and response schemas for the preferences API endpoints."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, StrictBool, StrictStr

from weighttogo.preferences.domain.entities import PreferenceKey


class PreferencesResponse(BaseModel):
    """Response body for GET /api/v1/preferences and PUT /api/v1/preferences/{key}.

    All four preferences are always present (lazy defaults merged in the
    application layer before this schema is constructed).

    Attributes:
        weight_unit: Global weight-unit preference — 'lbs' or 'kg'.
        notify_achievement: Whether to show achievement alerts.
        notify_milestone: Whether to show milestone alerts.
        notify_streak: Whether to show streak alerts.
    """

    weight_unit: Literal["lbs", "kg"]
    notify_achievement: bool
    notify_milestone: bool
    notify_streak: bool


class UpdatePreferenceRequest(BaseModel):
    """Request body for PUT /api/v1/preferences/{key}.

    The domain normalises the value per key, so a heterogeneous type is
    accepted here (bool | str). Invalid values return 422.

    Attributes:
        value: The new preference value.
    """

    value: StrictBool | StrictStr


def preferences_response_from_dict(resolved: dict[PreferenceKey, str]) -> PreferencesResponse:
    """Map the application-layer resolved dict to a PreferencesResponse.

    Converts 'true'/'false' EAV strings to Python booleans.

    Args:
        resolved: Fully-resolved dict with all four PreferenceKey entries.

    Returns:
        A PreferencesResponse ready for serialisation.
    """
    return PreferencesResponse(
        weight_unit=resolved[PreferenceKey.WEIGHT_UNIT],  # type: ignore[arg-type]
        notify_achievement=resolved[PreferenceKey.NOTIFY_ACHIEVEMENT] == "true",
        notify_milestone=resolved[PreferenceKey.NOTIFY_MILESTONE] == "true",
        notify_streak=resolved[PreferenceKey.NOTIFY_STREAK] == "true",
    )
