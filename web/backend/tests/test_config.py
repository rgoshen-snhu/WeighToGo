"""Tests for application settings."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from weighttogo.config import Settings, get_settings


def test_settings_defaults_environment_to_development(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.delenv("ENVIRONMENT", raising=False)
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://test:test@localhost:5432/test")
    monkeypatch.setenv("SECRET_KEY", "a" * 32)
    monkeypatch.chdir(tmp_path)

    settings = Settings()  # type: ignore[call-arg]

    assert settings.environment == "development"


def test_settings_raises_when_database_url_missing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """DATABASE_URL must be required — no default so misconfiguration is loud."""
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ValidationError):
        Settings()  # type: ignore[call-arg]


def test_get_settings_returns_a_cached_settings_instance(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://test:test@localhost:5432/test")
    monkeypatch.setenv("SECRET_KEY", "a" * 32)
    monkeypatch.chdir(tmp_path)
    get_settings.cache_clear()

    first = get_settings()
    second = get_settings()

    assert isinstance(first, Settings)
    assert first is second


def test_settings_auth_fields_have_correct_defaults(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Auth settings must have the defaults specified in SRS §12.5.1."""
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://test:test@localhost:5432/test")
    monkeypatch.setenv("SECRET_KEY", "a" * 32)
    monkeypatch.chdir(tmp_path)

    settings = Settings()  # type: ignore[call-arg]

    assert settings.access_token_expire_minutes == 15
    assert settings.refresh_token_expire_days == 7
    assert settings.max_login_attempts == 5
    assert settings.lockout_duration_minutes == 15


def test_settings_secret_key_is_required(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """SECRET_KEY must be required — no default prevents accidental plaintext keys."""
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://test:test@localhost:5432/test")
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ValidationError):
        Settings()  # type: ignore[call-arg]


def test_settings_secret_key_rejects_blank(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A blank SECRET_KEY must raise ValidationError at startup."""
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://test:test@localhost:5432/test")
    monkeypatch.setenv("SECRET_KEY", "")
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ValidationError):
        Settings()  # type: ignore[call-arg]


def test_settings_secret_key_rejects_whitespace_only(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A whitespace-only SECRET_KEY must raise ValidationError."""
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://test:test@localhost:5432/test")
    monkeypatch.setenv("SECRET_KEY", "   ")
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ValidationError):
        Settings()  # type: ignore[call-arg]


def test_settings_secret_key_rejects_short_value(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A SECRET_KEY shorter than 32 characters must raise ValidationError."""
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://test:test@localhost:5432/test")
    monkeypatch.setenv("SECRET_KEY", "a" * 31)
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ValidationError):
        Settings()  # type: ignore[call-arg]


def test_settings_secret_key_accepts_32_char_value(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A SECRET_KEY of exactly 32 characters must be accepted."""
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://test:test@localhost:5432/test")
    monkeypatch.setenv("SECRET_KEY", "a" * 32)
    monkeypatch.chdir(tmp_path)

    settings = Settings()  # type: ignore[call-arg]

    assert settings.secret_key.get_secret_value() == "a" * 32


def test_settings_cookie_secure_is_false_in_development(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """cookie_secure must be False in the development environment."""
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://test:test@localhost:5432/test")
    monkeypatch.setenv("SECRET_KEY", "a" * 32)
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.chdir(tmp_path)

    settings = Settings()  # type: ignore[call-arg]

    assert settings.cookie_secure is False


def test_settings_cookie_secure_is_true_in_production(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """cookie_secure must be True in the production environment."""
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://test:test@localhost:5432/test")
    monkeypatch.setenv("SECRET_KEY", "a" * 32)
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.chdir(tmp_path)

    settings = Settings()  # type: ignore[call-arg]

    assert settings.cookie_secure is True


def test_settings_rate_limit_enabled_defaults_to_true(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """rate_limit_enabled must default to True so production is always protected."""
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://test:test@localhost:5432/test")
    monkeypatch.setenv("SECRET_KEY", "a" * 32)
    monkeypatch.delenv("RATE_LIMIT_ENABLED", raising=False)
    monkeypatch.chdir(tmp_path)

    settings = Settings()  # type: ignore[call-arg]

    assert settings.rate_limit_enabled is True


def test_settings_rate_limit_enabled_false_when_env_var_set(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """RATE_LIMIT_ENABLED=false must propagate to rate_limit_enabled=False."""
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://test:test@localhost:5432/test")
    monkeypatch.setenv("SECRET_KEY", "a" * 32)
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "false")
    monkeypatch.chdir(tmp_path)

    settings = Settings()  # type: ignore[call-arg]

    assert settings.rate_limit_enabled is False
