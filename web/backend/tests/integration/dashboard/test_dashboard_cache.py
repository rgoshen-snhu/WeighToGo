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


def test_creating_a_weight_entry_busts_the_dashboard_cache(client: TestClient) -> None:
    # ARRANGE — register, add one entry, prime the cache with a read
    _register_and_login(client)
    client.post(
        "/api/v1/weight-entries",
        json={"weight_value": 180.0, "weight_unit": "lbs", "observation_date": "2026-05-01"},
    )
    first = client.get("/api/v1/dashboard/summary")
    assert first.json()["total_entries"] == 1

    # ACT — add a second entry (must invalidate the cache), then re-read
    client.post(
        "/api/v1/weight-entries",
        json={"weight_value": 179.0, "weight_unit": "lbs", "observation_date": "2026-05-02"},
    )
    after = client.get("/api/v1/dashboard/summary")

    # ASSERT — cache was invalidated on create; fresh count returned (not stale 1)
    assert after.json()["total_entries"] == 2


def _create_goal(client: TestClient) -> int:
    resp = client.post(
        "/api/v1/goals",
        json={
            "target_value": 150.0,
            "target_unit": "lbs",
            "start_value": 200.0,
            "goal_type": "lose",
            "target_date": None,
        },
    )
    assert resp.status_code == 201, resp.json()
    return int(resp.json()["goal_id"])


def test_creating_a_goal_busts_the_dashboard_cache(client: TestClient) -> None:
    # ARRANGE — register, log a weight so the dashboard has data, prime the cache
    _register_and_login(client)
    client.post(
        "/api/v1/weight-entries",
        json={"weight_value": 180.0, "weight_unit": "lbs", "observation_date": "2026-05-01"},
    )
    first = client.get("/api/v1/dashboard/summary")
    assert first.json()["active_goal"] is None

    # ACT — create a goal (must invalidate), then re-read
    _create_goal(client)
    after = client.get("/api/v1/dashboard/summary")

    # ASSERT — fresh summary now reflects the active goal (not the stale null)
    assert after.json()["active_goal"] is not None


def test_updating_a_goal_busts_the_dashboard_cache(client: TestClient) -> None:
    # ARRANGE — register, create a goal, prime the cache with a read
    _register_and_login(client)
    goal_id = _create_goal(client)
    first = client.get("/api/v1/dashboard/summary")
    assert first.json()["active_goal"]["goal"]["target_value"] == 150.0

    # ACT — update the goal target (must invalidate), then re-read
    resp = client.put(f"/api/v1/goals/{goal_id}", json={"target_value": 140.0})
    assert resp.status_code == 200, resp.json()
    after = client.get("/api/v1/dashboard/summary")

    # ASSERT — fresh summary reflects the new target (not the stale 150)
    assert after.json()["active_goal"]["goal"]["target_value"] == 140.0


def test_deleting_a_goal_busts_the_dashboard_cache(client: TestClient) -> None:
    # ARRANGE — register, create a goal, prime the cache with a read
    _register_and_login(client)
    goal_id = _create_goal(client)
    first = client.get("/api/v1/dashboard/summary")
    assert first.json()["active_goal"] is not None

    # ACT — abandon the goal (must invalidate), then re-read
    resp = client.delete(f"/api/v1/goals/{goal_id}")
    assert resp.status_code == 204
    after = client.get("/api/v1/dashboard/summary")

    # ASSERT — fresh summary no longer shows an active goal (not the stale one)
    assert after.json()["active_goal"] is None
