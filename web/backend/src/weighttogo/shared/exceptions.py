"""Base domain exceptions for the Weigh to Go! backend.

All custom exceptions raised within domain or application layers must inherit
from DomainError so callers can catch the entire hierarchy with a single clause
while still being able to discriminate specific failure modes.
"""


class DomainError(Exception):
    """Base class for all domain exceptions."""


class ValidationError(DomainError):
    """Raised when domain validation fails."""


class NotFoundError(DomainError):
    """Raised when a requested resource does not exist."""


class ConflictError(DomainError):
    """Raised when an operation conflicts with existing state."""
