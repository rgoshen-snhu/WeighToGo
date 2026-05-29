"""Unit tests for the preferences interface schemas (P3-1 — strict types)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from weighttogo.preferences.interface.schemas import UpdatePreferenceRequest


class TestUpdatePreferenceRequestStrict:
    def test_accepts_json_bool_true(self) -> None:
        req = UpdatePreferenceRequest(value=True)
        assert req.value is True

    def test_accepts_json_bool_false(self) -> None:
        req = UpdatePreferenceRequest(value=False)
        assert req.value is False

    def test_accepts_string_lbs(self) -> None:
        req = UpdatePreferenceRequest(value="lbs")
        assert req.value == "lbs"

    def test_accepts_string_true(self) -> None:
        req = UpdatePreferenceRequest(value="true")
        assert req.value == "true"

    def test_rejects_integer_one(self) -> None:
        """JSON number 1 must not coerce to True (strict mode).

        Uses model_validate (raw-dict path) to replicate JSON deserialization,
        which is the only realistic route for int inputs.
        """
        with pytest.raises(ValidationError):
            UpdatePreferenceRequest.model_validate({"value": 1})

    def test_rejects_integer_zero(self) -> None:
        """JSON number 0 must not coerce to False (strict mode)."""
        with pytest.raises(ValidationError):
            UpdatePreferenceRequest.model_validate({"value": 0})
