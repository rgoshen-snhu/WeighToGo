"""Pydantic request and response schemas for the weight-entries API endpoints.

Validates inputs at the API boundary before any domain logic runs (SRS §NFR-S-4).
Snake-case field names on both request and response schemas match the API payload
directly, eliminating a mapping layer on the frontend.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class WeightEntryRequest(BaseModel):
    """Request body for POST and PUT /api/v1/weight-entries (SRS §9.4).

    Attributes:
        weight_value: Positive decimal weight, ≤ 1500, two decimal places.
        weight_unit: Either ``'lbs'`` or ``'kg'``.
        observation_date: ISO-8601 date string; must not be in the future.
        notes: Optional free-text note, max 500 characters.
    """

    weight_value: Decimal = Field(gt=Decimal("0"), le=Decimal("1500"))
    weight_unit: Literal["lbs", "kg"]
    observation_date: date
    notes: str | None = Field(default=None, max_length=500)

    @field_validator("observation_date", mode="after")
    @classmethod
    def observation_date_not_future(cls, v: date) -> date:
        """Reject observation dates that are in the future."""
        if v > date.today():
            raise ValueError("Observation date cannot be in the future.")
        return v


class WeightEntryResponse(BaseModel):
    """Response body for a single weight entry (SRS §9.4).

    Attributes:
        entry_id: The surrogate primary key.
        weight_value: The recorded weight as a JSON number (SRS §3.2 micro-decision 1).
        weight_unit: The unit of measurement.
        observation_date: The date of the measurement.
        notes: Optional note.
        created_at: UTC timestamp of creation.
        updated_at: UTC timestamp of the most recent update.
    """

    entry_id: int
    weight_value: float
    weight_unit: str
    observation_date: date
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WeightEntryListResponse(BaseModel):
    """Paginated list response envelope for weight entries (SRS §9.4).

    Attributes:
        items: The weight entries in the current page.
        next_cursor: Opaque pagination token, or ``None`` when no further pages exist.
    """

    items: list[WeightEntryResponse]
    next_cursor: int | None
