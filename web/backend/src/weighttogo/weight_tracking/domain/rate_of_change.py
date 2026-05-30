"""Weekly rate-of-change algorithm for the weight_tracking bounded context.

Pure function — zero framework imports.  One of the CS 499 Milestone Three
algorithmic showcases.

The weekly rate of change is the difference between the moving average of the
most-recent 7-day window and the moving average of the immediately-prior 7-day
window.  Because the two windows are one week apart, that difference is already
expressed per week.

Time complexity:  O(w) over the entries that fall inside the two 7-day windows,
after the two indexed seeks performed by the caller's repository (ADR-0021).
Space complexity: O(1) — only running sums and counts are retained.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from typing import NamedTuple

WINDOW_DAYS = 7

INSUFFICIENT_DATA = "insufficient_data"


class RateEntry(NamedTuple):
    """Lightweight projection of the fields the rate algorithm needs.

    Defined here (not imported from the entity) so the algorithm stays a pure,
    framework-free function operating on a minimal value tuple.

    Attributes:
        observation_date: Calendar date of the measurement.
        weight_value: Recorded weight as a ``Decimal``.
        weight_unit: Either ``'lbs'`` or ``'kg'``.
    """

    observation_date: date
    weight_value: Decimal
    weight_unit: str


@dataclass(frozen=True)
class RateOfChange:
    """Value object describing the user's weekly rate of weight change.

    Attributes:
        weekly_rate: Signed weight change per week (recent mean minus prior
            mean), or ``None`` when there is not enough data to compute it.
        unit: The weight unit of ``weekly_rate``, or ``None`` when the rate is
            ``None``.
        reason: A short machine-readable reason when ``weekly_rate`` is
            ``None`` (e.g. ``'insufficient_data'``); ``None`` otherwise.
    """

    weekly_rate: Decimal | None
    unit: str | None
    reason: str | None


def _insufficient() -> RateOfChange:
    """Return the canonical insufficient-data result."""
    return RateOfChange(weekly_rate=None, unit=None, reason=INSUFFICIENT_DATA)


def weekly_rate_of_change(entries: Sequence[RateEntry]) -> RateOfChange:
    """Compute the weekly rate of weight change from a series of entries.

    The most-recent entry's date anchors a recent 7-day window
    ``(anchor - 7 days, anchor]`` and a prior 7-day window
    ``(anchor - 14 days, anchor - 7 days]``.  The rate is
    ``mean(recent) - mean(prior)``.  Both windows must contain at least one
    entry; otherwise the result is insufficient-data.

    All entries are expected to share a single weight unit; the caller is
    responsible for normalising mixed units before calling. The reported
    ``unit`` is taken from the first entry, which is therefore safe.

    Args:
        entries: Weight entries for one user, all in the same unit.  Order is
            not assumed; the function reads the maximum observation date as the
            anchor.

    Returns:
        A :class:`RateOfChange`.  ``weekly_rate`` is ``None`` with
        ``reason='insufficient_data'`` when either window is empty.
    """
    if not entries:
        return _insufficient()

    anchor = max(entry.observation_date for entry in entries)
    recent_floor = anchor - timedelta(days=WINDOW_DAYS)
    prior_floor = anchor - timedelta(days=2 * WINDOW_DAYS)

    recent_sum = Decimal("0")
    recent_count = 0
    prior_sum = Decimal("0")
    prior_count = 0

    for entry in entries:
        if recent_floor < entry.observation_date <= anchor:
            recent_sum += entry.weight_value
            recent_count += 1
        elif prior_floor < entry.observation_date <= recent_floor:
            prior_sum += entry.weight_value
            prior_count += 1

    if recent_count == 0 or prior_count == 0:
        return _insufficient()

    recent_mean = recent_sum / recent_count
    prior_mean = prior_sum / prior_count
    return RateOfChange(
        weekly_rate=recent_mean - prior_mean,
        unit=entries[0].weight_unit,
        reason=None,
    )
