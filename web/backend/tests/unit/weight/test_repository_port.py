"""Verify IWeightEntryRepository satisfies the Protocol runtime check (subtask 4)."""

from __future__ import annotations


def test_iweight_entry_repository_is_runtime_checkable() -> None:
    from weighttogo.weight_tracking.domain.ports import IWeightEntryRepository

    assert hasattr(IWeightEntryRepository, "__protocol_attrs__") or hasattr(
        IWeightEntryRepository, "_is_protocol"
    )


def test_concrete_class_satisfying_port_passes_isinstance_check() -> None:
    """A concrete implementation with all methods passes isinstance."""
    from datetime import date

    from weighttogo.weight_tracking.domain.entities import WeightEntry
    from weighttogo.weight_tracking.domain.ports import IWeightEntryRepository

    class _StubRepo:
        def save(self, entry: WeightEntry) -> WeightEntry:
            return entry

        def get_by_id(self, entry_id: int, user_id: int) -> WeightEntry | None:
            return None

        def get_by_id_including_deleted(self, entry_id: int, user_id: int) -> WeightEntry | None:
            return None

        def list_for_user(
            self, user_id: int, limit: int, before: tuple[date, int] | None
        ) -> list[WeightEntry]:
            return []

        def list_for_user_in_range(self, user_id: int, start: date, end: date) -> list[WeightEntry]:
            return []

        def count_for_user(self, user_id: int) -> int:
            return 0

        def get_latest_for_user(self, user_id: int) -> WeightEntry | None:
            return None

        def exists_for_user_on_date(
            self,
            user_id: int,
            observation_date: date,
            exclude_entry_id: int | None = None,
        ) -> bool:
            return False

        def list_observation_dates(self, user_id: int) -> set[date]:
            return set()

    repo = _StubRepo()
    assert isinstance(repo, IWeightEntryRepository)
