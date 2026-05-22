"""Tests for the health-check endpoint."""

from fastapi.testclient import TestClient

from weighttogo.config import get_settings


def test_health_endpoint_returns_ok_status_and_environment(
    client: TestClient,
) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["environment"] == get_settings().environment
