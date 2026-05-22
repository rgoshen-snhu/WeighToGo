"""Unit tests for the shared base domain exceptions module."""

import pytest

from weighttogo.shared.exceptions import (
    ConflictError,
    DomainError,
    NotFoundError,
    ValidationError,
)


def test_domain_error_is_a_base_exception() -> None:
    """DomainError must be a subclass of the built-in Exception."""
    assert issubclass(DomainError, Exception)


def test_domain_error_can_be_raised_and_caught() -> None:
    """DomainError must be raise-able and catch-able as DomainError."""
    with pytest.raises(DomainError):
        raise DomainError("something went wrong")


def test_validation_error_subclasses_domain_error() -> None:
    """ValidationError must inherit from DomainError."""
    assert issubclass(ValidationError, DomainError)


def test_not_found_error_subclasses_domain_error() -> None:
    """NotFoundError must inherit from DomainError."""
    assert issubclass(NotFoundError, DomainError)


def test_conflict_error_subclasses_domain_error() -> None:
    """ConflictError must inherit from DomainError."""
    assert issubclass(ConflictError, DomainError)


def test_specific_errors_can_be_caught_as_domain_error() -> None:
    """Specific exception types must be catch-able using the DomainError base."""
    with pytest.raises(DomainError):
        raise ValidationError("invalid weight value")

    with pytest.raises(DomainError):
        raise NotFoundError("weight entry not found")

    with pytest.raises(DomainError):
        raise ConflictError("entry already exists for this date")


def test_exception_message_is_preserved() -> None:
    """Exception message must be accessible via str()."""
    msg = "weight must be positive"
    exc = ValidationError(msg)
    assert str(exc) == msg
