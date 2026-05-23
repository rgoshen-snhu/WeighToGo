"""C11 regression: delete_cookie must include same attributes as set_cookie."""

from fastapi.testclient import TestClient


def _login(client: TestClient) -> None:
    client.post(
        "/api/v1/auth/register",
        json={"email": "cookiedel@example.com", "password": "SecurePass1!", "display_name": "CD"},
    )
    client.post(
        "/api/v1/auth/login",
        json={"email": "cookiedel@example.com", "password": "SecurePass1!"},
    )


def test_logout_delete_cookie_includes_samesite_httponly(client: TestClient) -> None:
    """Set-Cookie deletion headers from /logout must include SameSite and HttpOnly."""
    _login(client)
    response = client.post("/api/v1/auth/logout")
    assert response.status_code == 204

    cookie_headers = response.headers.get_list("set-cookie")
    assert cookie_headers, "expected Set-Cookie headers on logout"
    combined = " ".join(h.lower() for h in cookie_headers)
    assert "samesite=strict" in combined, f"missing SameSite=Strict in: {cookie_headers}"
    assert "httponly" in combined, f"missing HttpOnly in: {cookie_headers}"
