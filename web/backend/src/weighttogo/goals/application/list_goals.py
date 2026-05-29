"""ListGoals use case (FR-G-5 list endpoint)."""

from __future__ import annotations

from dataclasses import dataclass

from weighttogo.goals.domain.entities import Goal
from weighttogo.goals.domain.ports import IGoalRepository

_DEFAULT_LIMIT: int = 50
_MAX_LIMIT: int = 100


@dataclass(frozen=True)
class ListGoalsCommand:
    """Input for the ListGoals use case.

    Attributes:
        user_id: The requesting user's ID.
        limit: Maximum goals to return.  Capped at 100 to prevent unbounded
            DB reads on accounts with large goal histories.
    """

    user_id: int
    limit: int = _DEFAULT_LIMIT


class ListGoals:
    """Return all goals (active and historical) for a user.

    Args:
        goal_repo: The goal repository port.
    """

    def __init__(self, goal_repo: IGoalRepository) -> None:
        """Initialise with the goal repository port."""
        self._repo = goal_repo

    def execute(self, command: ListGoalsCommand) -> list[Goal]:
        """Execute the use case.

        Args:
            command: The command carrying the user ID and page size.

        Returns:
            At most ``command.limit`` goals for the user, newest first.
        """
        effective_limit = min(command.limit, _MAX_LIMIT)
        return self._repo.list_for_user(command.user_id, limit=effective_limit)
