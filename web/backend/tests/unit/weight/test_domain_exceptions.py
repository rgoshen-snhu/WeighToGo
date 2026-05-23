"""Unit tests for weight_tracking domain exceptions (subtask 5)."""

from __future__ import annotations


def test_weight_entry_not_found_error_is_exception() -> None:
    from weighttogo.weight_tracking.domain.exceptions import WeightEntryNotFoundError

    exc = WeightEntryNotFoundError()
    assert isinstance(exc, Exception)


def test_duplicate_observation_date_error_is_exception() -> None:
    from weighttogo.weight_tracking.domain.exceptions import DuplicateObservationDateError

    exc = DuplicateObservationDateError()
    assert isinstance(exc, Exception)


def test_observation_date_in_future_error_is_exception() -> None:
    from weighttogo.weight_tracking.domain.exceptions import ObservationDateInFutureError

    exc = ObservationDateInFutureError()
    assert isinstance(exc, Exception)
