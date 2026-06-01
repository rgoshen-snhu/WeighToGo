"""Integration tests: achievement detection on weight-entry create (FR-Ach-1/2, FR-G-4)."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from typing import TypedDict, cast

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from weighttogo.goals.infrastructure.models import GoalModel


class _Achievement(TypedDict):
    achievement_type: str
    threshold: str | float


class _WeightEntryResponse(TypedDict, total=False):
    entry_id: int
    newly_earned_achievements: list[_Achievement]


def _register_and_login(client: TestClient, email: str = "detect@example.com") -> None:
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "ValidPass123!", "display_name": "Detect User"},
    )


def _create_goal(
    client: TestClient,
    start: float = 200.0,
    target: float = 150.0,
    unit: str = "lbs",
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


def _post_entry(
    client: TestClient,
    weight: float,
    obs_date: str = "2026-01-10",
    unit: str = "lbs",
    notes: str | None = None,
) -> _WeightEntryResponse:
    resp = client.post(
        "/api/v1/weight-entries",
        json={
            "weight_value": weight,
            "weight_unit": unit,
            "observation_date": obs_date,
            "notes": notes,
        },
    )
    assert resp.status_code == 201, resp.json()
    return cast(_WeightEntryResponse, resp.json())


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


def test_lbs_goal_with_kg_entry_detects_milestone_correctly(client: TestClient) -> None:
    # ARRANGE: goal in lbs (start=200, target=150); entry in kg
    _register_and_login(client, "crossunit1@example.com")
    _create_goal(client, start=200.0, target=150.0, unit="lbs")
    # 195 lbs = 88.45 kg → delta_lbs = 5 → should fire the 5 lb milestone
    weight_kg = round(195.0 * 0.45359237, 4)
    data = _post_entry(client, weight_kg, unit="kg")
    types = [a["achievement_type"] for a in data["newly_earned_achievements"]]
    assert "milestone" in types


def test_kg_goal_with_lbs_entry_detects_milestone_correctly(client: TestClient) -> None:
    # ARRANGE: goal in kg (start=90.718, ≈200 lbs; target=68.039, ≈150 lbs); entry in lbs
    _register_and_login(client, "crossunit2@example.com")
    start_kg = round(200.0 * 0.45359237, 3)  # ≈90.718 kg
    target_kg = round(150.0 * 0.45359237, 3)  # ≈68.039 kg
    _create_goal(client, start=start_kg, target=target_kg, unit="kg")
    # 195 lbs → delta_lbs=5 → should fire 5 lb milestone
    data = _post_entry(client, 195.0, unit="lbs")
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


# ── Contract-locking tests: create-only & permanent write-flow (ADR-0026) ────
#
# Achievements are awarded only on weight-entry CREATE and are permanent — they
# are never recomputed on PUT or revoked on DELETE.  These tests lock that
# contract by asserting the invariant from the outside via HTTP; any future
# accidental introduction of achievement side-effects in the PUT/DELETE
# handlers will surface here as a red test.


def _put_entry(
    client: TestClient,
    entry_id: int,
    weight_value: float,
    observation_date: str,
) -> dict[str, object]:
    """PUT an existing weight entry and return the response body."""
    resp = client.put(
        f"/api/v1/weight-entries/{entry_id}",
        json={
            "weight_value": weight_value,
            "weight_unit": "lbs",
            "observation_date": observation_date,
            "notes": None,
        },
    )
    assert resp.status_code == 200, resp.json()
    return cast(dict[str, object], resp.json())


def _list_achievements(client: TestClient) -> list[dict[str, object]]:
    """Return the items list from GET /api/v1/achievements."""
    resp = client.get("/api/v1/achievements")
    assert resp.status_code == 200, resp.json()
    return cast(list[dict[str, object]], resp.json()["items"])


def _list_goals(client: TestClient) -> list[dict[str, object]]:
    """Return the goals list from GET /api/v1/goals."""
    resp = client.get("/api/v1/goals")
    assert resp.status_code == 200, resp.json()
    return cast(list[dict[str, object]], resp.json()["goals"])


def test_updating_entry_up_across_milestone_threshold_records_no_new_achievement(
    client: TestClient,
) -> None:
    """PUT that crosses a milestone threshold does not award a new achievement."""
    # ARRANGE
    _register_and_login(client, "contract-put-milestone@example.com")
    _create_goal(client, start=200.0, target=150.0)
    # 196 lbs → 4 lb lost; below the 5 lb milestone threshold
    entry = _post_entry(client, 196.0, "2026-02-01")
    assert entry["entry_id"] is not None
    assert _list_achievements(client) == []

    # ACT: update to 193 lbs → 7 lb lost (crosses 5 lb threshold)
    _put_entry(client, entry["entry_id"], 193.0, "2026-02-01")

    # ASSERT: milestone was NOT awarded on update — still 0 achievements
    assert _list_achievements(client) == []


def test_updating_entry_below_target_does_not_revoke_goal_reached_achievement(
    client: TestClient,
) -> None:
    """PUT that moves weight above target does not revoke the GOAL_REACHED achievement."""
    # ARRANGE
    _register_and_login(client, "contract-put-revoke@example.com")
    _create_goal(client, start=200.0, target=195.0)
    # 195.0 lbs exactly reaches goal → earns GOAL_REACHED
    entry = _post_entry(client, 195.0, "2026-02-01")
    assert entry["entry_id"] is not None
    achievements_before = _list_achievements(client)
    count_before = len(achievements_before)
    assert count_before >= 1

    # ACT: update to 196 lbs (above target — goal "un-reached" from data view)
    _put_entry(client, entry["entry_id"], 196.0, "2026-02-01")

    # ASSERT: GOAL_REACHED row was NOT revoked
    assert len(_list_achievements(client)) == count_before


def test_updating_entry_below_target_leaves_goal_is_achieved_true(
    client: TestClient,
) -> None:
    """PUT that moves weight above target does not clear the goal's is_achieved flag."""
    # ARRANGE
    _register_and_login(client, "contract-put-achieved@example.com")
    _create_goal(client, start=200.0, target=195.0)
    entry = _post_entry(client, 195.0, "2026-02-01")
    assert entry["entry_id"] is not None
    # Confirm goal is achieved after the entry
    goals_before = _list_goals(client)
    assert len(goals_before) == 1
    assert goals_before[0]["is_achieved"] is True

    # ACT: update to 196 lbs (above target)
    _put_entry(client, entry["entry_id"], 196.0, "2026-02-01")

    # ASSERT: goal achieved state NOT cleared
    goals_after = _list_goals(client)
    assert len(goals_after) == 1
    assert goals_after[0]["is_achieved"] is True


def test_deleting_goal_reaching_entry_does_not_revoke_achievements(
    client: TestClient,
) -> None:
    """DELETE of the entry that earned achievements does not revoke those achievements."""
    # ARRANGE
    _register_and_login(client, "contract-del-revoke@example.com")
    _create_goal(client, start=200.0, target=195.0)
    # 195 lbs reaches goal → earns GOAL_REACHED (+ possible milestone)
    entry = _post_entry(client, 195.0, "2026-02-01")
    assert entry["entry_id"] is not None
    count_before = len(_list_achievements(client))
    assert count_before >= 1

    # ACT: delete the goal-reaching entry
    del_resp = client.delete(f"/api/v1/weight-entries/{entry['entry_id']}")
    assert del_resp.status_code == 204

    # ASSERT: achievement count unchanged — records NOT revoked
    assert len(_list_achievements(client)) == count_before


def test_deleting_goal_reaching_entry_leaves_goal_is_achieved_true(
    client: TestClient,
) -> None:
    """DELETE of the goal-reaching entry does not clear the goal's is_achieved flag."""
    # ARRANGE
    _register_and_login(client, "contract-del-achieved@example.com")
    _create_goal(client, start=200.0, target=195.0)
    entry = _post_entry(client, 195.0, "2026-02-01")
    assert entry["entry_id"] is not None

    # ACT: delete the entry
    del_resp = client.delete(f"/api/v1/weight-entries/{entry['entry_id']}")
    assert del_resp.status_code == 204

    # ASSERT: goal achieved state NOT cleared
    goals_after = _list_goals(client)
    assert len(goals_after) == 1
    assert goals_after[0]["is_achieved"] is True


def test_deleting_entry_within_recorded_streak_does_not_revoke_streak_achievement(
    client: TestClient,
    db_session: Session,
) -> None:
    """DELETE of a middle entry in a completed streak does not revoke the STREAK achievement."""
    # ARRANGE
    _register_and_login(client, "contract-del-streak@example.com")
    _create_goal(client, start=200.0, target=150.0)
    # Backdate the goal so entries spanning the past 6 days fall inside the window.
    _backdate_active_goal(db_session, datetime(2025, 12, 1, tzinfo=UTC))

    # POST 7 consecutive daily entries from 6 days ago through today.
    today = date.today()
    dates = [(today - timedelta(days=6 - i)).isoformat() for i in range(7)]
    middle_entry_id: int | None = None
    for i, obs_date in enumerate(dates):
        resp = _post_entry(client, 199.0, obs_date)
        if i == 3:  # middle entry (3 days ago)
            middle_entry_id = resp["entry_id"]

    assert middle_entry_id is not None
    # Verify at least 1 STREAK achievement was earned after the 7th entry
    achievements = _list_achievements(client)
    streak_achievements = [a for a in achievements if a["achievement_type"] == "streak"]
    assert len(streak_achievements) >= 1

    # ACT: delete the middle entry (3 days ago)
    del_resp = client.delete(f"/api/v1/weight-entries/{middle_entry_id}")
    assert del_resp.status_code == 204

    # ASSERT: STREAK achievement NOT revoked — same count as before delete
    achievements_after = _list_achievements(client)
    streak_after = [a for a in achievements_after if a["achievement_type"] == "streak"]
    assert len(streak_after) >= 1
