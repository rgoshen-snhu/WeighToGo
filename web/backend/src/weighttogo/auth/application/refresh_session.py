"""RefreshSession use case.

Rotates the refresh token and issues a new access token.  Detects token
replay and revokes the entire token family on suspicion (SRS §FR-A-4,
ADR-0013).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Protocol

from weighttogo.auth.application.issue_tokens import TokenPair
from weighttogo.auth.domain.entities import RefreshToken
from weighttogo.auth.domain.exceptions import InvalidCredentialsError
from weighttogo.auth.domain.ports import IRefreshTokenRepository


class IJwtAdapter(Protocol):
    """Minimal port for JWT and refresh token issuance."""

    def issue_access_token(self, user_id: int, ttl: timedelta) -> str:
        """Issue a signed JWT access token."""
        ...

    def issue_refresh_token(self) -> tuple[str, str]:
        """Return a ``(raw_token, token_hash)`` tuple."""
        ...

    def hash_token(self, raw_token: str) -> str:
        """Return the SHA-256 hex digest of *raw_token*."""
        ...


@dataclass(frozen=True)
class RefreshSessionCommand:
    """Input for the ``RefreshSession`` use case.

    Attributes:
        raw_refresh_token: The opaque refresh token value from the cookie.
    """

    raw_refresh_token: str


class RefreshSession:
    """Rotate the refresh token and issue a new access token.

    Raises:
        InvalidCredentialsError: When the token is not found, revoked, or
            expired.  On replay (revoked token), the entire family is also
            revoked before raising.

    Args:
        jwt_adapter: Port for JWT and refresh token issuance.
        token_repo: Persistence port for ``RefreshToken`` entities.
        refresh_ttl_days: Refresh token time-to-live in days.
        access_ttl_minutes: Access token time-to-live in minutes.
    """

    def __init__(
        self,
        jwt_adapter: IJwtAdapter,
        token_repo: IRefreshTokenRepository,
        refresh_ttl_days: int = 7,
        access_ttl_minutes: int = 15,
    ) -> None:
        """Initialise the use case with its required dependencies."""
        self._jwt = jwt_adapter
        self._token_repo = token_repo
        self._refresh_ttl = timedelta(days=refresh_ttl_days)
        self._access_ttl = timedelta(minutes=access_ttl_minutes)

    def execute(self, cmd: RefreshSessionCommand) -> TokenPair:
        """Rotate the refresh token for *cmd.raw_refresh_token*.

        Args:
            cmd: Command carrying the raw refresh token from the cookie.

        Returns:
            A ``TokenPair`` with a new access token and new refresh token.

        Raises:
            InvalidCredentialsError: On any invalid or replayed refresh token.
        """
        token_hash = self._jwt.hash_token(cmd.raw_refresh_token)
        existing = self._token_repo.get_by_hash(token_hash)

        if existing is None:
            raise InvalidCredentialsError()

        # Replay detection: if already revoked, revoke the whole family
        if not existing.is_valid():
            if existing.revoked_at is not None:
                self._token_repo.revoke_family(existing.family_id)
            raise InvalidCredentialsError()

        # Rotate: revoke old token
        existing.revoke()
        self._token_repo.save(existing)

        # Issue new pair
        access_token = self._jwt.issue_access_token(existing.user_id, self._access_ttl)
        raw_refresh, refresh_hash = self._jwt.issue_refresh_token()

        new_record = RefreshToken(
            token_id=None,
            user_id=existing.user_id,
            token_hash=refresh_hash,
            family_id=existing.family_id,  # same family
            expires_at=datetime.now(UTC) + self._refresh_ttl,
        )
        self._token_repo.save(new_record)

        return TokenPair(access_token=access_token, raw_refresh_token=raw_refresh)
