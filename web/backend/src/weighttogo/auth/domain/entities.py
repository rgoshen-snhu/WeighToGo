"""Domain entities for the authentication bounded context.

Entities have identity and encapsulate domain behaviour. They have no
dependency on any framework or persistence technology.
"""

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class User:
    """A registered application user.

    Attributes:
        user_id: Surrogate primary key. ``None`` for unsaved users.
        email: RFC 5322 email address — the primary identifier (SRS ADR-0009).
        hashed_password: Bcrypt hash of the password. Never the plaintext.
        display_name: Human-readable name shown in the UI (2-50 chars).
        is_active: ``False`` after deactivation (soft-delete pattern).
        failed_login_count: Consecutive failed login attempts since last
            successful login or manual reset.
        locked_until: UTC datetime when the current lockout expires, or
            ``None`` if the account is not locked.
        created_at: UTC datetime the record was first persisted.
        updated_at: UTC datetime of the most recent update.
        last_login_at: UTC datetime of the most recent successful login.
    """

    user_id: int | None
    email: str
    hashed_password: str
    display_name: str
    is_active: bool = True
    failed_login_count: int = 0
    locked_until: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_login_at: datetime | None = None

    def is_locked(self) -> bool:
        """Return ``True`` if the account is currently locked.

        The lock is active when ``locked_until`` is set and is in the future.
        A past ``locked_until`` is treated as unlocked to avoid blocking
        users after the lockout period expires without a server restart.

        Returns:
            ``True`` when the account lockout is active; ``False`` otherwise.
        """
        if self.locked_until is None:
            return False
        return datetime.now(UTC) < self.locked_until

    def record_failed_login(self) -> None:
        """Increment the consecutive failed-login counter.

        Called by the ``AuthenticateUser`` use case on every failed attempt.
        The use case is responsible for checking thresholds and applying
        ``locked_until`` after the counter reaches the configured maximum.
        """
        self.failed_login_count += 1

    def reset_failed_logins(self) -> None:
        """Reset the failure counter and clear any active lockout.

        Called by the ``AuthenticateUser`` use case after a successful login
        to ensure the counter does not carry over to future attempts.
        """
        self.failed_login_count = 0
        self.locked_until = None


@dataclass
class RefreshToken:
    """A server-side refresh token record.

    Each row represents one issued refresh token. The token itself is never
    stored — only a bcrypt/SHA-256 hash. ``family_id`` links all tokens in a
    rotation chain so that replaying a revoked token triggers family-level
    revocation (SRS ADR-0013).

    Attributes:
        token_id: Surrogate primary key. ``None`` for unsaved tokens.
        user_id: FK to the owning user.
        token_hash: SHA-256 hex digest of the raw token bytes.
        family_id: UUID shared by all rotated tokens in the same session.
        expires_at: UTC datetime when the token expires.
        issued_at: UTC datetime the token was issued.
        revoked_at: UTC datetime the token was revoked, or ``None`` if live.
        replaced_by: FK to the successor token after rotation, or ``None``.
    """

    token_id: int | None
    user_id: int
    token_hash: str
    family_id: uuid.UUID
    expires_at: datetime
    issued_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    revoked_at: datetime | None = None
    replaced_by: int | None = None

    def is_valid(self) -> bool:
        """Return ``True`` if the token is neither revoked nor expired.

        Returns:
            ``True`` when the token can be used for a refresh; ``False`` when
            it has been revoked or has passed its expiry time.
        """
        if self.revoked_at is not None:
            return False
        return datetime.now(UTC) < self.expires_at

    def revoke(self) -> None:
        """Mark the token as revoked by setting ``revoked_at`` to now.

        Called by the ``RevokeSession`` and ``RefreshSession`` use cases.
        Once revoked a token must never be reused; callers should persist
        the updated entity immediately.
        """
        self.revoked_at = datetime.now(UTC)
