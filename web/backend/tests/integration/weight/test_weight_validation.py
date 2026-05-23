"""RFC 7807 validation error shape tests for weight endpoints (subtasks 18–19)."""

from __future__ import annotations

from datetime import date, timedelta

from fastapi.testclient import TestClient


def _register_and_login(client: TestClient) -> None:
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "valid@example.com",
            "password": "ValidPass123!",
            "display_name": "Valid User",
        },
    )


def _valid_payload(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "weight_value": 175.5,
        "weight_unit": "lbs",
        "observation_date": date.today().isoformat(),
    }
    base.update(overrides)
    return base


def test_invalid_weight_unit_returns_rfc7807_422(client: TestClient) -> None:
    _register_and_login(client)
    resp = client.post("/api/v1/weight-entries", json=_valid_payload(weight_unit="pounds"))
    assert resp.status_code == 422
    body = resp.json()
    assert body["type"] == "about:blank"
    assert body["status"] == 422
    assert "errors" in body
    field_codes = [e["field"] for e in body["errors"]]
    assert "weight_unit" in field_codes


def test_future_date_schema_rejection_returns_rfc7807_422(client: TestClient) -> None:
    _register_and_login(client)
    future = (date.today() + timedelta(days=1)).isoformat()
    resp = client.post("/api/v1/weight-entries", json=_valid_payload(observation_date=future))
    assert resp.status_code == 422
    body = resp.json()
    assert body["type"] == "about:blank"
    assert body["status"] == 422


def test_negative_weight_returns_rfc7807_422(client: TestClient) -> None:
    _register_and_login(client)
    resp = client.post("/api/v1/weight-entries", json=_valid_payload(weight_value=-1))
    assert resp.status_code == 422
    body = resp.json()
    assert "errors" in body
    field_codes = [e["field"] for e in body["errors"]]
    assert "weight_value" in field_codes
