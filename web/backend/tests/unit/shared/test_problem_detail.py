"""Unit tests for shared RFC-7807 build_problem_detail helper."""

from __future__ import annotations

import pytest

from weighttogo.shared.problem_detail import build_problem_detail


def test_build_problem_detail_required_fields_only() -> None:
    result = build_problem_detail(
        status=422,
        title="Validation failed",
        detail="The value is invalid.",
        instance="/api/v1/preferences/weight_unit",
    )
    assert result["type"] == "about:blank"
    assert result["title"] == "Validation failed"
    assert result["status"] == 422
    assert result["detail"] == "The value is invalid."
    assert result["instance"] == "/api/v1/preferences/weight_unit"
    assert result["errors"] is None
    assert result["request_id"] is None


def test_build_problem_detail_with_errors_and_request_id() -> None:
    errors = [{"field": "value", "code": "invalid_unit", "message": "Must be lbs or kg"}]
    result = build_problem_detail(
        status=422,
        title="Validation failed",
        detail="Invalid preference value.",
        instance="/api/v1/preferences/weight_unit",
        errors=errors,
        request_id="req-abc-123",
    )
    assert result["errors"] == errors
    assert result["request_id"] == "req-abc-123"


def test_build_problem_detail_includes_all_keys() -> None:
    result = build_problem_detail(
        status=404,
        title="Not found",
        detail="Resource does not exist.",
        instance="/api/v1/preferences",
    )
    expected_keys = {"type", "title", "status", "detail", "instance", "errors", "request_id"}
    assert set(result.keys()) == expected_keys


def test_build_problem_detail_status_is_int() -> None:
    result = build_problem_detail(
        status=422,
        title="Bad",
        detail="x",
        instance="/",
    )
    assert isinstance(result["status"], int)


@pytest.mark.parametrize("status", [400, 422, 404, 409, 500])
def test_build_problem_detail_accepts_common_status_codes(status: int) -> None:
    result = build_problem_detail(status=status, title="T", detail="D", instance="/")
    assert result["status"] == status
