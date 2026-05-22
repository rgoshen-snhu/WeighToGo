"""Unit tests for the User domain entity."""

from datetime import UTC, datetime

from weighttogo.auth.domain.entities import User


def _make_user(**kwargs: object) -> User:
    defaults: dict[str, object] = {
        "user_id": 1,
        "email": "test@example.com",
        "hashed_password": "$2b$12$fakehash",
        "display_name": "Test User",
        "is_active": True,
        "failed_login_count": 0,
        "locked_until": None,
        "created_at": datetime(2026, 1, 1, tzinfo=UTC),
        "updated_at": datetime(2026, 1, 1, tzinfo=UTC),
    }
    defaults.update(kwargs)
    return User(**defaults)  # type: ignore[arg-type]


def test_user_entity_stores_email() -> None:
    user = _make_user()
    assert user.email == "test@example.com"


def test_user_is_locked_when_locked_until_is_future() -> None:
    from datetime import timedelta

    future = datetime.now(UTC) + timedelta(minutes=15)
    user = _make_user(locked_until=future)
    assert user.is_locked() is True


def test_user_is_not_locked_when_locked_until_is_none() -> None:
    user = _make_user(locked_until=None)
    assert user.is_locked() is False


def test_user_is_not_locked_when_locked_until_is_past() -> None:
    from datetime import timedelta

    past = datetime.now(UTC) - timedelta(minutes=1)
    user = _make_user(locked_until=past)
    assert user.is_locked() is False


def test_user_record_failed_login_increments_count() -> None:
    user = _make_user(failed_login_count=2)
    user.record_failed_login()
    assert user.failed_login_count == 3


def test_user_reset_failed_logins_clears_count_and_lockout() -> None:
    from datetime import timedelta

    future = datetime.now(UTC) + timedelta(minutes=15)
    user = _make_user(failed_login_count=5, locked_until=future)
    user.reset_failed_logins()
    assert user.failed_login_count == 0
    assert user.locked_until is None
