"""Domain exceptions for the authentication bounded context.

These exceptions express domain-layer failure modes. They have no dependency
on any framework and are raised by use cases, caught by the interface layer.
"""

from datetime import datetime


class InvalidCredentialsError(Exception):
    """Raised when login credentials do not match any active account.

    The message is intentionally generic — callers must NOT surface the
    original exception text to the user (see SRS §FR-A-9, §NFR-S-7).
    """


class AccountLockedError(Exception):
    """Raised when a login attempt is made against a locked account.

    Carries the datetime at which the lockout expires so callers can
    compute a ``Retry-After`` value without querying the database again.

    Args:
        locked_until: The UTC datetime when the lockout expires.
    """

    def __init__(self, locked_until: datetime) -> None:
        """Initialise with the datetime at which the lockout expires."""
        super().__init__("Account is temporarily locked.")
        self.locked_until = locked_until


class EmailAlreadyRegisteredError(Exception):
    """Raised when registration is attempted with an already-used email.

    The message is generic — callers MUST return 409 Conflict with a
    message that does not confirm whether the address is registered
    (see SRS §FR-A-1, §NFR-S-7).
    """
