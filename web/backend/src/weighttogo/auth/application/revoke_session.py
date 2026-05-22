"""RevokeSession use case.

Revokes the refresh token on logout.  The operation is idempotent — if the
token is not found, the request still succeeds with no error (SRS §FR-A-3).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from weighttogo.auth.domain.ports import IRefreshTokenRepository


class IJwtAdapter(Protocol):
    """Minimal port for token hashing."""

    def hash_token(self, raw_token: str) -> str:
        """Return the SHA-256 hex digest of *raw_token*."""
        ...


@dataclass(frozen=True)
class RevokeSessionCommand:
    """Input for the ``RevokeSession`` use case.

    Attributes:
        raw_refresh_token: The opaque refresh token value from the cookie.
    """

    raw_refresh_token: str


class RevokeSession:
    """Revoke the refresh token on logout.

    The operation is intentionally idempotent: a missing or already-revoked
    token is silently ignored so that clients that re-send a logout request
    receive a consistent response.

    Args:
        token_repo: Persistence port for ``RefreshToken`` entities.
    """

    def __init__(self, token_repo: IRefreshTokenRepository) -> None:
        """Initialise the use case with its required dependency."""
        self._token_repo = token_repo

    def execute(self, cmd: RevokeSessionCommand) -> None:
        """Revoke the token identified by *cmd.raw_refresh_token*.

        Args:
            cmd: Command carrying the raw refresh token from the cookie.
        """
        import hashlib

        token_hash = hashlib.sha256(cmd.raw_refresh_token.encode()).hexdigest()
        token = self._token_repo.get_by_hash(token_hash)
        if token is None:
            return

        token.revoke()
        self._token_repo.save(token)
