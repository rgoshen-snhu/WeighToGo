"""Integration tests for GET /api/v1/dashboard/summary (subtask 21)."""

from __future__ import annotations

from datetime import date

import pytest
from fastapi.testclient import TestClient


def _register_and_login(client: TestClient, email: str = "dash@example.com") -> None:
    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "ValidPass123!",
            "display_name": "Dash User",
        },
    )


def test_dashboard_requires_auth(client: TestClient) -> None:
    resp = client.get("/api/v1/dashboard/summary")
    assert resp.status_code == 401


def test_dashboard_empty_user_shape(client: TestClient) -> None:
    _register_and_login(client)
    resp = client.get("/api/v1/dashboard/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert data["latest_entry"] is None
    assert data["total_entries"] == 0
    assert data["active_goal"] is None


def test_dashboard_populated_user_shape(client: TestClient) -> None:
    _register_and_login(client)
    client.post(
        "/api/v1/weight-entries",
        json={
            "weight_value": 175.5,
            "weight_unit": "lbs",
            "observation_date": date.today().isoformat(),
        },
    )
    resp = client.get("/api/v1/dashboard/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_entries"] == 1
    assert data["latest_entry"] is not None
    assert data["latest_entry"]["weight_value"] == 175.5


def test_dashboard_soft_deleted_entries_excluded(client: TestClient) -> None:
    _register_and_login(client)
    create_resp = client.post(
        "/api/v1/weight-entries",
        json={
            "weight_value": 175.5,
            "weight_unit": "lbs",
            "observation_date": date.today().isoformat(),
        },
    )
    entry_id = create_resp.json()["entry_id"]
    client.delete(f"/api/v1/weight-entries/{entry_id}")
    resp = client.get("/api/v1/dashboard/summary")
    data = resp.json()
    assert data["total_entries"] == 0
    assert data["latest_entry"] is None


def test_dashboard_includes_active_goal_progress(client: TestClient) -> None:
    _register_and_login(client)
    client.post(
        "/api/v1/weight-entries",
        json={
            "weight_value": 175.0,
            "weight_unit": "lbs",
            "observation_date": date.today().isoformat(),
        },
    )
    client.post(
        "/api/v1/goals",
        json={
            "goal_type": "lose",
            "start_value": 200.0,
            "target_value": 150.0,
            "target_unit": "lbs",
            "target_date": None,
        },
    )
    resp = client.get("/api/v1/dashboard/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert data["active_goal"] is not None
    assert data["active_goal"]["goal"]["goal_type"] == "lose"
    # (200-175)/(200-150) = 50%
    assert data["active_goal"]["progress_percent"] == pytest.approx(50.0)


def test_dashboard_active_goal_null_when_no_goal(client: TestClient) -> None:
    _register_and_login(client)
    client.post(
        "/api/v1/weight-entries",
        json={
            "weight_value": 175.0,
            "weight_unit": "lbs",
            "observation_date": date.today().isoformat(),
        },
    )
    resp = client.get("/api/v1/dashboard/summary")
    assert resp.json()["active_goal"] is None


def test_dashboard_active_goal_progress_null_when_goal_but_no_entries(
    client: TestClient,
) -> None:
    _register_and_login(client)
    client.post(
        "/api/v1/goals",
        json={
            "goal_type": "lose",
            "start_value": 200.0,
            "target_value": 150.0,
            "target_unit": "lbs",
            "target_date": None,
        },
    )
    resp = client.get("/api/v1/dashboard/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert data["active_goal"] is not None
    assert data["active_goal"]["goal"]["goal_type"] == "lose"
    assert data["active_goal"]["progress_percent"] is None
    assert data["active_goal"]["current_value"] is None
