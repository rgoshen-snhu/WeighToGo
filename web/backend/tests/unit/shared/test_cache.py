"""Unit tests for the shared TTL cache (NFR-P-5, ADR-0023)."""

from __future__ import annotations

from weighttogo.shared.cache import TTLCache


def test_get_returns_none_on_miss() -> None:
    # ARRANGE
    cache: TTLCache[int, str] = TTLCache()

    # ACT / ASSERT
    assert cache.get(1) is None


def test_get_returns_value_after_set_hit() -> None:
    # ARRANGE
    cache: TTLCache[int, str] = TTLCache()

    # ACT
    cache.set(1, "summary")

    # ASSERT
    assert cache.get(1) == "summary"
