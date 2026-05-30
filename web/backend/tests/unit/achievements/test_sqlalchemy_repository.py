"""Unit tests for SqlAlchemyAchievementRepository."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from weighttogo.achievements.domain.entities import Achievement, AchievementType
from weighttogo.auth.infrastructure.models import Base


@pytest.fixture()
def session() -> Session:
    """In-memory SQLite session with all tables created."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    with engine.connect() as conn:
        conn.execute(text("PRAGMA foreign_keys=ON"))

    # Import models so Base.metadata knows all tables before create_all
    from weighttogo.achievements.infrastructure.models import AchievementModel  # noqa: F401
    from weighttogo.goals.infrastructure.models import GoalModel  # noqa: F401
    from weighttogo.weight_tracking.infrastructure.models import WeightEntryModel  # noqa: F401

    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    s = factory()
    _seed(s)
    return s


def _seed(s: Session) -> None:
    """Insert the minimal user + goal rows needed for FK constraints."""
    from weighttogo.auth.infrastructure.models import UserModel
    from weighttogo.goals.infrastructure.models import GoalModel

    user = UserModel(
        email="ach_repo@example.com",
        display_name="Ach Repo",
        password_hash="x",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    s.add(user)
    s.flush()

    goal = GoalModel(
        user_id=user.user_id,
        target_value=Decimal("150"),
        target_unit="lbs",
        start_value=Decimal("200"),
        goal_type="lose",
        is_active=True,
        is_achieved=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    s.add(goal)
    s.flush()

    # Attach IDs to the session object for use in tests
    s._test_user_id = user.user_id  # type: ignore[attr-defined]
    s._test_goal_id = goal.goal_id  # type: ignore[attr-defined]


def _make_milestone(s: Session, threshold: Decimal = Decimal("5")) -> Achievement:
    return Achievement(
        achievement_id=None,
        user_id=s._test_user_id,  # type: ignore[attr-defined]
        goal_id=s._test_goal_id,  # type: ignore[attr-defined]
        achievement_type=AchievementType.MILESTONE,
        threshold=threshold,
        earned_at=datetime.now(UTC),
    )


# ── save ──────────────────────────────────────────────────────────────────────


def test_save_assigns_achievement_id(session: Session) -> None:
    from weighttogo.achievements.infrastructure.repositories import SqlAlchemyAchievementRepository

    repo = SqlAlchemyAchievementRepository(session)
    saved = repo.save(_make_milestone(session))
    assert saved is not None
    assert saved.achievement_id is not None


# ── get_recorded_thresholds ───────────────────────────────────────────────────


def test_get_recorded_thresholds_returns_persisted_values(session: Session) -> None:
    from weighttogo.achievements.infrastructure.repositories import SqlAlchemyAchievementRepository

    repo = SqlAlchemyAchievementRepository(session)
    repo.save(_make_milestone(session, Decimal("5")))
    repo.save(_make_milestone(session, Decimal("10")))
    result = repo.get_recorded_thresholds(session._test_goal_id)  # type: ignore[attr-defined]
    assert result == frozenset({Decimal("5"), Decimal("10")})


def test_get_recorded_thresholds_returns_empty_when_none(session: Session) -> None:
    from weighttogo.achievements.infrastructure.repositories import SqlAlchemyAchievementRepository

    repo = SqlAlchemyAchievementRepository(session)
    result = repo.get_recorded_thresholds(session._test_goal_id)  # type: ignore[attr-defined]
    assert result == frozenset()


# ── get_recorded_streak_thresholds ────────────────────────────────────────────


def _make_streak(s: Session, threshold: Decimal) -> Achievement:
    return Achievement(
        achievement_id=None,
        user_id=s._test_user_id,  # type: ignore[attr-defined]
        goal_id=s._test_goal_id,  # type: ignore[attr-defined]
        achievement_type=AchievementType.STREAK,
        threshold=threshold,
        earned_at=datetime.now(UTC),
    )


def test_get_recorded_streak_thresholds_returns_only_streak_rows(session: Session) -> None:
    from weighttogo.achievements.infrastructure.repositories import SqlAlchemyAchievementRepository

    # ARRANGE: a streak(7) and a milestone(5) on the same goal
    repo = SqlAlchemyAchievementRepository(session)
    repo.save(_make_streak(session, Decimal("7")))
    repo.save(_make_milestone(session, Decimal("5")))
    # ACT
    result = repo.get_recorded_streak_thresholds(session._test_goal_id)  # type: ignore[attr-defined]
    # ASSERT: only the streak threshold comes back
    assert result == frozenset({Decimal("7")})


def test_get_recorded_streak_thresholds_returns_empty_when_none(session: Session) -> None:
    from weighttogo.achievements.infrastructure.repositories import SqlAlchemyAchievementRepository

    repo = SqlAlchemyAchievementRepository(session)
    result = repo.get_recorded_streak_thresholds(session._test_goal_id)  # type: ignore[attr-defined]
    assert result == frozenset()


# ── get_by_id ─────────────────────────────────────────────────────────────────


def test_get_by_id_returns_achievement_for_correct_user(session: Session) -> None:
    from weighttogo.achievements.infrastructure.repositories import SqlAlchemyAchievementRepository

    repo = SqlAlchemyAchievementRepository(session)
    saved = repo.save(_make_milestone(session))
    assert saved is not None
    assert saved.achievement_id is not None
    found = repo.get_by_id(saved.achievement_id, session._test_user_id)  # type: ignore[attr-defined]
    assert found is not None
    assert found.achievement_id == saved.achievement_id


def test_get_by_id_returns_none_for_wrong_user_idor_guard(session: Session) -> None:
    from weighttogo.achievements.infrastructure.repositories import SqlAlchemyAchievementRepository

    repo = SqlAlchemyAchievementRepository(session)
    saved = repo.save(_make_milestone(session))
    assert saved is not None
    assert saved.achievement_id is not None
    result = repo.get_by_id(saved.achievement_id, user_id=99999)
    assert result is None


# ── list_for_user ─────────────────────────────────────────────────────────────


def test_list_for_user_returns_achievements_newest_first(session: Session) -> None:
    from weighttogo.achievements.infrastructure.repositories import SqlAlchemyAchievementRepository

    repo = SqlAlchemyAchievementRepository(session)
    now = datetime.now(UTC)
    ach_old = Achievement(
        achievement_id=None,
        user_id=session._test_user_id,  # type: ignore[attr-defined]
        goal_id=session._test_goal_id,  # type: ignore[attr-defined]
        achievement_type=AchievementType.MILESTONE,
        threshold=Decimal("5"),
        earned_at=now - timedelta(hours=2),
    )
    ach_new = Achievement(
        achievement_id=None,
        user_id=session._test_user_id,  # type: ignore[attr-defined]
        goal_id=session._test_goal_id,  # type: ignore[attr-defined]
        achievement_type=AchievementType.MILESTONE,
        threshold=Decimal("10"),
        earned_at=now,
    )
    repo.save(ach_old)
    repo.save(ach_new)
    results = repo.list_for_user(session._test_user_id, limit=10)  # type: ignore[attr-defined]
    assert results[0].threshold == Decimal("10")
    assert results[1].threshold == Decimal("5")
