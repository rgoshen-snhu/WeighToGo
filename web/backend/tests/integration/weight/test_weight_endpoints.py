"""Integration tests for /api/v1/weight-entries endpoints (subtask 17)."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from fastapi.testclient import TestClient

# ── Helpers ───────────────────────────────────────────────────────────────────


def _register_and_login(client: TestClient) -> TestClient:
    """Register a user and return a client with session cookies set."""
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "weight@example.com",
            "password": "ValidPass123!",
            "display_name": "Weight Tester",
        },
    )
    return client


def _valid_payload(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "weight_value": 175.5,
        "weight_unit": "lbs",
        "observation_date": date.today().isoformat(),
        "notes": None,
    }
    base.update(overrides)
    return base


# ── Auth guard ────────────────────────────────────────────────────────────────


def test_list_entries_requires_auth(client: TestClient) -> None:
    resp = client.get("/api/v1/weight-entries")
    assert resp.status_code == 401


def test_create_entry_requires_auth(client: TestClient) -> None:
    resp = client.post("/api/v1/weight-entries", json=_valid_payload())
    assert resp.status_code == 401


def test_get_entry_requires_auth(client: TestClient) -> None:
    resp = client.get("/api/v1/weight-entries/1")
    assert resp.status_code == 401


def test_update_entry_requires_auth(client: TestClient) -> None:
    resp = client.put("/api/v1/weight-entries/1", json=_valid_payload())
    assert resp.status_code == 401


def test_delete_entry_requires_auth(client: TestClient) -> None:
    resp = client.delete("/api/v1/weight-entries/1")
    assert resp.status_code == 401


# ── Create ────────────────────────────────────────────────────────────────────


def test_create_entry_returns_201_with_body(client: TestClient) -> None:
    _register_and_login(client)
    resp = client.post("/api/v1/weight-entries", json=_valid_payload())
    assert resp.status_code == 201
    data = resp.json()
    assert data["weight_unit"] == "lbs"
    assert "entry_id" in data


def test_create_entry_duplicate_date_returns_409(client: TestClient) -> None:
    _register_and_login(client)
    client.post("/api/v1/weight-entries", json=_valid_payload())
    resp = client.post("/api/v1/weight-entries", json=_valid_payload())
    assert resp.status_code == 409


def test_create_entry_future_date_returns_422(client: TestClient) -> None:
    _register_and_login(client)
    future = (date.today() + timedelta(days=1)).isoformat()
    resp = client.post("/api/v1/weight-entries", json=_valid_payload(observation_date=future))
    assert resp.status_code == 422


# ── List ──────────────────────────────────────────────────────────────────────


def test_list_entries_returns_paginated_envelope(client: TestClient) -> None:
    _register_and_login(client)
    client.post("/api/v1/weight-entries", json=_valid_payload())
    resp = client.get("/api/v1/weight-entries")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "next_cursor" in data
    assert len(data["items"]) == 1


# ── Get single ────────────────────────────────────────────────────────────────


def test_get_entry_returns_200(client: TestClient) -> None:
    _register_and_login(client)
    create_resp = client.post("/api/v1/weight-entries", json=_valid_payload())
    entry_id = create_resp.json()["entry_id"]
    resp = client.get(f"/api/v1/weight-entries/{entry_id}")
    assert resp.status_code == 200
    assert resp.json()["entry_id"] == entry_id


def test_get_nonexistent_entry_returns_404(client: TestClient) -> None:
    _register_and_login(client)
    resp = client.get("/api/v1/weight-entries/99999")
    assert resp.status_code == 404


# ── Update ────────────────────────────────────────────────────────────────────


def test_update_entry_returns_200_with_new_value(client: TestClient) -> None:
    _register_and_login(client)
    create_resp = client.post("/api/v1/weight-entries", json=_valid_payload())
    entry_id = create_resp.json()["entry_id"]
    resp = client.put(
        f"/api/v1/weight-entries/{entry_id}",
        json=_valid_payload(weight_value=180.0),
    )
    assert resp.status_code == 200
    assert resp.json()["weight_value"] == 180.0


def test_update_entry_conflict_date_returns_409(client: TestClient) -> None:
    _register_and_login(client)
    today = date.today()
    yesterday = (today - timedelta(days=1)).isoformat()
    client.post("/api/v1/weight-entries", json=_valid_payload(observation_date=yesterday))
    create_resp = client.post("/api/v1/weight-entries", json=_valid_payload())
    entry_id = create_resp.json()["entry_id"]
    resp = client.put(
        f"/api/v1/weight-entries/{entry_id}",
        json=_valid_payload(observation_date=yesterday),
    )
    assert resp.status_code == 409


# ── Delete ────────────────────────────────────────────────────────────────────


def test_delete_entry_returns_204(client: TestClient) -> None:
    _register_and_login(client)
    create_resp = client.post("/api/v1/weight-entries", json=_valid_payload())
    entry_id = create_resp.json()["entry_id"]
    resp = client.delete(f"/api/v1/weight-entries/{entry_id}")
    assert resp.status_code == 204


def test_delete_entry_is_idempotent(client: TestClient) -> None:
    _register_and_login(client)
    create_resp = client.post("/api/v1/weight-entries", json=_valid_payload())
    entry_id = create_resp.json()["entry_id"]
    client.delete(f"/api/v1/weight-entries/{entry_id}")
    resp = client.delete(f"/api/v1/weight-entries/{entry_id}")
    assert resp.status_code == 204


def test_delete_nonexistent_entry_returns_404(client: TestClient) -> None:
    _register_and_login(client)
    resp = client.delete("/api/v1/weight-entries/99999")
    assert resp.status_code == 404
