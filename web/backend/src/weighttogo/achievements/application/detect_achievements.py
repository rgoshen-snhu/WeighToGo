"""DetectAchievements use case (FR-Ach-1, FR-Ach-2, FR-Ach-3, FR-G-4)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from decimal import Decimal

from weighttogo.achievements.domain.entities import Achievement, AchievementType
from weighttogo.achievements.domain.milestone_detector import GoalSnapshot, detect_milestones
from weighttogo.achievements.domain.ports import IAchievementRepository
from weighttogo.achievements.domain.streak_detector import (
    detect_streaks,
    streak_threshold_decimal,
)


@dataclass(frozen=True)
class DetectAchievementsCommand:
    """Input for the DetectAchievements use case.

    Attributes:
        user_id: The authenticated user's ID.
        goal_id: The active goal's primary key.
        goal_type: ``'lose'`` or ``'gain'``.
        start_value: The goal's starting weight.
        target_value: The goal's target weight.
        current_weight: The weight value from the new entry (same unit as
            start/target — the router normalises before calling this use case).
        observation_dates: Distinct dates the user has logged a weight entry,
            used for streak detection (FR-Ach-3).  Empty when streak detection
            is not requested (preserves the pre-streak call contract).
        today: The reference date for streak detection; defaults to the UTC
            date at execution time when ``None``.
        goal_created_at: The active goal's creation date.  When set, streak
            detection counts only observation dates on/after it, so a streak
            reflects consecutive logging toward *this* goal and a new goal
            cannot re-award streaks earned under a prior one.  ``None`` uses
            the full history (preserves the pre-window call contract).
    """

    user_id: int
    goal_id: int
    goal_type: str
    start_value: Decimal
    target_value: Decimal
    current_weight: Decimal
    observation_dates: frozenset[date] = field(default_factory=frozenset)
    today: date | None = None
    goal_created_at: date | None = None


class DetectAchievements:
    """Detect and persist newly earned achievements for a weight entry.

    Orchestrates:

    1. Load already-recorded milestone thresholds into a ``frozenset``
       (single DB read — O(k) space).
    2. Run ``detect_milestones()`` — O(k) pure function.
    3. Check whether the goal's target weight is now reached (FR-G-4).
    4. Detect 7/30-consecutive-day logging streaks (FR-Ach-3) when
       observation dates are supplied — O(n log n) pure function.
    5. Persist each new ``Achievement`` via the repository.
    6. Return the list of newly persisted achievements (empty if none).

    No cross-domain imports: ``GoalSnapshot`` is a ``NamedTuple`` defined in
    the achievements domain so this use case never imports
    ``weighttogo.goals`` — preserving the Clean Architecture isolation
    contract (ADR-0019).

    Args:
        achievement_repo: The achievement repository port.
    """

    def __init__(self, achievement_repo: IAchievementRepository) -> None:
        """Initialise with the achievement repository port."""
        self._repo = achievement_repo

    def execute(self, cmd: DetectAchievementsCommand) -> list[Achievement]:
        """Execute milestone and goal-reached detection.

        Args:
            cmd: Command carrying goal and weight entry fields.

        Returns:
            List of newly earned ``Achievement`` entities (may be empty).
        """
        now = datetime.now(UTC)
        newly_earned: list[Achievement] = []

        # ── 1. Milestone detection (FR-Ach-2) ────────────────────────────────
        recorded = self._repo.get_recorded_thresholds(cmd.goal_id)
        snap = GoalSnapshot(
            goal_id=cmd.goal_id,
            goal_type=cmd.goal_type,
            start_value=cmd.start_value,
            target_value=cmd.target_value,
        )
        for threshold in detect_milestones(snap, cmd.current_weight, recorded):
            ach = self._repo.save(
                Achievement(
                    achievement_id=None,
                    user_id=cmd.user_id,
                    goal_id=cmd.goal_id,
                    achievement_type=AchievementType.MILESTONE,
                    threshold=threshold,
                    earned_at=now,
                )
            )
            if ach is not None:
                newly_earned.append(ach)

        # ── 2. Goal-reached detection (FR-G-4, FR-Ach-1) ─────────────────────
        if self._goal_is_reached(cmd) and not self._repo.has_goal_reached_been_recorded(
            cmd.goal_id
        ):
            ach = self._repo.save(
                Achievement(
                    achievement_id=None,
                    user_id=cmd.user_id,
                    goal_id=cmd.goal_id,
                    achievement_type=AchievementType.GOAL_REACHED,
                    threshold=None,
                    earned_at=now,
                )
            )
            if ach is not None:
                newly_earned.append(ach)

        # ── 3. Streak detection (FR-Ach-3) ───────────────────────────────────
        if cmd.observation_dates:
            recorded_streaks = self._repo.get_recorded_streak_thresholds(cmd.goal_id)
            reference_day = cmd.today or now.date()
            # Scope the streak to logging toward THIS goal: a new goal must not
            # re-award streaks earned earlier, because the idempotency guard
            # above reads only this goal's rows.  Filtering to dates on/after
            # the goal's creation keeps the run honest to this goal.
            window = cmd.observation_dates
            if cmd.goal_created_at is not None:
                window = frozenset(d for d in cmd.observation_dates if d >= cmd.goal_created_at)
            for streak in detect_streaks(window, reference_day):
                threshold = streak_threshold_decimal(streak)
                if threshold in recorded_streaks:
                    continue
                ach = self._repo.save(
                    Achievement(
                        achievement_id=None,
                        user_id=cmd.user_id,
                        goal_id=cmd.goal_id,
                        achievement_type=AchievementType.STREAK,
                        threshold=threshold,
                        earned_at=now,
                    )
                )
                if ach is not None:
                    newly_earned.append(ach)

        return newly_earned

    def _goal_is_reached(self, cmd: DetectAchievementsCommand) -> bool:
        """Return ``True`` when *current_weight* has met or passed the target."""
        if cmd.goal_type == "lose":
            return cmd.current_weight <= cmd.target_value
        return cmd.current_weight >= cmd.target_value
