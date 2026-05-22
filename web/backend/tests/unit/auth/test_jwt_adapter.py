"""Unit tests for the JWT adapter."""

from datetime import timedelta

import pytest

from weighttogo.auth.infrastructure.jwt_adapter import JwtAdapter

_SECRET = "test-secret-key-that-is-at-least-32-bytes-long!"


def test_issue_access_token_returns_non_empty_string() -> None:
    adapter = JwtAdapter(secret_key=_SECRET, algorithm="HS256")
    token = adapter.issue_access_token(user_id=1, ttl=timedelta(minutes=15))
    assert isinstance(token, str)
    assert len(token) > 0


def test_verify_access_token_returns_user_id() -> None:
    adapter = JwtAdapter(secret_key=_SECRET, algorithm="HS256")
    token = adapter.issue_access_token(user_id=42, ttl=timedelta(minutes=15))
    user_id = adapter.verify_access_token(token)
    assert user_id == 42


def test_verify_access_token_raises_on_expired_token() -> None:
    from weighttogo.auth.infrastructure.jwt_adapter import TokenExpiredError

    adapter = JwtAdapter(secret_key=_SECRET, algorithm="HS256")
    token = adapter.issue_access_token(user_id=1, ttl=timedelta(seconds=-1))
    with pytest.raises(TokenExpiredError):
        adapter.verify_access_token(token)


def test_verify_access_token_raises_on_wrong_secret() -> None:
    from weighttogo.auth.infrastructure.jwt_adapter import InvalidTokenError

    adapter = JwtAdapter(secret_key=_SECRET, algorithm="HS256")
    bad_secret = "different-secret-key-at-least-32-chars!!"
    bad_adapter = JwtAdapter(secret_key=bad_secret, algorithm="HS256")
    token = adapter.issue_access_token(user_id=1, ttl=timedelta(minutes=15))
    with pytest.raises(InvalidTokenError):
        bad_adapter.verify_access_token(token)


def test_access_token_payload_contains_no_email_or_pii() -> None:
    """Tokens must contain only user_id and standard claims (SRS §NFR-S-3)."""
    import base64
    import json

    adapter = JwtAdapter(secret_key=_SECRET, algorithm="HS256")
    token = adapter.issue_access_token(user_id=99, ttl=timedelta(minutes=15))
    # Decode the payload (middle segment) without verification
    payload_b64 = token.split(".")[1]
    # Add padding
    padding = 4 - len(payload_b64) % 4
    payload_b64 += "=" * (padding % 4)
    payload = json.loads(base64.urlsafe_b64decode(payload_b64))
    # Must contain sub (user_id) and standard claims
    assert str(payload["sub"]) == "99"
    # Must NOT contain email, display_name, or any other PII field
    forbidden_keys = {"email", "display_name", "phone", "name"}
    assert not forbidden_keys.intersection(payload.keys())


def test_issue_refresh_token_returns_raw_token_and_hash() -> None:
    adapter = JwtAdapter(secret_key=_SECRET, algorithm="HS256")
    raw_token, token_hash = adapter.issue_refresh_token()
    assert isinstance(raw_token, str)
    assert isinstance(token_hash, str)
    assert len(raw_token) > 0
    assert len(token_hash) == 64  # SHA-256 hex digest


def test_two_refresh_tokens_are_different() -> None:
    adapter = JwtAdapter(secret_key=_SECRET, algorithm="HS256")
    t1, h1 = adapter.issue_refresh_token()
    t2, h2 = adapter.issue_refresh_token()
    assert t1 != t2
    assert h1 != h2


def test_hash_token_is_deterministic() -> None:
    adapter = JwtAdapter(secret_key=_SECRET, algorithm="HS256")
    raw, h1 = adapter.issue_refresh_token()
    h2 = adapter.hash_token(raw)
    assert h1 == h2
