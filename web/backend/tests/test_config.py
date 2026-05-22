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
    monkeypatch.chdir(tmp_path)
    get_settings.cache_clear()

    first = get_settings()
    second = get_settings()

    assert isinstance(first, Settings)
    assert first is second
