"""Unit tests for the RefreshToken domain entity."""

import uuid
from datetime import UTC, datetime, timedelta

from weighttogo.auth.domain.entities import RefreshToken


def _make_token(**kwargs: object) -> RefreshToken:
    defaults: dict[str, object] = {
        "token_id": 1,
        "user_id": 42,
        "token_hash": "abc123hash",
        "family_id": uuid.uuid4(),
        "expires_at": datetime.now(UTC) + timedelta(days=7),
        "issued_at": datetime.now(UTC),
        "revoked_at": None,
        "replaced_by": None,
    }
    defaults.update(kwargs)
    return RefreshToken(**defaults)  # type: ignore[arg-type]


def test_refresh_token_is_valid_when_not_expired_and_not_revoked() -> None:
    token = _make_token()
    assert token.is_valid() is True


def test_refresh_token_is_invalid_when_revoked() -> None:
    now = datetime.now(UTC)
    token = _make_token(revoked_at=now)
    assert token.is_valid() is False


def test_refresh_token_is_invalid_when_expired() -> None:
    past = datetime.now(UTC) - timedelta(seconds=1)
    token = _make_token(expires_at=past)
    assert token.is_valid() is False


def test_refresh_token_revoke_sets_revoked_at() -> None:
    token = _make_token()
    assert token.revoked_at is None
    token.revoke()
    assert token.revoked_at is not None
