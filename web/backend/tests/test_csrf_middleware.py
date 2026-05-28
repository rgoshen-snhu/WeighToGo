"""CSRF Origin/Referer middleware tests (SRS §NFR-S-9, GH-34).

Verifies CSRF middleware behaviour:
- Requests where Origin or Referer IS present and WRONG → 403
- Requests with no Origin and no Referer → pass through (cannot be a
  browser CSRF attack; SameSite=Strict cookies guard that path)
- Requests from allowed CORS origins or the API's own origin → pass through
- Safe methods (GET, HEAD, OPTIONS) → always pass through

The default cors_allowed_origins setting is "http://localhost:5173".

Pass-through tests use permissive_client (raise_server_exceptions=False)
because the unit-test SQLite DB has no schema; a 5xx from the endpoint is
still proof that the CSRF middleware did not block the request with a 403.
"""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from weighttogo.main import app


@pytest.fixture
def permissive_client() -> Iterator[TestClient]:
    """TestClient that surfaces 5xx as responses rather than raising exceptions."""
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client


# ── Absent-header pass-through ────────────────────────────────────────────────


def test_post_with_missing_origin_and_referer_passes_through(
    permissive_client: TestClient,
) -> None:
    """POST with no Origin and no Referer must NOT be rejected by CSRF.

    A cross-origin browser CSRF attack always includes an Origin header (required
    by the CORS specification).  A request with neither Origin nor Referer cannot
    be a browser-originated CSRF attack — SameSite=Strict cookies already guard
    that path.  This allows same-origin requests proxied through Vite dev server
    (changeOrigin=true strips both headers) to reach the backend.
    """
    response = permissive_client.post(
        "/api/v1/auth/login",
        json={"email": "x@example.com", "password": "irrelevant"},
        headers={},
    )

    assert response.status_code != 403


# ── Disallowed origin blocked ─────────────────────────────────────────────────


def test_post_with_disallowed_origin_is_forbidden(client: TestClient) -> None:
    """POST where Origin is present but not in the allowlist → 403."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "x@example.com", "password": "irrelevant"},
        headers={"Origin": "https://evil.example.com"},
    )

    assert response.status_code == 403
    body = response.json()
    assert body["title"] == "Forbidden"
    assert body["status"] == 403


def test_delete_with_disallowed_origin_is_forbidden(client: TestClient) -> None:
    """DELETE with a wrong Origin must be rejected — pins that all unsafe methods are checked."""
    response = client.delete(
        "/api/v1/weight-entries/1",
        headers={"Origin": "https://evil.example.com"},
    )

    assert response.status_code == 403


def test_put_with_disallowed_origin_is_forbidden(client: TestClient) -> None:
    """PUT with a wrong Origin must be rejected — pins check covers PUT, not just POST."""
    response = client.put(
        "/api/v1/weight-entries/1",
        json={},
        headers={"Origin": "https://evil.example.com"},
    )

    assert response.status_code == 403


def test_post_with_null_origin_is_forbidden(client: TestClient) -> None:
    """Origin: null (opaque origin — sandboxed iframes, data: URLs, file://) → 403.

    'null' is not in cors_allowed_origins and not the API's own origin; it is
    a common attack vector from sandboxed frames and must be explicitly blocked.
    """
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "x@example.com", "password": "irrelevant"},
        headers={"Origin": "null"},
    )

    assert response.status_code == 403


def test_origin_takes_precedence_over_benign_referer(client: TestClient) -> None:
    """A malicious Origin must be rejected even when Referer points to an allowed origin.

    Pins the 'check Origin first' decision documented in ADR-0017.  A future
    refactor that reverses the precedence would allow the attacker to smuggle a
    benign Referer alongside a hostile Origin.
    """
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "x@example.com", "password": "irrelevant"},
        headers={
            "Origin": "https://evil.example.com",
            "Referer": "http://localhost:5173/login",
        },
    )

    assert response.status_code == 403


# ── Allowed origins pass through ──────────────────────────────────────────────


def test_post_with_allowed_origin_header_passes(permissive_client: TestClient) -> None:
    """POST from an allowed CORS origin must reach the endpoint."""
    response = permissive_client.post(
        "/api/v1/auth/login",
        json={"email": "x@example.com", "password": "irrelevant"},
        headers={"Origin": "http://localhost:5173"},
    )

    assert response.status_code != 403


def test_post_falls_back_to_referer_when_origin_missing(permissive_client: TestClient) -> None:
    """POST with an allowed Referer (no Origin) must reach the endpoint."""
    response = permissive_client.post(
        "/api/v1/auth/login",
        json={"email": "x@example.com", "password": "irrelevant"},
        headers={"Referer": "http://localhost:5173/login"},
    )

    assert response.status_code != 403


def test_post_from_api_own_origin_passes(permissive_client: TestClient) -> None:
    """Same-origin requests (e.g. Swagger UI at /api/docs) must not be blocked.

    Swagger UI posts back to the API's own host, sending Origin or Referer
    pointing to the API server itself.  Those are not CSRF attacks (ADR-0017
    §same-origin allowance).  TestClient uses http://testserver as the API host.
    """
    response = permissive_client.post(
        "/api/v1/auth/login",
        json={"email": "x@example.com", "password": "irrelevant"},
        headers={"Origin": "http://testserver"},
    )

    assert response.status_code != 403


def test_post_from_api_own_origin_via_referer_passes(permissive_client: TestClient) -> None:
    """Same-origin Referer (no Origin header) must also be permitted (ADR-0017)."""
    response = permissive_client.post(
        "/api/v1/auth/login",
        json={"email": "x@example.com", "password": "irrelevant"},
        headers={"Referer": "http://testserver/api/docs"},
    )

    assert response.status_code != 403


# ── Safe-method bypass ────────────────────────────────────────────────────────


def test_get_request_bypasses_csrf_check(client: TestClient) -> None:
    """GET requests must always pass — safe methods carry no CSRF risk."""
    response = client.get("/health")

    assert response.status_code == 200


def test_head_request_bypasses_csrf_check(client: TestClient) -> None:
    """HEAD requests must not be blocked by CSRF — HEAD is in _SAFE_METHODS.

    /health does not implement HEAD so 405 is expected from the router; what
    matters is that the CSRF middleware is not the one returning 403.
    """
    response = client.head("/health")

    assert response.status_code != 403


def test_options_preflight_bypasses_csrf_check(client: TestClient) -> None:
    """OPTIONS preflights must always pass — handled by CORSMiddleware upstream."""
    response = client.options("/api/v1/weight-entries")

    assert response.status_code != 403
