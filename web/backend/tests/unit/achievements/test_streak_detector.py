"""Unit tests for detect_streaks pure function (FR-Ach-3).

Algorithm: O(n log n) sort + O(n) consecutive-run scan over set-backed dates.
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal


def test_detect_streaks_exact_seven_day_run_yields_seven() -> None:
    from weighttogo.achievements.domain.streak_detector import detect_streaks

    # ARRANGE: 7 consecutive days
    dates = frozenset(date(2026, 1, d) for d in range(1, 8))  # Jan 1..7
    # ACT
    result = detect_streaks(dates, today=date(2026, 1, 7))
    # ASSERT
    assert [s.length_days for s in result] == [7]


def test_detect_streaks_six_day_run_yields_nothing() -> None:
    from weighttogo.achievements.domain.streak_detector import detect_streaks

    # ARRANGE: Jan 1..6 — only 6 consecutive days
    dates = frozenset(date(2026, 1, d) for d in range(1, 7))
    # ACT
    result = detect_streaks(dates, today=date(2026, 1, 6))
    # ASSERT
    assert result == []


def test_detect_streaks_thirty_day_run_yields_both_seven_and_thirty() -> None:
    from weighttogo.achievements.domain.streak_detector import detect_streaks

    # ARRANGE: 30 consecutive days
    base = date(2026, 1, 1)
    dates = frozenset(base + timedelta(days=i) for i in range(30))
    # ACT
    result = detect_streaks(dates, today=base + timedelta(days=29))
    # ASSERT
    assert [s.length_days for s in result] == [7, 30]


def test_detect_streaks_broken_run_resets_and_uses_longest() -> None:
    from weighttogo.achievements.domain.streak_detector import detect_streaks

    # ARRANGE: 5-day run (Jan 1..5), gap, then 7-day run (Feb 1..7) → longest 7
    first = frozenset(date(2026, 1, d) for d in range(1, 6))
    second = frozenset(date(2026, 2, d) for d in range(1, 8))
    # ACT
    result = detect_streaks(first | second, today=date(2026, 2, 7))
    # ASSERT
    assert [s.length_days for s in result] == [7]


def test_detect_streaks_gap_prevents_threshold() -> None:
    from weighttogo.achievements.domain.streak_detector import detect_streaks

    # ARRANGE: Jan 1..4 then Jan 6..8 — max run is 4, no 7-day streak
    dates = frozenset(date(2026, 1, d) for d in (1, 2, 3, 4, 6, 7, 8))
    # ACT
    result = detect_streaks(dates, today=date(2026, 1, 8))
    # ASSERT
    assert result == []


def test_detect_streaks_collapses_to_calendar_days_via_set() -> None:
    from weighttogo.achievements.domain.streak_detector import detect_streaks

    # ARRANGE: seven distinct consecutive days; the set input is the contract
    # that collapses any duplicate same-day entries to one calendar day.
    dates = frozenset(date(2026, 3, d) for d in range(1, 8))
    # ACT
    result = detect_streaks(dates, today=date(2026, 3, 7))
    # ASSERT
    assert [s.length_days for s in result] == [7]


def test_detect_streaks_empty_input_yields_nothing() -> None:
    from weighttogo.achievements.domain.streak_detector import detect_streaks

    # ARRANGE / ACT
    result = detect_streaks(frozenset(), today=date(2026, 1, 1))
    # ASSERT
    assert result == []


def test_detect_streaks_ignores_future_dates() -> None:
    from weighttogo.achievements.domain.streak_detector import detect_streaks

    # ARRANGE: 7 consecutive days but all after today → ignored
    dates = frozenset(date(2026, 1, d) for d in range(10, 17))
    # ACT
    result = detect_streaks(dates, today=date(2026, 1, 1))
    # ASSERT
    assert result == []


def test_streak_threshold_decimal_returns_exact_decimal() -> None:
    from weighttogo.achievements.domain.streak_detector import (
        Streak,
        streak_threshold_decimal,
    )

    # ARRANGE / ACT / ASSERT
    assert streak_threshold_decimal(Streak(length_days=7)) == Decimal("7")
