"""Unit tests for auth domain exceptions."""

from datetime import UTC

from weighttogo.auth.domain.exceptions import (
    AccountLockedError,
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
)


def test_invalid_credentials_error_is_exception() -> None:
    # ARRANGE / ACT
    exc = InvalidCredentialsError()

    # ASSERT
    assert isinstance(exc, Exception)


def test_account_locked_error_carries_locked_until() -> None:
    from datetime import datetime

    # ARRANGE
    locked_until = datetime(2026, 6, 1, 12, 0, 0, tzinfo=UTC)

    # ACT
    exc = AccountLockedError(locked_until=locked_until)

    # ASSERT
    assert exc.locked_until == locked_until


def test_email_already_registered_error_is_exception() -> None:
    # ARRANGE / ACT
    exc = EmailAlreadyRegisteredError()

    # ASSERT
    assert isinstance(exc, Exception)
