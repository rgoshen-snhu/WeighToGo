"""Unit tests for the WeightEntry domain entity (subtasks 2–3)."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal

from weighttogo.weight_tracking.domain.entities import WeightEntry


def _make_entry(**kwargs: object) -> WeightEntry:

    defaults: dict[str, object] = {
        "entry_id": 1,
        "user_id": 42,
        "weight_value": Decimal("175.50"),
        "weight_unit": "lbs",
        "observation_date": date(2026, 5, 20),
        "notes": None,
        "created_at": datetime(2026, 5, 20, 12, 0, tzinfo=UTC),
        "updated_at": datetime(2026, 5, 20, 12, 0, tzinfo=UTC),
        "is_deleted": False,
        "deleted_at": None,
    }
    defaults.update(kwargs)
    return WeightEntry(**defaults)  # type: ignore[arg-type]


# ── Construction (subtask 2) ──────────────────────────────────────────────────


def test_weight_entry_stores_weight_value() -> None:
    entry = _make_entry()
    assert entry.weight_value == Decimal("175.50")


def test_weight_entry_stores_weight_unit() -> None:
    entry = _make_entry()
    assert entry.weight_unit == "lbs"


def test_weight_entry_stores_observation_date() -> None:
    entry = _make_entry()
    assert entry.observation_date == date(2026, 5, 20)


def test_weight_entry_defaults_is_deleted_to_false() -> None:
    entry = WeightEntry(
        entry_id=None,
        user_id=1,
        weight_value=Decimal("80.00"),
        weight_unit="kg",
        observation_date=date(2026, 5, 1),
        notes=None,
        created_at=datetime(2026, 5, 1, tzinfo=UTC),
        updated_at=datetime(2026, 5, 1, tzinfo=UTC),
    )
    assert entry.is_deleted is False
    assert entry.deleted_at is None


# ── soft_delete (subtask 3) ───────────────────────────────────────────────────


def test_soft_delete_sets_is_deleted_true() -> None:
    entry = _make_entry()
    entry.soft_delete()
    assert entry.is_deleted is True


def test_soft_delete_sets_deleted_at_to_now_utc() -> None:
    before = datetime.now(UTC)
    entry = _make_entry()
    entry.soft_delete()
    assert entry.deleted_at is not None
    assert entry.deleted_at >= before


def test_soft_delete_is_idempotent() -> None:
    entry = _make_entry()
    entry.soft_delete()
    first_deleted_at = entry.deleted_at
    entry.soft_delete()
    # Second call must not change deleted_at
    assert entry.deleted_at == first_deleted_at
    assert entry.is_deleted is True
