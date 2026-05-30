"""Unit tests for the weekly rate-of-change pure domain function (FR-D-3)."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from weighttogo.weight_tracking.domain.rate_of_change import (
    RateEntry,
    weekly_rate_of_change,
)

_ANCHOR = date(2026, 5, 29)


def _entry(days_before_anchor: int, value: str, unit: str = "lbs") -> RateEntry:
    """Build a RateEntry *days_before_anchor* days before the fixed anchor."""
    return RateEntry(
        observation_date=_ANCHOR - timedelta(days=days_before_anchor),
        weight_value=Decimal(value),
        weight_unit=unit,
    )


def test_rate_is_none_for_empty_series() -> None:
    # ARRANGE
    entries: list[RateEntry] = []

    # ACT
    result = weekly_rate_of_change(entries)

    # ASSERT
    assert result.weekly_rate is None
    assert result.unit is None
    assert result.reason == "insufficient_data"


def test_rate_is_none_for_single_entry() -> None:
    # ARRANGE — a lone entry cannot fill the prior window
    entries = [_entry(0, "180.0")]

    # ACT
    result = weekly_rate_of_change(entries)

    # ASSERT
    assert result.weekly_rate is None
    assert result.reason == "insufficient_data"


def test_falling_trend_returns_negative_rate() -> None:
    # ARRANGE — recent window lighter than the prior window
    entries = [
        _entry(10, "190.0"),  # prior window
        _entry(8, "188.0"),  # prior window
        _entry(3, "182.0"),  # recent window
        _entry(0, "180.0"),  # recent window
    ]

    # ACT
    result = weekly_rate_of_change(entries)

    # ASSERT — recent mean 181, prior mean 189 -> -8 per week
    assert result.weekly_rate == Decimal("-8")
    assert result.unit == "lbs"
    assert result.reason is None


def test_rising_trend_returns_positive_rate() -> None:
    # ARRANGE — recent window heavier than the prior window
    entries = [
        _entry(9, "150.0"),  # prior window
        _entry(2, "154.0"),  # recent window
    ]

    # ACT
    result = weekly_rate_of_change(entries)

    # ASSERT
    assert result.weekly_rate == Decimal("4")
    assert result.unit == "lbs"


def test_flat_trend_returns_zero_rate() -> None:
    # ARRANGE — identical means in both windows
    entries = [
        _entry(9, "170.0"),  # prior window
        _entry(2, "170.0"),  # recent window
    ]

    # ACT
    result = weekly_rate_of_change(entries)

    # ASSERT — Decimal equality is exact, not a float comparison
    assert result.weekly_rate == Decimal("0")
    assert result.reason is None


def test_sparse_data_uses_available_points_in_each_window() -> None:
    # ARRANGE — one point per window, spanning the full 14-day range
    entries = [
        _entry(13, "200.0"),  # prior window
        _entry(1, "196.0"),  # recent window
    ]

    # ACT
    result = weekly_rate_of_change(entries)

    # ASSERT
    assert result.weekly_rate == Decimal("-4")


def test_all_entries_in_recent_window_only_is_insufficient() -> None:
    # ARRANGE — both entries fall in the recent window; prior window empty
    entries = [
        _entry(2, "180.0"),
        _entry(0, "179.0"),
    ]

    # ACT
    result = weekly_rate_of_change(entries)

    # ASSERT
    assert result.weekly_rate is None
    assert result.reason == "insufficient_data"
