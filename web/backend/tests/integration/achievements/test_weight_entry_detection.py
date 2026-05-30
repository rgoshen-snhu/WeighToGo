"""Integration tests: achievement detection on weight-entry create (FR-Ach-1/2, FR-G-4)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, cast

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from weighttogo.goals.infrastructure.models import GoalModel


def _register_and_login(client: TestClient, email: str = "detect@example.com") -> None:
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "ValidPass123!", "display_name": "Detect User"},
    )


def _create_goal(
    client: TestClient,
    start: float = 200.0,
    target: float = 150.0,
    goal_type: str = "lose",
) -> None:
    client.post(
        "/api/v1/goals",
        json={
            "goal_type": goal_type,
            "target_value": target,
            "target_unit": "lbs",
            "start_value": start,
            "target_date": None,
        },
    )


def _post_entry(client: TestClient, weight: float, obs_date: str = "2026-01-10") -> dict[str, Any]:
    resp = client.post(
        "/api/v1/weight-entries",
        json={"weight_value": weight, "weight_unit": "lbs", "observation_date": obs_date},
    )
    assert resp.status_code == 201, resp.json()
    return cast(dict[str, Any], resp.json())


# ── Response shape ────────────────────────────────────────────────────────────


def test_weight_entry_response_includes_newly_earned_achievements_field(
    client: TestClient,
) -> None:
    _register_and_login(client)
    data = _post_entry(client, 198.0)
    assert "newly_earned_achievements" in data


def test_weight_entry_without_active_goal_returns_empty_achievements(
    client: TestClient,
) -> None:
    _register_and_login(client, "nogoal@example.com")
    data = _post_entry(client, 198.0)
    assert data["newly_earned_achievements"] == []


# ── Milestone detection ───────────────────────────────────────────────────────


def test_weight_entry_crossing_5lb_threshold_returns_milestone(client: TestClient) -> None:
    _register_and_login(client, "milestone@example.com")
    _create_goal(client)
    # start=200, current=195 → delta=5, crosses 5 lb threshold
    data = _post_entry(client, 195.0)
    achievements = data["newly_earned_achievements"]
    assert len(achievements) == 1
    assert achievements[0]["achievement_type"] == "milestone"
    # Pydantic serialises Decimal as a string in JSON
    assert float(achievements[0]["threshold"]) == 5.0


def test_second_entry_at_same_weight_returns_no_new_achievements(client: TestClient) -> None:
    _register_and_login(client, "idempotent@example.com")
    _create_goal(client)
    _post_entry(client, 195.0, "2026-01-10")  # earns 5 lb milestone
    # Second entry at same weight on a different date — threshold already recorded
    data = _post_entry(client, 195.0, "2026-01-11")
    assert data["newly_earned_achievements"] == []


# ── Streak detection (FR-Ach-3) ───────────────────────────────────────────────


def _consecutive_dates(start_day: int, count: int) -> list[str]:
    """Return *count* consecutive ISO dates in January 2026 from *start_day*."""
    return [f"2026-01-{start_day + i:02d}" for i in range(count)]


def _backdate_active_goal(db_session: Session, when: datetime) -> None:
    """Move the active goal's ``created_at`` earlier.

    Streaks count only logging on/after the goal's creation (FR-Ach-3), so a
    goal created "now" in the test must be backdated for past-dated entries to
    fall inside the streak window.
    """
    goal = db_session.query(GoalModel).filter_by(is_active=True).first()
    assert goal is not None
    goal.created_at = when
    db_session.flush()


def test_seven_consecutive_daily_entries_earn_streak(
    client: TestClient, db_session: Session
) -> None:
    # ARRANGE: lose goal; entries at 199 lbs (delta=1) so no milestone fires
    _register_and_login(client, "streak7@example.com")
    _create_goal(client)
    _backdate_active_goal(db_session, datetime(2025, 12, 1, tzinfo=UTC))
    dates = _consecutive_dates(1, 7)  # Jan 1..7, after goal creation
    # ACT: post the first six entries, then the seventh completes the streak
    last = None
    for d in dates:
        last = _post_entry(client, 199.0, d)
    assert last is not None
    # ASSERT: the 7th POST response carries the streak(7) achievement
    streaks = [a for a in last["newly_earned_achievements"] if a["achievement_type"] == "streak"]
    assert len(streaks) == 1
    assert float(streaks[0]["threshold"]) == 7.0


def test_eighth_consecutive_entry_does_not_re_earn_seven_day_streak(
    client: TestClient, db_session: Session
) -> None:
    # ARRANGE: earn the 7-day streak first
    _register_and_login(client, "streak8@example.com")
    _create_goal(client)
    _backdate_active_goal(db_session, datetime(2025, 12, 1, tzinfo=UTC))
    for d in _consecutive_dates(1, 7):  # Jan 1..7 earns streak(7)
        _post_entry(client, 199.0, d)
    # ACT: an eighth consecutive day extends the run but 7 is already recorded
    data = _post_entry(client, 199.0, "2026-01-08")
    # ASSERT: no new streak(7) achievement (idempotent); 30 not yet reached
    streaks = [a for a in data["newly_earned_achievements"] if a["achievement_type"] == "streak"]
    assert streaks == []


# ── Goal-reached detection (FR-G-4) ──────────────────────────────────────────


def test_weight_entry_reaching_target_returns_goal_reached(client: TestClient) -> None:
    _register_and_login(client, "goalreached@example.com")
    _create_goal(client, start=200.0, target=195.0)  # small gap for easy testing
    data = _post_entry(client, 195.0)
    types = [a["achievement_type"] for a in data["newly_earned_achievements"]]
    assert "goal_reached" in types


# ── Fix 1 regression: weight entry survives when detection finds nothing new ──
# The original bug: session.rollback() in the IntegrityError handler cancelled
# the weight entry too. The real race condition (concurrent duplicate) cannot be
# reproduced without threading, but the non-race path exercises the same commit:
# when no achievements are newly earned the entry must still be persisted.


def test_weight_entry_is_persisted_when_no_new_achievements_detected(
    client: TestClient,
) -> None:
    _register_and_login(client, "persist@example.com")
    _create_goal(client)
    _post_entry(client, 195.0, "2026-01-10")  # earns 5 lb milestone
    # Second entry: nothing new to earn; verify the entry is still saved
    data = _post_entry(client, 195.0, "2026-01-11")
    assert data["entry_id"] is not None
    # Confirm the entry is retrievable (it wasn't rolled back)
    resp = client.get(f"/api/v1/weight-entries/{data['entry_id']}")
    assert resp.status_code == 200


# ── Fix 2 regression: cross-unit detection ────────────────────────────────────
# Goal in lbs, entry in kg: without unit normalisation the raw kg value is
# compared against lbs thresholds → wrong milestones.  A kg entry of ~88.45 kg
# (195 lbs) against a lbs goal starting at 200 lbs should correctly fire the
# 5 lb (≈2.27 kg) milestone.


def _create_goal_unit(
    client: TestClient,
    start: float,
    target: float,
    unit: str,
    goal_type: str = "lose",
) -> None:
    client.post(
        "/api/v1/goals",
        json={
            "goal_type": goal_type,
            "target_value": target,
            "target_unit": unit,
            "start_value": start,
            "target_date": None,
        },
    )


def _post_entry_unit(
    client: TestClient, weight: float, unit: str, obs_date: str = "2026-01-10"
) -> dict[str, Any]:
    resp = client.post(
        "/api/v1/weight-entries",
        json={"weight_value": weight, "weight_unit": unit, "observation_date": obs_date},
    )
    assert resp.status_code == 201, resp.json()
    return cast(dict[str, Any], resp.json())


def test_lbs_goal_with_kg_entry_detects_milestone_correctly(client: TestClient) -> None:
    # ARRANGE: goal in lbs (start=200, target=150); entry in kg
    _register_and_login(client, "crossunit1@example.com")
    _create_goal_unit(client, start=200.0, target=150.0, unit="lbs")
    # 195 lbs = 88.45 kg → delta_lbs = 5 → should fire the 5 lb milestone
    weight_kg = round(195.0 * 0.45359237, 4)
    data = _post_entry_unit(client, weight_kg, "kg")
    types = [a["achievement_type"] for a in data["newly_earned_achievements"]]
    assert "milestone" in types


def test_kg_goal_with_lbs_entry_detects_milestone_correctly(client: TestClient) -> None:
    # ARRANGE: goal in kg (start=90.718, ≈200 lbs; target=68.039, ≈150 lbs); entry in lbs
    _register_and_login(client, "crossunit2@example.com")
    start_kg = round(200.0 * 0.45359237, 3)  # ≈90.718 kg
    target_kg = round(150.0 * 0.45359237, 3)  # ≈68.039 kg
    _create_goal_unit(client, start=start_kg, target=target_kg, unit="kg")
    # 195 lbs → delta_lbs=5 → should fire 5 lb milestone
    data = _post_entry_unit(client, 195.0, "lbs")
    types = [a["achievement_type"] for a in data["newly_earned_achievements"]]
    assert "milestone" in types


# ── Fix 3 regression: goal is marked achieved when target is reached ──────────
# FR-G-4: the POST that reaches the target must flip is_achieved=True and
# is_active=False on the goal in the same transaction.


def test_goal_is_marked_achieved_when_target_entry_is_posted(client: TestClient) -> None:
    _register_and_login(client, "goalmark@example.com")
    _create_goal(client, start=200.0, target=195.0)
    # Entry exactly at target weight
    data = _post_entry(client, 195.0)
    assert "goal_reached" in [a["achievement_type"] for a in data["newly_earned_achievements"]]
    # Active goal should now be gone (is_active=False after mark_achieved)
    active_resp = client.get("/api/v1/goals/active")
    assert active_resp.status_code == 200
    assert active_resp.json()["goal"] is None
