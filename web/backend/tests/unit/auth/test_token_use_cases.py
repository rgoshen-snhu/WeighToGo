"""Unit tests for IssueTokens, RefreshSession, and RevokeSession use cases."""

import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock

import pytest

from weighttogo.auth.application.issue_tokens import IssueTokens, IssueTokensCommand, TokenPair
from weighttogo.auth.application.refresh_session import RefreshSession, RefreshSessionCommand
from weighttogo.auth.application.revoke_session import RevokeSession, RevokeSessionCommand
from weighttogo.auth.domain.entities import RefreshToken
from weighttogo.auth.domain.exceptions import InvalidCredentialsError

# ── Helpers ──────────────────────────────────────────────────────────────────


def _make_jwt_adapter(access_token: str = "access.jwt.token") -> MagicMock:
    adapter = MagicMock()
    adapter.issue_access_token.return_value = access_token
    adapter.issue_refresh_token.return_value = ("raw_refresh_token", "refresh_hash_abc123")
    adapter.hash_token.side_effect = lambda t: f"hash_{t}"
    return adapter


def _make_refresh_token(
    revoked: bool = False,
    expired: bool = False,
    family_id: uuid.UUID | None = None,
) -> RefreshToken:
    fid = family_id or uuid.uuid4()
    expires = datetime.now(UTC) + (timedelta(seconds=-1) if expired else timedelta(days=7))
    return RefreshToken(
        token_id=1,
        user_id=42,
        token_hash="refresh_hash_abc123",
        family_id=fid,
        expires_at=expires,
        issued_at=datetime.now(UTC),
        revoked_at=datetime.now(UTC) if revoked else None,
    )


def _make_issue_tokens(jwt_adapter: MagicMock, token_repo: MagicMock) -> IssueTokens:
    return IssueTokens(
        jwt_adapter=jwt_adapter, token_repo=token_repo, refresh_ttl_days=7, access_ttl_minutes=15
    )


def _make_refresh_session(jwt_adapter: MagicMock, token_repo: MagicMock) -> RefreshSession:
    return RefreshSession(
        jwt_adapter=jwt_adapter, token_repo=token_repo, refresh_ttl_days=7, access_ttl_minutes=15
    )


# ── IssueTokens ───────────────────────────────────────────────────────────────


def test_issue_tokens_returns_token_pair() -> None:
    jwt_adapter = _make_jwt_adapter()
    token_repo = MagicMock()
    token_repo.save.side_effect = lambda t: t
    use_case = _make_issue_tokens(jwt_adapter, token_repo)
    cmd = IssueTokensCommand(user_id=42)

    result = use_case.execute(cmd)

    assert isinstance(result, TokenPair)
    assert result.access_token == "access.jwt.token"
    assert result.raw_refresh_token == "raw_refresh_token"


def test_issue_tokens_saves_refresh_token_record() -> None:
    jwt_adapter = _make_jwt_adapter()
    token_repo = MagicMock()
    token_repo.save.side_effect = lambda t: t
    use_case = _make_issue_tokens(jwt_adapter, token_repo)
    cmd = IssueTokensCommand(user_id=42)

    use_case.execute(cmd)

    token_repo.save.assert_called_once()
    saved: RefreshToken = token_repo.save.call_args[0][0]
    assert saved.user_id == 42
    assert saved.token_hash == "refresh_hash_abc123"


# ── RefreshSession ────────────────────────────────────────────────────────────


def test_refresh_session_returns_new_token_pair() -> None:
    existing_token = _make_refresh_token()
    token_repo = MagicMock()
    token_repo.get_by_hash.return_value = existing_token
    token_repo.save.side_effect = lambda t: t
    jwt_adapter = _make_jwt_adapter()
    use_case = _make_refresh_session(jwt_adapter, token_repo)
    cmd = RefreshSessionCommand(raw_refresh_token="raw_token")

    result = use_case.execute(cmd)

    assert isinstance(result, TokenPair)


def test_refresh_session_revokes_old_token() -> None:
    existing_token = _make_refresh_token()
    token_repo = MagicMock()
    token_repo.get_by_hash.return_value = existing_token
    token_repo.save.side_effect = lambda t: t
    jwt_adapter = _make_jwt_adapter()
    use_case = _make_refresh_session(jwt_adapter, token_repo)
    cmd = RefreshSessionCommand(raw_refresh_token="raw_token")

    use_case.execute(cmd)

    assert existing_token.revoked_at is not None


def test_refresh_session_raises_on_revoked_token() -> None:
    revoked_token = _make_refresh_token(revoked=True)
    token_repo = MagicMock()
    token_repo.get_by_hash.return_value = revoked_token
    jwt_adapter = _make_jwt_adapter()
    use_case = _make_refresh_session(jwt_adapter, token_repo)
    cmd = RefreshSessionCommand(raw_refresh_token="raw_token")

    with pytest.raises(InvalidCredentialsError):
        use_case.execute(cmd)


def test_refresh_session_revokes_family_on_token_replay() -> None:
    """Replaying a revoked token must revoke the entire family (SRS ADR-0013)."""
    family = uuid.uuid4()
    revoked_token = _make_refresh_token(revoked=True, family_id=family)
    token_repo = MagicMock()
    token_repo.get_by_hash.return_value = revoked_token
    jwt_adapter = _make_jwt_adapter()
    use_case = _make_refresh_session(jwt_adapter, token_repo)
    cmd = RefreshSessionCommand(raw_refresh_token="raw_token")

    with pytest.raises(InvalidCredentialsError):
        use_case.execute(cmd)

    token_repo.revoke_family.assert_called_once_with(family)


def test_refresh_session_raises_when_token_not_found() -> None:
    token_repo = MagicMock()
    token_repo.get_by_hash.return_value = None
    jwt_adapter = _make_jwt_adapter()
    use_case = _make_refresh_session(jwt_adapter, token_repo)
    cmd = RefreshSessionCommand(raw_refresh_token="nonexistent")

    with pytest.raises(InvalidCredentialsError):
        use_case.execute(cmd)


# ── RevokeSession ─────────────────────────────────────────────────────────────


def test_revoke_session_revokes_refresh_token() -> None:
    existing_token = _make_refresh_token()
    token_repo = MagicMock()
    token_repo.get_by_hash.return_value = existing_token
    token_repo.save.side_effect = lambda t: t
    use_case = RevokeSession(token_repo=token_repo)
    cmd = RevokeSessionCommand(raw_refresh_token="raw_token")

    use_case.execute(cmd)

    assert existing_token.revoked_at is not None
    token_repo.save.assert_called_once()


def test_revoke_session_is_idempotent_when_token_not_found() -> None:
    token_repo = MagicMock()
    token_repo.get_by_hash.return_value = None
    use_case = RevokeSession(token_repo=token_repo)
    cmd = RevokeSessionCommand(raw_refresh_token="nonexistent")

    # Should not raise
    use_case.execute(cmd)
    token_repo.save.assert_not_called()
