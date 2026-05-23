"""C2 regression: /refresh must revoke the token family when user is not found.

When the user row is absent after a successful token rotation the route must
call revoke_family so the newly-issued refresh token does not stay live in
the database.
"""

from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from weighttogo.auth.infrastructure.models import RefreshTokenModel
from weighttogo.auth.infrastructure.repositories import SqlAlchemyUserRepository


def test_refresh_revokes_family_when_user_not_found(
    client: TestClient, db_session: Session
) -> None:
    """All refresh tokens must be revoked when get_by_id returns None after rotation."""
    # Register only — gives us exactly one token family in the DB so we can
    # assert ALL tokens are revoked without a separate-family false positive.
    client.post(
        "/api/v1/auth/register",
        json={"email": "c2user@example.com", "password": "SecurePass1!", "display_name": "C2 User"},
    )

    # Patch get_by_id to simulate user deleted between rotation and user-check
    with patch.object(SqlAlchemyUserRepository, "get_by_id", return_value=None):
        response = client.post("/api/v1/auth/refresh")

    assert response.status_code == 401

    # Every token in the DB must now be revoked (none orphaned)
    tokens = db_session.query(RefreshTokenModel).all()
    assert tokens, "expected at least one token in DB"
    assert all(t.revoked_at is not None for t in tokens), (
        f"orphaned token(s) found: {[t.token_id for t in tokens if t.revoked_at is None]}"
    )
