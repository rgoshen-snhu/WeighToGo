"""IssueTokens use case.

Issues a JWT access token and a server-side refresh token record on
successful authentication (SRS §FR-A-2, §NFR-S-3, ADR-0013).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Protocol

from weighttogo.auth.domain.entities import RefreshToken
from weighttogo.auth.domain.ports import IRefreshTokenRepository


class IJwtAdapter(Protocol):
    """Minimal port for JWT and refresh token issuance."""

    def issue_access_token(self, user_id: int, ttl: timedelta) -> str:
        """Issue a signed JWT access token for *user_id*."""
        ...

    def issue_refresh_token(self) -> tuple[str, str]:
        """Return a ``(raw_token, token_hash)`` tuple."""
        ...


@dataclass(frozen=True)
class IssueTokensCommand:
    """Input for the ``IssueTokens`` use case.

    Attributes:
        user_id: The authenticated user's surrogate primary key.
    """

    user_id: int


@dataclass(frozen=True)
class TokenPair:
    """Output of the ``IssueTokens`` and ``RefreshSession`` use cases.

    Attributes:
        access_token: The signed JWT string for the HTTP-only cookie.
        raw_refresh_token: The opaque refresh token for the HTTP-only cookie.
            The hash counterpart is stored server-side; the raw value is never
            persisted.
    """

    access_token: str
    raw_refresh_token: str


class IssueTokens:
    """Issue an access token and a server-side refresh token record.

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

    def execute(self, cmd: IssueTokensCommand) -> TokenPair:
        """Issue a new token pair for *cmd.user_id*.

        Args:
            cmd: Command carrying the authenticated user's ID.

        Returns:
            A ``TokenPair`` with both tokens ready for cookie delivery.
        """
        access_token = self._jwt.issue_access_token(cmd.user_id, self._access_ttl)
        raw_refresh, refresh_hash = self._jwt.issue_refresh_token()

        refresh_record = RefreshToken(
            token_id=None,
            user_id=cmd.user_id,
            token_hash=refresh_hash,
            family_id=uuid.uuid4(),
            expires_at=datetime.now(UTC) + self._refresh_ttl,
        )
        self._token_repo.save(refresh_record)

        return TokenPair(access_token=access_token, raw_refresh_token=raw_refresh)
