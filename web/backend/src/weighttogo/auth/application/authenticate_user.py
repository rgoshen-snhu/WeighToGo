"""AuthenticateUser use case.

Verifies credentials against the stored hash, enforces account lockout
(SRS §NFR-S-6, §FR-A-2), and returns the authenticated ``User`` entity.

All failure paths raise the *same* ``InvalidCredentialsError`` to prevent
username enumeration (SRS §FR-A-9, §NFR-S-7).  The only exception is
``AccountLockedError``, which is distinct because the frontend must be able
to show a user-friendly lockout message without leaking credential details.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Protocol

from weighttogo.auth.domain.entities import User
from weighttogo.auth.domain.exceptions import AccountLockedError, InvalidCredentialsError
from weighttogo.auth.domain.ports import IUserRepository


class IPasswordAdapter(Protocol):
    """Minimal port for password verification."""

    def verify(self, plaintext: str, hashed: str) -> bool:
        """Return ``True`` if *plaintext* matches *hashed*."""
        ...


@dataclass(frozen=True)
class AuthenticateUserCommand:
    """Input for the ``AuthenticateUser`` use case.

    Attributes:
        email: The email address supplied by the login form.
        password: The plain-text password supplied by the login form.
    """

    email: str
    password: str


class AuthenticateUser:
    """Verify login credentials and return the authenticated user.

    Raises:
        InvalidCredentialsError: For any credential mismatch, unknown email,
            or inactive account (generic — no enumeration).
        AccountLockedError: When the account is in an active lockout period.

    Args:
        user_repo: Persistence port for ``User`` entities.
        password_adapter: Port for constant-time password comparison.
        max_attempts: Number of consecutive failures before lockout.
        lockout_minutes: Initial lockout duration in minutes.  Subsequent
            lockouts use exponential back-off capped at 24 hours.
    """

    _MAX_LOCKOUT_HOURS: int = 24

    def __init__(
        self,
        user_repo: IUserRepository,
        password_adapter: IPasswordAdapter,
        max_attempts: int = 5,
        lockout_minutes: int = 15,
    ) -> None:
        """Initialise the use case with its required dependencies."""
        self._user_repo = user_repo
        self._password_adapter = password_adapter
        self._max_attempts = max_attempts
        self._lockout_minutes = lockout_minutes

    def execute(self, cmd: AuthenticateUserCommand) -> User:
        """Authenticate *cmd* and return the user on success.

        Args:
            cmd: The login command with email and password.

        Returns:
            The authenticated ``User`` entity with its failure counter reset.

        Raises:
            InvalidCredentialsError: On any credential failure or inactive account.
            AccountLockedError: When the account lockout is still active.
        """
        user = self._user_repo.get_by_email(cmd.email)

        # --- Gate: account existence check using constant-time path ----------
        # We still call the hash verify against a dummy if no user is found so
        # the response time is indistinguishable (timing-safe enumeration guard).
        if user is None or not user.is_active:
            # Perform a dummy verify to keep response time indistinguishable
            # (timing-safe enumeration guard — SRS §FR-A-9, §NFR-S-7).
            _dummy = "$2b$12$dummyhashfortimingxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
            self._password_adapter.verify(cmd.password, _dummy)
            raise InvalidCredentialsError()

        # --- Gate: lockout check ---------------------------------------------
        if user.is_locked():
            raise AccountLockedError(locked_until=user.locked_until)  # type: ignore[arg-type]

        # --- Verify credentials ----------------------------------------------
        if not self._password_adapter.verify(cmd.password, user.hashed_password):
            user.record_failed_login()
            if user.failed_login_count >= self._max_attempts:
                lockout_duration = self._compute_lockout_duration(user.failed_login_count)
                user.locked_until = datetime.now(UTC) + lockout_duration
            self._user_repo.save(user)
            raise InvalidCredentialsError()

        # --- Success: reset failure tracking ---------------------------------
        user.reset_failed_logins()
        user.last_login_at = datetime.now(UTC)
        self._user_repo.save(user)
        return user

    def _compute_lockout_duration(self, failed_count: int) -> timedelta:
        """Compute an exponential back-off lockout duration capped at 24 hours.

        First lockout: ``lockout_minutes``.
        Subsequent: ``lockout_minutes * 2^(lockout_cycle - 1)``, capped.

        Args:
            failed_count: The total consecutive failed attempts including the
                one just recorded.

        Returns:
            A ``timedelta`` representing the lockout window.
        """
        # Number of times we've hit the threshold (1-based)
        cycle = max(1, (failed_count - self._max_attempts) // self._max_attempts + 1)
        minutes = self._lockout_minutes * (2 ** (cycle - 1))
        capped_minutes = min(minutes, self._MAX_LOCKOUT_HOURS * 60)
        return timedelta(minutes=capped_minutes)
