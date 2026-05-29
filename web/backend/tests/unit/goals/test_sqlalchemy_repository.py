"""Unit tests for SqlAlchemyGoalRepository using an in-memory SQLite DB."""

from __future__ import annotations

from collections.abc import Generator
from datetime import UTC, datetime
from decimal import Decimal

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from weighttogo.auth.infrastructure.models import Base
from weighttogo.goals.domain.entities import Goal, GoalType
from weighttogo.goals.domain.exceptions import ActiveGoalAlreadyExistsError
from weighttogo.goals.infrastructure.models import GoalModel  # noqa: F401 — registers with Base
from weighttogo.goals.infrastructure.repositories import SqlAlchemyGoalRepository


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
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
    # Create a test user — supply all NOT NULL columns that use Python-side
    # defaults (no server_default in SQLite schema).
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


def _make_goal(user_id: int = 1) -> Goal:
    now = datetime.now(UTC)
    return Goal(
        goal_id=None,
        user_id=user_id,
        target_value=Decimal("150"),
        target_unit="lbs",
        start_value=Decimal("200"),
        goal_type=GoalType.LOSE,
        target_date=None,
        is_active=True,
        is_achieved=False,
        achieved_at=None,
        created_at=now,
        updated_at=now,
    )


# ── save / get ────────────────────────────────────────────────────────────────


def test_save_new_goal_assigns_id(db_session: Session) -> None:
    repo = SqlAlchemyGoalRepository(db_session)
    goal = _make_goal()
    saved = repo.save(goal)
    assert saved.goal_id is not None


def test_get_by_id_returns_saved_goal(db_session: Session) -> None:
    repo = SqlAlchemyGoalRepository(db_session)
    saved = repo.save(_make_goal())
    db_session.commit()
    fetched = repo.get_by_id(saved.goal_id, user_id=1)  # type: ignore[arg-type]
    assert fetched is not None
    assert fetched.target_value == Decimal("150")


def test_get_by_id_scoped_to_user_id(db_session: Session) -> None:
    repo = SqlAlchemyGoalRepository(db_session)
    saved = repo.save(_make_goal(user_id=1))
    db_session.commit()
    assert repo.get_by_id(saved.goal_id, user_id=99) is None  # type: ignore[arg-type]


# ── active goal lookup ────────────────────────────────────────────────────────


def test_get_active_for_user_returns_active_goal(db_session: Session) -> None:
    repo = SqlAlchemyGoalRepository(db_session)
    repo.save(_make_goal())
    db_session.commit()
    active = repo.get_active_for_user(user_id=1)
    assert active is not None
    assert active.is_active is True


def test_get_active_for_user_returns_none_when_none(db_session: Session) -> None:
    repo = SqlAlchemyGoalRepository(db_session)
    assert repo.get_active_for_user(user_id=1) is None


# ── partial unique index via race backstop ────────────────────────────────────


def test_save_second_active_goal_raises_active_goal_already_exists(
    db_session: Session,
) -> None:
    repo = SqlAlchemyGoalRepository(db_session)
    repo.save(_make_goal())
    db_session.commit()
    with pytest.raises(ActiveGoalAlreadyExistsError):
        repo.save(_make_goal())
        db_session.commit()


# ── abandon and recreate ──────────────────────────────────────────────────────


def test_abandon_then_recreate_succeeds(db_session: Session) -> None:
    """After abandoning, a user can set a new active goal (partial index allows it)."""
    repo = SqlAlchemyGoalRepository(db_session)
    goal = repo.save(_make_goal())
    db_session.commit()
    goal.abandon()
    repo.save(goal)
    db_session.commit()
    # Create a second active goal — must succeed
    second = repo.save(_make_goal())
    db_session.commit()
    assert second.goal_id is not None


# ── list ──────────────────────────────────────────────────────────────────────


def test_list_for_user_returns_all_goals(db_session: Session) -> None:
    repo = SqlAlchemyGoalRepository(db_session)
    saved = repo.save(_make_goal())
    db_session.commit()
    saved.abandon()
    repo.save(saved)
    db_session.commit()
    repo.save(_make_goal())
    db_session.commit()
    goals = repo.list_for_user(user_id=1, limit=50)
    assert len(goals) == 2


def test_list_for_user_respects_limit(db_session: Session) -> None:
    repo = SqlAlchemyGoalRepository(db_session)
    # Persist three goals: create one, abandon it, repeat, then create a third
    first = repo.save(_make_goal())
    db_session.commit()
    first.abandon()
    repo.save(first)
    db_session.commit()
    second = repo.save(_make_goal())
    db_session.commit()
    second.abandon()
    repo.save(second)
    db_session.commit()
    repo.save(_make_goal())
    db_session.commit()

    goals = repo.list_for_user(user_id=1, limit=2)
    assert len(goals) == 2
