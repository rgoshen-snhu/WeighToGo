"""Unit tests for SqlAlchemyWeightEntryRepository using an in-memory SQLite DB.

Covers the range read for the trend / rate-of-change paths (FR-D-2, FR-D-3) and
the observation-date read used by streak detection (FR-Ach-3).  The range query
rides the ``(user_id, observation_date)`` composite index; the index-usage proof
itself runs on PostgreSQL in
``tests/integration/weight/test_index_usage_postgres.py``.
"""

from __future__ import annotations

from collections.abc import Generator
from datetime import UTC, date, datetime
from decimal import Decimal

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from weighttogo.auth.infrastructure.models import Base
from weighttogo.weight_tracking.domain.entities import WeightEntry
from weighttogo.weight_tracking.infrastructure.models import (  # noqa: F401 — registers with Base
    WeightEntryModel,
)
from weighttogo.weight_tracking.infrastructure.repositories import (
    SqlAlchemyWeightEntryRepository,
)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """In-memory SQLite session with all tables created and a seeded user."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    with engine.connect() as conn:
        conn.execute(text("PRAGMA foreign_keys=ON"))
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = session_factory()
    session.execute(
        text(
            "INSERT INTO users"
            " (email, password_hash, display_name, is_active, failed_login_count,"
            "  created_at, updated_at)"
            " VALUES ('test@example.com', 'hash', 'Test', 1, 0,"
            "  CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
        )
    )
    session.commit()
    yield session
    session.close()
    Base.metadata.drop_all(engine)
    engine.dispose()


def _save_entry(
    repo: SqlAlchemyWeightEntryRepository,
    observation_date: date,
    value: str,
    *,
    is_deleted: bool = False,
    user_id: int = 1,
) -> WeightEntry:
    now = datetime.now(UTC)
    entry = WeightEntry(
        entry_id=None,
        user_id=user_id,
        weight_value=Decimal(value),
        weight_unit="lbs",
        observation_date=observation_date,
        notes=None,
        created_at=now,
        updated_at=now,
        is_deleted=is_deleted,
        deleted_at=now if is_deleted else None,
    )
    return repo.save(entry)


def test_list_for_user_in_range_returns_entries_within_bounds(db_session: Session) -> None:
    # ARRANGE
    repo = SqlAlchemyWeightEntryRepository(db_session)
    _save_entry(repo, date(2026, 5, 1), "200")  # before range
    _save_entry(repo, date(2026, 5, 10), "190")  # in range
    _save_entry(repo, date(2026, 5, 20), "180")  # in range
    _save_entry(repo, date(2026, 5, 30), "170")  # after range

    # ACT
    result = repo.list_for_user_in_range(1, date(2026, 5, 10), date(2026, 5, 20))

    # ASSERT
    assert [e.observation_date for e in result] == [date(2026, 5, 10), date(2026, 5, 20)]


def test_list_for_user_in_range_excludes_soft_deleted(db_session: Session) -> None:
    # ARRANGE
    repo = SqlAlchemyWeightEntryRepository(db_session)
    _save_entry(repo, date(2026, 5, 10), "190")
    _save_entry(repo, date(2026, 5, 12), "188", is_deleted=True)

    # ACT
    result = repo.list_for_user_in_range(1, date(2026, 5, 1), date(2026, 5, 31))

    # ASSERT
    assert [e.observation_date for e in result] == [date(2026, 5, 10)]


def test_list_for_user_in_range_orders_oldest_first(db_session: Session) -> None:
    # ARRANGE — insert out of date order
    repo = SqlAlchemyWeightEntryRepository(db_session)
    _save_entry(repo, date(2026, 5, 20), "180")
    _save_entry(repo, date(2026, 5, 5), "200")
    _save_entry(repo, date(2026, 5, 12), "190")

    # ACT
    result = repo.list_for_user_in_range(1, date(2026, 5, 1), date(2026, 5, 31))

    # ASSERT
    assert [e.observation_date for e in result] == [
        date(2026, 5, 5),
        date(2026, 5, 12),
        date(2026, 5, 20),
    ]


def test_list_observation_dates_excludes_deleted_entries(db_session: Session) -> None:
    # ARRANGE: two active dates + one deleted date (FR-Ach-3)
    repo = SqlAlchemyWeightEntryRepository(db_session)
    _save_entry(repo, date(2026, 1, 1), "180")
    _save_entry(repo, date(2026, 1, 2), "180")
    _save_entry(repo, date(2026, 1, 3), "180", is_deleted=True)

    # ACT
    result = repo.list_observation_dates(1)

    # ASSERT: deleted entry excluded
    assert result == {date(2026, 1, 1), date(2026, 1, 2)}
