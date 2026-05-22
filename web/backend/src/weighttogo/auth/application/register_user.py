"""RegisterUser use case.

Validates that the email is unique, hashes the password, and persists a new
``User`` entity (SRS §FR-A-1, §NFR-S-2).

The use case has no knowledge of FastAPI, SQLAlchemy, or any HTTP concern.
It depends on the ``IUserRepository`` and ``IPasswordAdapter`` ports, both
of which are injected at construction time.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from weighttogo.auth.domain.entities import User
from weighttogo.auth.domain.exceptions import EmailAlreadyRegisteredError
from weighttogo.auth.domain.ports import IUserRepository


class IPasswordAdapter(Protocol):
    """Minimal port for the password-hashing capability."""

    def hash(self, plaintext: str) -> str:
        """Return a hash of *plaintext*."""
        ...

    def verify(self, plaintext: str, hashed: str) -> bool:
        """Return ``True`` if *plaintext* matches *hashed*."""
        ...


@dataclass(frozen=True)
class RegisterUserCommand:
    """Input for the ``RegisterUser`` use case.

    Attributes:
        email: The candidate email address (validated by the interface layer).
        password: The plain-text password (validated by the interface layer).
        display_name: The human-readable display name (2–50 characters).
    """

    email: str
    password: str
    display_name: str


class RegisterUser:
    """Create a new user account.

    Raises:
        EmailAlreadyRegisteredError: When the email is already in use.

    Args:
        user_repo: Persistence port for ``User`` entities.
        password_adapter: Port for hashing and verifying passwords.
    """

    def __init__(
        self,
        user_repo: IUserRepository,
        password_adapter: IPasswordAdapter,
    ) -> None:
        """Initialise the use case with its required dependencies."""
        self._user_repo = user_repo
        self._password_adapter = password_adapter

    def execute(self, cmd: RegisterUserCommand) -> User:
        """Run the registration flow for *cmd*.

        Args:
            cmd: The registration command with email, password, and display name.

        Returns:
            The newly persisted ``User`` entity with ``user_id`` populated.

        Raises:
            EmailAlreadyRegisteredError: When ``cmd.email`` is already registered.
        """
        if self._user_repo.get_by_email(cmd.email) is not None:
            raise EmailAlreadyRegisteredError()

        hashed = self._password_adapter.hash(cmd.password)
        user = User(
            user_id=None,
            email=cmd.email,
            hashed_password=hashed,
            display_name=cmd.display_name.strip(),
        )
        return self._user_repo.save(user)
