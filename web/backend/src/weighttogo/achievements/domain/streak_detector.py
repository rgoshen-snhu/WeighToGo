"""Streak detection algorithm for the achievements bounded context.

Pure function — zero framework imports.  Algorithmic showcase for the CS 499
Milestone Three rubric (FR-Ach-3).

Algorithm: build a sorted list from the set-backed observation dates (duplicate
same-day entries collapse to one calendar day via set semantics), then a single
linear scan tracks the longest run of consecutive calendar days.  Each streak
threshold whose longest run is met is emitted exactly once.

Time complexity:  O(n log n) for the sort + O(n) for the scan, n = distinct days.
Space complexity: O(n) for the sorted list and output.  Set membership is O(1).
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from typing import NamedTuple

STREAK_THRESHOLDS: tuple[int, ...] = (7, 30)


class Streak(NamedTuple):
    """A detected consecutive-day logging streak.

    Attributes:
        length_days: The streak threshold met (7 or 30).
    """

    length_days: int


def _longest_consecutive_run(observation_dates: frozenset[date], today: date) -> int:
    """Return the length of the longest run of consecutive calendar days.

    Future-dated entries (after *today*) are ignored defensively.  Duplicate
    same-day entries are already collapsed by the ``set`` input.

    Args:
        observation_dates: Distinct observation dates (set collapses dupes).
        today: Upper bound; dates after this are ignored.

    Returns:
        The longest consecutive-day run length (0 when no valid dates).
    """
    days = sorted(d for d in observation_dates if d <= today)
    if not days:
        return 0

    longest = 1
    current = 1
    one_day = timedelta(days=1)
    for prev, curr in zip(days, days[1:], strict=False):
        if curr == prev + one_day:
            current += 1
            longest = max(longest, current)
        else:
            current = 1
    return longest


def detect_streaks(observation_dates: frozenset[date], today: date) -> list[Streak]:
    """Return streak thresholds (7, 30) met by the user's logging history.

    A threshold T is met when the longest run of consecutive calendar days in
    *observation_dates* (on or before *today*) is at least T.  Duplicate
    same-day entries collapse to one calendar day because the input is a set.

    Args:
        observation_dates: Distinct dates the user logged a weight entry.
        today: The current date; future-dated entries are ignored.

    Returns:
        List of ``Streak`` for each threshold met, ascending by length.
        Empty when no threshold is met.
    """
    longest = _longest_consecutive_run(observation_dates, today)
    return [Streak(length_days=t) for t in STREAK_THRESHOLDS if longest >= t]


def streak_threshold_decimal(streak: Streak) -> Decimal:
    """Return the streak length as a ``Decimal`` for the achievement threshold.

    Args:
        streak: The detected streak.

    Returns:
        The threshold as ``Decimal`` (matches the achievements ``threshold`` column).
    """
    return Decimal(streak.length_days)
