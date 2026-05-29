"""Shared RFC-7807 Problem Details builder.

Produces a consistent ``application/problem+json`` body shape required by
SRS §9.2. Complements ``error_handlers.py`` (which handles Pydantic
``RequestValidationError`` globally); domain-exception 422/4xx bodies
in routers use this helper instead of hand-building the dict per router.
"""

from __future__ import annotations


def build_problem_detail(
    *,
    status: int,
    title: str,
    detail: str,
    instance: str,
    errors: list[dict[str, str]] | None = None,
    request_id: str | None = None,
) -> dict[str, object]:
    """Return an RFC-7807 Problem Details dict.

    Args:
        status:     HTTP status code (e.g. 422).
        title:      Short human-readable summary of the problem type.
        detail:     Human-readable explanation of this specific occurrence.
        instance:   URI reference for the specific request (e.g. request.url.path).
        errors:     Optional list of field-level error dicts {field, code, message}.
        request_id: Optional correlation ID from the x-request-id header.

    Returns:
        Dict with keys: type, title, status, detail, instance, errors, request_id.
    """
    return {
        "type": "about:blank",
        "title": title,
        "status": status,
        "detail": detail,
        "instance": instance,
        "errors": errors,
        "request_id": request_id,
    }
