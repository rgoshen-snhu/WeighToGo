"""Shared database session dependency for FastAPI.

Provides the ``get_db_session`` dependency function used by all route handlers
that need a SQLAlchemy session.

Usage in route handlers::

    from weighttogo.shared.db import get_db_session

    @router.post("/example")
    def create(session: Session = Depends(get_db_session)):
        ...

Session lifecycle:
    - On success: commit then close.
    - On ``HTTPException`` (expected application errors such as 401, 404, 409):
      commit any valid domain mutations (e.g. failed-login counter increments)
      then close.
    - On unexpected exceptions: rollback then close.

``HTTPException`` must NOT trigger a rollback because domain use cases may
have persisted valid state changes (e.g. recording a failed login attempt)
before raising an ``HTTPException`` to signal the HTTP error to the client.
"""

from __future__ import annotations

from collections.abc import Generator

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from weighttogo.config import get_settings

_engine = None
_SessionLocal: sessionmaker[Session] | None = None


def _get_engine() -> object:
    """Lazily build the engine from settings so tests can override dependencies."""
    global _engine, _SessionLocal  # noqa: PLW0603
    if _engine is None:
        settings = get_settings()
        _engine = create_engine(settings.database_url, pool_pre_ping=True)
        _SessionLocal = sessionmaker(bind=_engine, autocommit=False, autoflush=False)
    return _engine


def get_db_session() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session per request.

    See module docstring for the commit/rollback policy.

    Yields:
        An active SQLAlchemy ``Session``.
    """
    _get_engine()
    assert _SessionLocal is not None
    session = _SessionLocal()
    try:
        yield session
        session.commit()
    except HTTPException:
        # Expected application-level error — commit valid domain changes then re-raise.
        session.commit()
        raise
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
