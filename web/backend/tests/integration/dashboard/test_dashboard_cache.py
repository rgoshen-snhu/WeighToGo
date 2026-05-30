"""Integration tests for dashboard summary TTL caching (NFR-P-5, ADR-0023)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from weighttogo.dashboard.interface.router import _dashboard_cache

# The process-global dashboard cache is reset before each test by the autouse
# reset inside the ``client`` fixture (tests/integration/conftest.py), so every
# test here starts with an empty cache.


def _register_and_login(client: TestClient, email: str = "cache@example.com") -> None:
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "ValidPass123!", "display_name": "Cache User"},
    )


def test_dashboard_read_populates_the_cache(client: TestClient) -> None:
    # ARRANGE — a registered user with one entry; cache starts empty
    _register_and_login(client)
    client.post(
        "/api/v1/weight-entries",
        json={"weight_value": 180.0, "weight_unit": "lbs", "observation_date": "2026-05-01"},
    )
    assert len(_dashboard_cache._store) == 0  # noqa: SLF001 — white-box state check

    # ACT — first read should populate the cache
    resp = client.get("/api/v1/dashboard/summary")

    # ASSERT — endpoint succeeds and a summary is now cached
    assert resp.status_code == 200
    assert len(_dashboard_cache._store) == 1  # noqa: SLF001
