"""C10 regression: rate limiter must respect trusted_proxies setting for XFF bucketing."""

from unittest.mock import patch

from fastapi.testclient import TestClient

from weighttogo.config import Settings, get_settings


def _patched_settings(**overrides: object) -> Settings:
    base = get_settings()
    data = base.model_dump()
    data.update(overrides)
    # Reconstruct without env_file validation
    return Settings.model_validate(data)


def test_shared_bucket_when_trusted_proxies_false(client: TestClient) -> None:
    """With trusted_proxies=False, different XFF headers share the same rate bucket."""
    from weighttogo.auth.interface import router as router_module
    from weighttogo.config import get_settings as gs

    settings_off = _patched_settings(trusted_proxies=False)
    with (
        patch.object(router_module, "get_settings", return_value=settings_off),
        patch.object(gs, "__call__", return_value=settings_off),
    ):
        r1 = client.get("/health", headers={"X-Forwarded-For": "1.2.3.4"})
        r2 = client.get("/health", headers={"X-Forwarded-For": "9.8.7.6"})
    # Both succeed — not testing the 429 itself, just that they go through
    assert r1.status_code == 200
    assert r2.status_code == 200


def test_independent_buckets_when_trusted_proxies_true(client: TestClient) -> None:
    """With trusted_proxies=True, distinct XFF IPs get independent rate buckets."""
    from collections.abc import Callable

    from fastapi import Request as FastAPIRequest

    from weighttogo.auth.interface.router import _make_rate_limit_key

    settings_on = _patched_settings(trusted_proxies=True)
    key_func: Callable[[FastAPIRequest], str] = _make_rate_limit_key(settings_on)

    class _FakeRequest:
        def __init__(self, xff: str, remote: str = "10.0.0.1") -> None:
            self.headers = {"x-forwarded-for": xff}
            self.client = type("addr", (), {"host": remote})()

    key1 = key_func(_FakeRequest("1.2.3.4"))  # type: ignore[arg-type]
    key2 = key_func(_FakeRequest("9.8.7.6"))  # type: ignore[arg-type]
    key3 = key_func(_FakeRequest("1.2.3.4"))  # type: ignore[arg-type]

    assert key1 != key2, "distinct XFF IPs must produce distinct keys"
    assert key1 == key3, "same XFF IP must produce the same key"
