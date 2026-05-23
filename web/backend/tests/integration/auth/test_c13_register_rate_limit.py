"""C13 regression: /register must be rate-limited per NFR-S-5 (3 req/hour)."""

from fastapi.testclient import TestClient

from weighttogo.auth.interface.router import limiter


def test_register_returns_429_after_limit(client: TestClient) -> None:
    """The 4th registration attempt from the same IP within an hour must return 429."""
    limiter.enabled = True
    try:
        statuses = []
        for i in range(4):
            r = client.post(
                "/api/v1/auth/register",
                json={
                    "email": f"rl_reg_{i}@example.com",
                    "password": "SecurePass1!",
                    "display_name": f"User {i}",
                },
            )
            statuses.append(r.status_code)
    finally:
        limiter.enabled = False

    assert 429 in statuses, f"expected 429 in: {statuses}"
