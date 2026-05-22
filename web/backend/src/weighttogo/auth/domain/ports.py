"""Repository port interfaces for the authentication domain.

Ports (interfaces) are defined in the domain layer. Infrastructure adapters
implement them. Use cases depend only on these abstractions — never on
SQLAlchemy, psycopg, or any persistence detail.

Following the Hexagonal Architecture pattern (SRS §4.2.3, ADR-0012), the
domain knows *what* it needs from persistence but never *how* it is provided.
"""

from __future__ import annotations

import uuid
from typing import Protocol, runtime_checkable

from weighttogo.auth.domain.entities import RefreshToken, User


@runtime_checkable
class IUserRepository(Protocol):
    """Read/write port for the ``users`` table.

    All methods are synchronous at the domain level. The infrastructure
    adapter may use async internally but must present this interface.
    """

    def save(self, user: User) -> User:
        """Persist *user* and return it with ``user_id`` populated.

        Performs an INSERT for new entities (``user_id`` is ``None``) or
        an UPDATE for existing ones.

        Args:
            user: The entity to persist.

        Returns:
            The same entity, updated with the database-assigned ``user_id``
            and any server-side defaults (``created_at``, ``updated_at``).
        """
        ...

    def get_by_email(self, email: str) -> User | None:
        """Look up a user by email address.

        Email comparison is case-insensitive (CITEXT column in PostgreSQL).

        Args:
            email: The email address to look up.

        Returns:
            The matching ``User`` entity, or ``None`` if not found.
        """
        ...

    def get_by_id(self, user_id: int) -> User | None:
        """Look up a user by primary key.

        Args:
            user_id: The surrogate primary key.

        Returns:
            The matching ``User`` entity, or ``None`` if not found.
        """
        ...


@runtime_checkable
class IRefreshTokenRepository(Protocol):
    """Read/write port for the ``refresh_tokens`` table."""

    def save(self, token: RefreshToken) -> RefreshToken:
        """Persist *token* and return it with ``token_id`` populated.

        Args:
            token: The token entity to persist.

        Returns:
            The same entity with a database-assigned ``token_id``.
        """
        ...

    def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        """Look up a token by its hash value.

        Args:
            token_hash: The SHA-256 hex digest of the raw token.

        Returns:
            The matching ``RefreshToken`` entity, or ``None`` if not found.
        """
        ...

    def revoke_family(self, family_id: uuid.UUID) -> None:
        """Mark every token in *family_id* as revoked.

        Called when token replay is detected to invalidate the entire
        session lineage (SRS ADR-0013).

        Args:
            family_id: The UUID shared by all tokens in the rotation chain.
        """
        ...
