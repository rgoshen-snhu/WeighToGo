"""Integration tests for /api/v1/goals endpoints."""

from __future__ import annotations

from datetime import date
from typing import Any, cast

import pytest
from fastapi.testclient import TestClient

# ── Helpers ───────────────────────────────────────────────────────────────────


def _register_and_login(client: TestClient, email: str = "goals@example.com") -> None:
    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "ValidPass123!",
            "display_name": "Goals Tester",
        },
    )


def _valid_goal(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "target_value": 150.0,
        "target_unit": "lbs",
        "start_value": 200.0,
        "goal_type": "lose",
        "target_date": None,
    }
    base.update(overrides)
    return base


def _create_goal(client: TestClient, **overrides: Any) -> dict[str, Any]:
    resp = client.post("/api/v1/goals", json=_valid_goal(**overrides))
    assert resp.status_code == 201, resp.json()
    return cast(dict[str, Any], resp.json())


# ── Auth guard (401) ──────────────────────────────────────────────────────────


def test_create_goal_requires_auth(client: TestClient) -> None:
    resp = client.post("/api/v1/goals", json=_valid_goal())
    assert resp.status_code == 401


def test_get_active_goal_requires_auth(client: TestClient) -> None:
    resp = client.get("/api/v1/goals/active")
    assert resp.status_code == 401


def test_list_goals_requires_auth(client: TestClient) -> None:
    resp = client.get("/api/v1/goals")
    assert resp.status_code == 401


def test_update_goal_requires_auth(client: TestClient) -> None:
    resp = client.put("/api/v1/goals/1", json={"target_value": 145.0})
    assert resp.status_code == 401


def test_delete_goal_requires_auth(client: TestClient) -> None:
    resp = client.delete("/api/v1/goals/1")
    assert resp.status_code == 401


# ── Create (201 / 409) ────────────────────────────────────────────────────────


def test_create_goal_returns_201_with_body(client: TestClient) -> None:
    _register_and_login(client)
    resp = client.post("/api/v1/goals", json=_valid_goal())
    assert resp.status_code == 201
    data = resp.json()
    assert data["target_value"] == 150.0
    assert data["goal_type"] == "lose"
    assert "goal_id" in data


def test_create_second_active_goal_returns_409(client: TestClient) -> None:
    _register_and_login(client)
    client.post("/api/v1/goals", json=_valid_goal())
    resp = client.post("/api/v1/goals", json=_valid_goal())
    assert resp.status_code == 409


# ── GET /active ───────────────────────────────────────────────────────────────


def test_get_active_goal_null_when_none(client: TestClient) -> None:
    _register_and_login(client)
    resp = client.get("/api/v1/goals/active")
    assert resp.status_code == 200
    data = resp.json()
    assert data["goal"] is None
    assert data["progress_percent"] is None


def test_get_active_goal_with_no_entries_has_null_progress(client: TestClient) -> None:
    _register_and_login(client)
    _create_goal(client)
    resp = client.get("/api/v1/goals/active")
    assert resp.status_code == 200
    data = resp.json()
    assert data["goal"] is not None
    assert data["progress_percent"] is None


def test_get_active_goal_with_weight_entry_computes_progress(client: TestClient) -> None:
    _register_and_login(client)
    _create_goal(client)
    # Create a weight entry at the halfway point (175 lbs)
    client.post(
        "/api/v1/weight-entries",
        json={
            "weight_value": 175.0,
            "weight_unit": "lbs",
            "observation_date": date.today().isoformat(),
            "notes": None,
        },
    )
    resp = client.get("/api/v1/goals/active")
    assert resp.status_code == 200
    data = resp.json()
    assert data["goal"] is not None
    assert data["progress_percent"] == pytest.approx(50.0, abs=0.5)


# ── GET /goals (list) ─────────────────────────────────────────────────────────


def test_list_goals_returns_empty_when_none(client: TestClient) -> None:
    _register_and_login(client)
    resp = client.get("/api/v1/goals")
    assert resp.status_code == 200
    assert resp.json()["goals"] == []


def test_list_goals_returns_created_goal(client: TestClient) -> None:
    _register_and_login(client)
    _create_goal(client)
    resp = client.get("/api/v1/goals")
    assert resp.status_code == 200
    assert len(resp.json()["goals"]) == 1


def test_list_goals_history_excludes_active(client: TestClient) -> None:
    _register_and_login(client, "goal-history@example.com")
    # Create then abandon one goal (becomes past), then create an active one.
    first = _create_goal(client)
    client.delete(f"/api/v1/goals/{first['goal_id']}")
    _create_goal(client)  # new active goal

    # Default list returns both.
    all_resp = client.get("/api/v1/goals")
    assert all_resp.status_code == 200
    assert len(all_resp.json()["goals"]) == 2

    # History list returns only the abandoned (non-active) goal.
    hist_resp = client.get("/api/v1/goals?history=true")
    assert hist_resp.status_code == 200
    hist = hist_resp.json()["goals"]
    assert len(hist) == 1
    assert hist[0]["is_active"] is False
    assert hist[0]["goal_id"] == first["goal_id"]


# ── PUT /goals/{goal_id} ──────────────────────────────────────────────────────


def test_update_goal_returns_200_with_new_values(client: TestClient) -> None:
    _register_and_login(client)
    goal = _create_goal(client)
    resp = client.put(
        f"/api/v1/goals/{goal['goal_id']}",
        json={"target_value": 145.0, "target_date": None},
    )
    assert resp.status_code == 200
    assert resp.json()["target_value"] == 145.0


def test_update_goal_returns_404_when_not_found(client: TestClient) -> None:
    _register_and_login(client)
    resp = client.put("/api/v1/goals/99999", json={"target_value": 145.0, "target_date": None})
    assert resp.status_code == 404


# ── DELETE /goals/{goal_id} ───────────────────────────────────────────────────


def test_delete_goal_returns_204(client: TestClient) -> None:
    _register_and_login(client)
    goal = _create_goal(client)
    resp = client.delete(f"/api/v1/goals/{goal['goal_id']}")
    assert resp.status_code == 204


def test_delete_goal_returns_404_when_not_found(client: TestClient) -> None:
    _register_and_login(client)
    resp = client.delete("/api/v1/goals/99999")
    assert resp.status_code == 404


def test_delete_goal_allows_new_active_goal_after_abandon(client: TestClient) -> None:
    _register_and_login(client)
    goal = _create_goal(client)
    client.delete(f"/api/v1/goals/{goal['goal_id']}")
    resp = client.post("/api/v1/goals", json=_valid_goal())
    assert resp.status_code == 201


# ── IDOR — user B cannot access user A's goal ─────────────────────────────────


def test_update_goal_returns_409_when_goal_is_abandoned(client: TestClient) -> None:
    _register_and_login(client)
    goal = _create_goal(client)
    client.delete(f"/api/v1/goals/{goal['goal_id']}")
    resp = client.put(
        f"/api/v1/goals/{goal['goal_id']}",
        json={"target_value": 145.0, "target_date": None},
    )
    assert resp.status_code == 409


def test_update_goal_returns_422_when_lose_goal_target_exceeds_start(client: TestClient) -> None:
    _register_and_login(client)
    goal = _create_goal(client, start_value=200.0, target_value=150.0, goal_type="lose")
    resp = client.put(
        f"/api/v1/goals/{goal['goal_id']}",
        json={"target_value": 210.0, "target_date": None},
    )
    assert resp.status_code == 422


def test_update_goal_idor_returns_404(client: TestClient) -> None:
    # User A creates a goal
    _register_and_login(client, email="user-a@example.com")
    goal = _create_goal(client)
    goal_id = goal["goal_id"]

    # Log out by registering user B (new TestClient session shares cookies
    # but /register replaces the auth session)
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "user-b@example.com",
            "password": "ValidPass123!",
            "display_name": "User B",
        },
    )
    # User B tries to update user A's goal → must get 404 (not 403)
    resp = client.put(
        f"/api/v1/goals/{goal_id}",
        json={"target_value": 145.0, "target_date": None},
    )
    assert resp.status_code == 404


def test_delete_goal_idor_returns_404(client: TestClient) -> None:
    # User A creates a goal
    _register_and_login(client, email="user-c@example.com")
    goal = _create_goal(client)
    goal_id = goal["goal_id"]

    # Log in as user D
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "user-d@example.com",
            "password": "ValidPass123!",
            "display_name": "User D",
        },
    )
    resp = client.delete(f"/api/v1/goals/{goal_id}")
    assert resp.status_code == 404
