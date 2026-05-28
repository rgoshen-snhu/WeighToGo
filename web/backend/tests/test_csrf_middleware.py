"""CSRF Origin/Referer middleware tests (SRS §NFR-S-9, GH-34).

Verifies that state-changing requests without a valid Origin or Referer header
are rejected with 403, and that safe methods and requests from allowed origins
are permitted.

The default cors_allowed_origins setting is "http://localhost:5173".

Pass-through tests use raise_server_exceptions=False because the unit-test
SQLite DB has no schema; a 5xx from the endpoint is still proof that the CSRF
middleware did not block the request with a 403.
"""

import pytest
from fastapi.testclient import TestClient

from weighttogo.main import app


@pytest.fixture
def permissive_client() -> TestClient:
    """TestClient that surfaces 5xx as responses rather than raising exceptions."""
    return TestClient(app, raise_server_exceptions=False)


def test_post_with_missing_origin_and_referer_is_forbidden(client: TestClient) -> None:
    """POST without Origin or Referer must be rejected 403 (SRS §NFR-S-9)."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "x@example.com", "password": "irrelevant"},
        headers={},
    )

    assert response.status_code == 403
    body = response.json()
    assert body["title"] == "Forbidden"
    assert body["status"] == 403


def test_post_with_allowed_origin_header_passes(permissive_client: TestClient) -> None:
    """POST from an allowed origin must reach the endpoint (not blocked by CSRF)."""
    response = permissive_client.post(
        "/api/v1/auth/login",
        json={"email": "x@example.com", "password": "irrelevant"},
        headers={"Origin": "http://localhost:5173"},
    )

    assert response.status_code != 403


def test_post_with_disallowed_origin_is_forbidden(client: TestClient) -> None:
    """POST from an origin not in cors_allowed_origins must be rejected 403."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "x@example.com", "password": "irrelevant"},
        headers={"Origin": "https://evil.example.com"},
    )

    assert response.status_code == 403


def test_post_falls_back_to_referer_when_origin_missing(permissive_client: TestClient) -> None:
    """POST with an allowed Referer (no Origin) must reach the endpoint."""
    response = permissive_client.post(
        "/api/v1/auth/login",
        json={"email": "x@example.com", "password": "irrelevant"},
        headers={"Referer": "http://localhost:5173/login"},
    )

    assert response.status_code != 403


def test_get_request_bypasses_csrf_check(client: TestClient) -> None:
    """GET requests must always pass — safe methods carry no CSRF risk."""
    response = client.get("/health")

    assert response.status_code == 200


def test_options_preflight_bypasses_csrf_check(client: TestClient) -> None:
    """OPTIONS preflights must always pass — handled by CORSMiddleware upstream."""
    response = client.options("/api/v1/weight-entries")

    assert response.status_code in (200, 204, 400, 405)
