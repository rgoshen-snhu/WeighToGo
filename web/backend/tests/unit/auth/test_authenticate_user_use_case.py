"""Unit tests for the AuthenticateUser use case."""

from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock

import pytest

from weighttogo.auth.application.authenticate_user import AuthenticateUser, AuthenticateUserCommand
from weighttogo.auth.domain.entities import User
from weighttogo.auth.domain.exceptions import AccountLockedError, InvalidCredentialsError


def _make_user(
    failed_login_count: int = 0,
    locked_until: datetime | None = None,
    is_active: bool = True,
) -> User:
    return User(
        user_id=1,
        email="user@example.com",
        hashed_password="$2b$12$fakehash",
        display_name="Test User",
        is_active=is_active,
        failed_login_count=failed_login_count,
        locked_until=locked_until,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


def _make_repo(user: User | None) -> MagicMock:
    repo = MagicMock()
    repo.get_by_email.return_value = user
    repo.save.side_effect = lambda u: u
    return repo


def _make_password_adapter(matches: bool = True) -> MagicMock:
    adapter = MagicMock()
    adapter.verify.return_value = matches
    return adapter


def _make_use_case(repo: MagicMock, pw: MagicMock) -> AuthenticateUser:
    return AuthenticateUser(user_repo=repo, password_adapter=pw, max_attempts=5, lockout_minutes=15)


def test_authenticate_returns_user_on_valid_credentials() -> None:
    user = _make_user()
    repo = _make_repo(user)
    pw = _make_password_adapter(matches=True)
    use_case = _make_use_case(repo, pw)
    cmd = AuthenticateUserCommand(email="user@example.com", password="correct")

    result = use_case.execute(cmd)

    assert result.user_id == 1


def test_authenticate_resets_failed_login_counter_on_success() -> None:
    user = _make_user(failed_login_count=3)
    repo = _make_repo(user)
    pw = _make_password_adapter(matches=True)
    use_case = _make_use_case(repo, pw)
    cmd = AuthenticateUserCommand(email="user@example.com", password="correct")

    use_case.execute(cmd)

    # repo.save must be called, and the saved user must have counter reset
    saved_user: User = repo.save.call_args[0][0]
    assert saved_user.failed_login_count == 0
    assert saved_user.locked_until is None


def test_authenticate_raises_invalid_credentials_when_user_not_found() -> None:
    repo = _make_repo(user=None)
    pw = _make_password_adapter(matches=False)
    use_case = _make_use_case(repo, pw)
    cmd = AuthenticateUserCommand(email="nobody@example.com", password="irrelevant")

    with pytest.raises(InvalidCredentialsError):
        use_case.execute(cmd)


def test_authenticate_raises_invalid_credentials_when_password_wrong() -> None:
    user = _make_user()
    repo = _make_repo(user)
    pw = _make_password_adapter(matches=False)
    use_case = _make_use_case(repo, pw)
    cmd = AuthenticateUserCommand(email="user@example.com", password="wrong")

    with pytest.raises(InvalidCredentialsError):
        use_case.execute(cmd)


def test_authenticate_increments_failed_count_on_wrong_password() -> None:
    user = _make_user(failed_login_count=2)
    repo = _make_repo(user)
    pw = _make_password_adapter(matches=False)
    use_case = _make_use_case(repo, pw)
    cmd = AuthenticateUserCommand(email="user@example.com", password="wrong")

    with pytest.raises(InvalidCredentialsError):
        use_case.execute(cmd)

    saved_user: User = repo.save.call_args[0][0]
    assert saved_user.failed_login_count == 3


def test_authenticate_locks_account_after_max_attempts() -> None:
    user = _make_user(failed_login_count=4)  # one more failure → lock
    repo = _make_repo(user)
    pw = _make_password_adapter(matches=False)
    use_case = _make_use_case(repo, pw)
    cmd = AuthenticateUserCommand(email="user@example.com", password="wrong")

    with pytest.raises(InvalidCredentialsError):
        use_case.execute(cmd)

    saved_user: User = repo.save.call_args[0][0]
    assert saved_user.locked_until is not None


def test_authenticate_raises_account_locked_when_account_is_locked() -> None:
    locked_until = datetime.now(UTC) + timedelta(minutes=10)
    user = _make_user(locked_until=locked_until)
    repo = _make_repo(user)
    pw = _make_password_adapter(matches=True)
    use_case = _make_use_case(repo, pw)
    cmd = AuthenticateUserCommand(email="user@example.com", password="correct")

    with pytest.raises(AccountLockedError) as exc_info:
        use_case.execute(cmd)

    assert exc_info.value.locked_until == locked_until


def test_authenticate_raises_invalid_credentials_for_inactive_user() -> None:
    user = _make_user(is_active=False)
    repo = _make_repo(user)
    pw = _make_password_adapter(matches=True)
    use_case = _make_use_case(repo, pw)
    cmd = AuthenticateUserCommand(email="user@example.com", password="correct")

    # Inactive user → generic credentials error (no enumeration of account state)
    with pytest.raises(InvalidCredentialsError):
        use_case.execute(cmd)
