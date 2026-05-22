"""Unit tests for the RegisterUser use case."""

from datetime import UTC
from unittest.mock import MagicMock

import pytest

from weighttogo.auth.application.register_user import RegisterUser, RegisterUserCommand
from weighttogo.auth.domain.entities import User
from weighttogo.auth.domain.exceptions import EmailAlreadyRegisteredError


def _make_mock_repo(existing_user: User | None = None) -> MagicMock:
    repo = MagicMock()
    repo.get_by_email.return_value = existing_user
    repo.save.side_effect = lambda user: user
    return repo


def _make_mock_password_adapter() -> MagicMock:
    adapter = MagicMock()
    adapter.hash.return_value = "$2b$12$fakehash"
    return adapter


def test_register_user_creates_and_saves_new_user() -> None:
    # ARRANGE
    repo = _make_mock_repo(existing_user=None)
    password_adapter = _make_mock_password_adapter()
    use_case = RegisterUser(user_repo=repo, password_adapter=password_adapter)
    cmd = RegisterUserCommand(
        email="new@example.com",
        password="SecurePass1!",
        display_name="New User",
    )

    # ACT
    user = use_case.execute(cmd)

    # ASSERT
    repo.save.assert_called_once()
    assert user.email == "new@example.com"
    assert user.display_name == "New User"
    assert user.hashed_password == "$2b$12$fakehash"


def test_register_user_raises_when_email_already_exists() -> None:
    from datetime import datetime

    existing = User(
        user_id=1,
        email="taken@example.com",
        hashed_password="$2b$12$hash",
        display_name="Existing",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    repo = _make_mock_repo(existing_user=existing)
    password_adapter = _make_mock_password_adapter()
    use_case = RegisterUser(user_repo=repo, password_adapter=password_adapter)
    cmd = RegisterUserCommand(
        email="taken@example.com",
        password="SecurePass1!",
        display_name="Another",
    )

    with pytest.raises(EmailAlreadyRegisteredError):
        use_case.execute(cmd)


def test_register_user_hashes_password_before_saving() -> None:
    repo = _make_mock_repo(existing_user=None)
    password_adapter = _make_mock_password_adapter()
    use_case = RegisterUser(user_repo=repo, password_adapter=password_adapter)
    cmd = RegisterUserCommand(
        email="user@example.com",
        password="PlainPassword1!",
        display_name="User",
    )

    use_case.execute(cmd)

    # Password adapter must have been called with the plain password
    password_adapter.hash.assert_called_once_with("PlainPassword1!")
    # Saved user must NOT have the plain password
    saved_user: User = repo.save.call_args[0][0]
    assert saved_user.hashed_password != "PlainPassword1!"


def test_register_user_trims_display_name_whitespace() -> None:
    repo = _make_mock_repo(existing_user=None)
    password_adapter = _make_mock_password_adapter()
    use_case = RegisterUser(user_repo=repo, password_adapter=password_adapter)
    cmd = RegisterUserCommand(
        email="user@example.com",
        password="SecurePass1!",
        display_name="  Padded Name  ",
    )

    user = use_case.execute(cmd)

    assert user.display_name == "Padded Name"
