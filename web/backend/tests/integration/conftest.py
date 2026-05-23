"""Shared fixtures for integration tests.

Provides a TestClient wired to an in-memory SQLite database.  Each test
function receives a client that starts with a fresh, empty schema and is
isolated from other tests.

SQLite is used instead of PostgreSQL so that integration tests can run in CI
without a running database service.  A single shared connection is used for
the whole test so that create_all, the test code, and the route handlers all
operate on the same in-memory database.
"""

from __future__ import annotations

from collections.abc import Generator, Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from weighttogo.auth.infrastructure.models import Base
from weighttogo.auth.interface.router import limiter
from weighttogo.main import app
from weighttogo.shared.db import get_db_session


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Yield a fresh in-memory SQLite session per test.

    Uses ``StaticPool`` so that all accesses within the test use the same
    in-memory database connection — required because SQLite ``:memory:`` is
    per-connection.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Enable FK constraints in SQLite
    with engine.connect() as conn:
        conn.execute(text("PRAGMA foreign_keys=ON"))

    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = session_factory()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture(scope="function")
def client(db_session: Session) -> Iterator[TestClient]:
    """Yield a TestClient whose database dependency uses the in-memory session.

    Rate limiting is disabled via ``limiter.enabled = False`` so that tests
    calling the same endpoint multiple times are not blocked.
    """

    def _override_db() -> Generator[Session, None, None]:
        # Mirrors the commit/rollback policy of shared/db.get_db_session.
        # HTTPException is an expected application-level event (e.g. 401, 409)
        # and should NOT trigger a rollback — the domain may have made valid
        # DB changes (e.g. incrementing the failed login counter) that we
        # want to keep.
        from fastapi import HTTPException

        try:
            yield db_session
            db_session.commit()
        except HTTPException:
            db_session.commit()
            raise
        except Exception:
            db_session.rollback()
            raise

    app.dependency_overrides[get_db_session] = _override_db
    limiter.enabled = False
    with TestClient(app, raise_server_exceptions=True) as test_client:
        yield test_client
    limiter.enabled = True
    app.dependency_overrides.pop(get_db_session, None)
