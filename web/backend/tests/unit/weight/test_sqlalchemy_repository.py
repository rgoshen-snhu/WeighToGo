"""Unit tests for SqlAlchemyWeightEntryRepository read helpers (FR-Ach-3)."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from weighttogo.auth.infrastructure.models import Base


@pytest.fixture()
def session() -> Session:
    """In-memory SQLite session with all tables created and a seeded user."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    with engine.connect() as conn:
        conn.execute(text("PRAGMA foreign_keys=ON"))

    from weighttogo.weight_tracking.infrastructure.models import WeightEntryModel  # noqa: F401

    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    s = factory()
    _seed_user(s)
    return s


def _seed_user(s: Session) -> None:
    from weighttogo.auth.infrastructure.models import UserModel

    user = UserModel(
        email="weight_repo@example.com",
        display_name="Weight Repo",
        password_hash="x",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    s.add(user)
    s.flush()
    s._test_user_id = user.user_id  # type: ignore[attr-defined]


def _add_entry(
    s: Session,
    observation_date: date,
    *,
    is_deleted: bool = False,
) -> None:
    from weighttogo.weight_tracking.infrastructure.models import WeightEntryModel

    s.add(
        WeightEntryModel(
            user_id=s._test_user_id,  # type: ignore[attr-defined]
            weight_value=Decimal("180.00"),
            weight_unit="lbs",
            observation_date=observation_date,
            notes=None,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            is_deleted=is_deleted,
            deleted_at=None,
        )
    )
    s.flush()


def test_list_observation_dates_excludes_deleted_entries(session: Session) -> None:
    from weighttogo.weight_tracking.infrastructure.repositories import (
        SqlAlchemyWeightEntryRepository,
    )

    # ARRANGE: two active dates + one deleted date
    _add_entry(session, date(2026, 1, 1))
    _add_entry(session, date(2026, 1, 2))
    _add_entry(session, date(2026, 1, 3), is_deleted=True)
    repo = SqlAlchemyWeightEntryRepository(session)
    # ACT
    result = repo.list_observation_dates(session._test_user_id)  # type: ignore[attr-defined]
    # ASSERT: deleted entry excluded
    assert result == {date(2026, 1, 1), date(2026, 1, 2)}
