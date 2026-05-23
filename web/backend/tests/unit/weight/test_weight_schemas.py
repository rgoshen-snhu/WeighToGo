"""Unit tests for weight_tracking interface Pydantic schemas (subtask 16)."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest


def _valid_payload(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "weight_value": Decimal("175.50"),
        "weight_unit": "lbs",
        "observation_date": date.today().isoformat(),
        "notes": None,
    }
    base.update(overrides)
    return base


# ── weight_value ──────────────────────────────────────────────────────────────


def test_schema_accepts_positive_weight_value() -> None:
    from weighttogo.weight_tracking.interface.schemas import WeightEntryRequest

    req = WeightEntryRequest(**_valid_payload(weight_value=Decimal("175.50")))  # type: ignore[arg-type]
    assert req.weight_value == Decimal("175.50")


def test_schema_rejects_zero_weight_value() -> None:
    from pydantic import ValidationError

    from weighttogo.weight_tracking.interface.schemas import WeightEntryRequest

    with pytest.raises(ValidationError):
        WeightEntryRequest(**_valid_payload(weight_value=Decimal("0")))  # type: ignore[arg-type]


def test_schema_rejects_negative_weight_value() -> None:
    from pydantic import ValidationError

    from weighttogo.weight_tracking.interface.schemas import WeightEntryRequest

    with pytest.raises(ValidationError):
        WeightEntryRequest(**_valid_payload(weight_value=Decimal("-1")))  # type: ignore[arg-type]


def test_schema_accepts_max_weight_value() -> None:
    from weighttogo.weight_tracking.interface.schemas import WeightEntryRequest

    req = WeightEntryRequest(**_valid_payload(weight_value=Decimal("1500")))  # type: ignore[arg-type]
    assert req.weight_value == Decimal("1500")


def test_schema_rejects_above_max_weight_value() -> None:
    from pydantic import ValidationError

    from weighttogo.weight_tracking.interface.schemas import WeightEntryRequest

    with pytest.raises(ValidationError):
        WeightEntryRequest(**_valid_payload(weight_value=Decimal("1500.01")))  # type: ignore[arg-type]


# ── weight_unit ───────────────────────────────────────────────────────────────


def test_schema_accepts_lbs_unit() -> None:
    from weighttogo.weight_tracking.interface.schemas import WeightEntryRequest

    req = WeightEntryRequest(**_valid_payload(weight_unit="lbs"))  # type: ignore[arg-type]
    assert req.weight_unit == "lbs"


def test_schema_accepts_kg_unit() -> None:
    from weighttogo.weight_tracking.interface.schemas import WeightEntryRequest

    req = WeightEntryRequest(**_valid_payload(weight_unit="kg"))  # type: ignore[arg-type]
    assert req.weight_unit == "kg"


def test_schema_rejects_invalid_unit() -> None:
    from pydantic import ValidationError

    from weighttogo.weight_tracking.interface.schemas import WeightEntryRequest

    with pytest.raises(ValidationError):
        WeightEntryRequest(**_valid_payload(weight_unit="pounds"))  # type: ignore[arg-type]


# ── observation_date ──────────────────────────────────────────────────────────


def test_schema_accepts_today_as_observation_date() -> None:
    from weighttogo.weight_tracking.interface.schemas import WeightEntryRequest

    req = WeightEntryRequest(**_valid_payload(observation_date=date.today().isoformat()))  # type: ignore[arg-type]
    assert req.observation_date == date.today()


def test_schema_rejects_future_observation_date() -> None:
    from pydantic import ValidationError

    from weighttogo.weight_tracking.interface.schemas import WeightEntryRequest

    future = (date.today() + timedelta(days=1)).isoformat()
    with pytest.raises(ValidationError):
        WeightEntryRequest(**_valid_payload(observation_date=future))  # type: ignore[arg-type]


# ── notes ─────────────────────────────────────────────────────────────────────


def test_schema_accepts_none_notes() -> None:
    from weighttogo.weight_tracking.interface.schemas import WeightEntryRequest

    req = WeightEntryRequest(**_valid_payload(notes=None))  # type: ignore[arg-type]
    assert req.notes is None


def test_schema_accepts_max_length_notes() -> None:
    from weighttogo.weight_tracking.interface.schemas import WeightEntryRequest

    req = WeightEntryRequest(**_valid_payload(notes="x" * 500))  # type: ignore[arg-type]
    assert len(req.notes or "") == 500


def test_schema_rejects_notes_exceeding_500_chars() -> None:
    from pydantic import ValidationError

    from weighttogo.weight_tracking.interface.schemas import WeightEntryRequest

    with pytest.raises(ValidationError):
        WeightEntryRequest(**_valid_payload(notes="x" * 501))  # type: ignore[arg-type]
