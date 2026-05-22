"""JWT issuance and verification adapter.

Uses python-jose with HS256 to issue and verify access tokens and to generate
opaque refresh tokens stored server-side (SRS §NFR-S-3, ADR-0013).

Access tokens contain *only* the user surrogate ID (``sub`` claim) and the
standard JWT claims (``iat``, ``exp``, ``jti``).  No email, display name, or
other PII appears in the token payload.

Refresh tokens are random 256-bit values.  The raw value is returned once to
the caller for cookie delivery; only its SHA-256 hex digest is stored in the
database so that a database breach does not immediately yield valid tokens.
"""

import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Any

from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError


class TokenType(StrEnum):
    """Distinguishes access tokens from any future token types."""

    ACCESS = "access"


class TokenExpiredError(Exception):
    """Raised when an access token has passed its ``exp`` claim."""


class InvalidTokenError(Exception):
    """Raised when a token cannot be decoded or fails signature verification."""


class JwtAdapter:
    """Adapter for JWT issuance and verification.

    Args:
        secret_key: The HMAC signing key (at least 32 random bytes).
        algorithm: The signing algorithm (must be ``'HS256'``).
    """

    def __init__(self, secret_key: str, algorithm: str = "HS256") -> None:
        """Initialise the adapter with the signing key and algorithm."""
        self._secret = secret_key
        self._algorithm = algorithm

    # ── Access tokens ─────────────────────────────────────────────────────────

    def issue_access_token(self, user_id: int, ttl: timedelta) -> str:
        """Issue a signed JWT access token for *user_id*.

        The payload contains only ``sub`` (user surrogate ID as a string),
        ``iat``, ``exp``, and ``jti``.  No PII is present (SRS §NFR-S-3).

        Args:
            user_id: The authenticated user's surrogate primary key.
            ttl: Token time-to-live as a ``timedelta``.

        Returns:
            A signed JWT string in compact serialisation format.
        """
        now = datetime.now(UTC)
        claims: dict[str, Any] = {
            "sub": str(user_id),
            "iat": now,
            "exp": now + ttl,
            "jti": secrets.token_hex(16),
            "typ": TokenType.ACCESS,
        }
        token: str = jwt.encode(claims, self._secret, algorithm=self._algorithm)
        return token

    def verify_access_token(self, token: str) -> int:
        """Decode and verify *token*, returning the user ID from ``sub``.

        Args:
            token: The compact JWT string from the cookie.

        Returns:
            The user surrogate ID extracted from the ``sub`` claim.

        Raises:
            TokenExpiredError: When the token's ``exp`` claim is in the past.
            InvalidTokenError: When the signature is invalid, the token is
                malformed, or any other verification failure occurs.
        """
        try:
            payload = jwt.decode(
                token,
                self._secret,
                algorithms=[self._algorithm],
                options={"require_exp": True},
            )
            return int(payload["sub"])
        except ExpiredSignatureError as exc:
            raise TokenExpiredError("Access token has expired.") from exc
        except JWTError as exc:
            raise InvalidTokenError("Token verification failed.") from exc

    # ── Refresh tokens ────────────────────────────────────────────────────────

    def issue_refresh_token(self) -> tuple[str, str]:
        """Generate a cryptographically random refresh token.

        Returns:
            A ``(raw_token, token_hash)`` tuple.  The raw token is placed in
            the HTTP-only cookie; the hash is stored in the database.
        """
        raw = secrets.token_hex(32)  # 256 bits of entropy
        return raw, self.hash_token(raw)

    def hash_token(self, raw_token: str) -> str:
        """Return the SHA-256 hex digest of *raw_token*.

        Args:
            raw_token: The opaque refresh token string.

        Returns:
            The 64-character lowercase hex digest.
        """
        return hashlib.sha256(raw_token.encode()).hexdigest()
