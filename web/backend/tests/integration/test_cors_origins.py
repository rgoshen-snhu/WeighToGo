"""C7 regression: CORS_ALLOWED_ORIGINS env var must actually govern allowed origins."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def cors_client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    """TestClient whose CORS middleware accepts https://example.com."""
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "https://example.com")

    # Re-import app with a fresh settings cache so the new env var takes effect.
    from weighttogo.config import get_settings

    get_settings.cache_clear()

    # Re-create the app with the patched settings
    import importlib

    import weighttogo.main as main_module

    importlib.reload(main_module)

    client = TestClient(main_module.app, raise_server_exceptions=True)
    yield client

    get_settings.cache_clear()
    importlib.reload(main_module)
    # Clear again: the reload calls _get_cors_origins() → get_settings(), which
    # re-caches settings while CORS_ALLOWED_ORIGINS is still patched.  Clearing
    # here ensures the next get_settings() call (after monkeypatch reverts the
    # env var) reconstructs from the correct environment.
    get_settings.cache_clear()


def test_cors_allows_configured_origin(cors_client: TestClient) -> None:
    """An origin listed in CORS_ALLOWED_ORIGINS must be reflected in OPTIONS response."""
    response = cors_client.options(
        "/health",
        headers={
            "Origin": "https://example.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.headers.get("access-control-allow-origin") == "https://example.com"


def test_cors_rejects_unconfigured_origin(cors_client: TestClient) -> None:
    """An origin NOT in CORS_ALLOWED_ORIGINS must not appear in the response."""
    response = cors_client.options(
        "/health",
        headers={
            "Origin": "https://evil.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.headers.get("access-control-allow-origin") != "https://evil.com"
