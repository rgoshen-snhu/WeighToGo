"""Security header regression tests (SRS §NFR-S-10, GH-34).

Verifies that every response carries the full set of SRS-required security
headers and that environment-sensitive headers (HSTS) are gated correctly.
"""

import pytest
from fastapi.testclient import TestClient

from weighttogo.config import get_settings


def test_csp_header_is_present_on_json_responses(client: TestClient) -> None:
    """Content-Security-Policy must be emitted on all responses (SRS §NFR-S-10)."""
    response = client.get("/health")

    assert "Content-Security-Policy" in response.headers


def test_csp_default_policy_is_strict_for_json_responses(client: TestClient) -> None:
    """Default CSP must deny all resource loading — maximally protective for JSON endpoints."""
    response = client.get("/health")

    csp = response.headers["Content-Security-Policy"]
    assert "default-src 'none'" in csp
    assert "frame-ancestors 'none'" in csp


def test_csp_override_allows_swagger_cdn_and_inline_script_for_docs_endpoint(
    client: TestClient,
) -> None:
    """Docs CSP must allow CDN assets and inline scripts.

    FastAPI's Swagger UI page includes a dynamic inline <script> block that
    initialises SwaggerUIBundle.  Because the content is parameterised at
    runtime a static SHA256 hash is impractical, so 'unsafe-inline' is the
    required allowance for script-src on docs paths only.
    """
    response = client.get("/api/docs")

    csp = response.headers["Content-Security-Policy"]
    assert "cdn.jsdelivr.net" in csp
    assert "'unsafe-inline'" in csp


def test_hsts_is_not_emitted_outside_production(client: TestClient) -> None:
    """HSTS must be omitted in non-production environments (dev servers run over HTTP)."""
    # conftest sets ENVIRONMENT=test
    response = client.get("/health")

    assert "Strict-Transport-Security" not in response.headers


def test_hsts_is_emitted_in_production_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """HSTS must be present in the production environment (SRS §NFR-S-10)."""
    # ARRANGE — patch env and clear LRU cache so middleware picks up production settings
    monkeypatch.setenv("ENVIRONMENT", "production")
    get_settings.cache_clear()
    try:
        from weighttogo.main import app

        prod_client = TestClient(app)

        # ACT
        response = prod_client.get("/health")

        # ASSERT
        assert "Strict-Transport-Security" in response.headers
        expected_hsts = "max-age=31536000; includeSubDomains"
        assert response.headers["Strict-Transport-Security"] == expected_hsts
    finally:
        # Restore — clear cache so subsequent tests see the test environment again
        get_settings.cache_clear()
