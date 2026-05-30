"""Unit tests for the shared TTL cache (NFR-P-5, ADR-0023)."""

from __future__ import annotations

from weighttogo.shared.cache import DEFAULT_MAX_SIZE, DEFAULT_TTL_SECONDS, TTLCache


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


def test_get_returns_none_after_ttl_expires() -> None:
    # ARRANGE — controllable monotonic clock
    clock = {"t": 1000.0}
    cache: TTLCache[int, str] = TTLCache(ttl_seconds=30.0, now=lambda: clock["t"])
    cache.set(1, "summary")

    # ACT — advance past the TTL
    clock["t"] = 1031.0

    # ASSERT
    assert cache.get(1) is None


def test_get_returns_value_just_before_ttl_expires() -> None:
    # ARRANGE
    clock = {"t": 1000.0}
    cache: TTLCache[int, str] = TTLCache(ttl_seconds=30.0, now=lambda: clock["t"])
    cache.set(1, "summary")

    # ACT — still inside the window
    clock["t"] = 1029.0

    # ASSERT
    assert cache.get(1) == "summary"


def test_expired_entry_is_evicted_not_just_hidden() -> None:
    # ARRANGE — prove lazy eviction frees storage, not only hides the value
    clock = {"t": 1000.0}
    cache: TTLCache[int, str] = TTLCache(ttl_seconds=30.0, now=lambda: clock["t"])
    cache.set(1, "summary")

    # ACT — read after expiry triggers eviction
    clock["t"] = 1031.0
    assert cache.get(1) is None

    # ASSERT — the underlying store no longer holds the key
    assert 1 not in cache._store  # noqa: SLF001 — white-box storage check


def test_concurrent_eviction_of_same_expired_key_does_not_raise() -> None:
    # ARRANGE — reproduce the TOCTOU window: between the expiry check and the
    # eviction, a second thread (simulated here via the injected clock) removes
    # the same expired key.  A non-atomic ``del`` would raise KeyError -> 500.
    cache: TTLCache[int, str] = TTLCache(ttl_seconds=30.0, now=lambda: 1000.0)
    cache.set(1, "summary")

    def racing_now() -> float:
        # Drop the key as if another thread already evicted it, then report a
        # time past the deadline so this call also attempts to evict it.
        cache._store.pop(1, None)  # noqa: SLF001 — simulate concurrent eviction
        return 2000.0

    cache._now = racing_now  # noqa: SLF001 — inject the racing clock

    # ACT / ASSERT — the second eviction must be a no-op, not a KeyError
    assert cache.get(1) is None


def test_invalidate_removes_entry() -> None:
    # ARRANGE
    cache: TTLCache[int, str] = TTLCache()
    cache.set(1, "summary")

    # ACT
    cache.invalidate(1)

    # ASSERT
    assert cache.get(1) is None


def test_invalidate_absent_key_is_noop() -> None:
    # ARRANGE
    cache: TTLCache[int, str] = TTLCache()

    # ACT — must not raise
    cache.invalidate(99)

    # ASSERT
    assert cache.get(99) is None


def test_clear_removes_all_entries() -> None:
    # ARRANGE
    cache: TTLCache[int, str] = TTLCache()
    cache.set(1, "a")
    cache.set(2, "b")

    # ACT
    cache.clear()

    # ASSERT
    assert cache.get(1) is None
    assert cache.get(2) is None


def test_set_overwrites_existing_value_and_refreshes_ttl() -> None:
    # ARRANGE
    clock = {"t": 1000.0}
    cache: TTLCache[int, str] = TTLCache(ttl_seconds=30.0, now=lambda: clock["t"])
    cache.set(1, "old")

    # ACT — overwrite later resets the deadline to 1050
    clock["t"] = 1020.0
    cache.set(1, "new")
    clock["t"] = 1045.0

    # ASSERT — still live and holding the new value
    assert cache.get(1) == "new"


def test_invalidate_one_key_leaves_others() -> None:
    # ARRANGE
    cache: TTLCache[int, str] = TTLCache()
    cache.set(1, "a")
    cache.set(2, "b")

    # ACT
    cache.invalidate(1)

    # ASSERT
    assert cache.get(1) is None
    assert cache.get(2) == "b"


def test_default_ttl_constant_is_thirty_seconds() -> None:
    assert DEFAULT_TTL_SECONDS == 30.0


def test_default_maxsize_constant_is_set() -> None:
    assert DEFAULT_MAX_SIZE == 1024


def test_set_never_grows_past_maxsize() -> None:
    # ARRANGE — a small bounded cache
    cache: TTLCache[int, str] = TTLCache(maxsize=3)

    # ACT — insert more distinct keys than the cap
    for key in range(10):
        cache.set(key, f"v{key}")

    # ASSERT — storage is bounded, never unbounded growth
    assert len(cache._store) == 3  # noqa: SLF001 — white-box size check


def test_eviction_drops_expired_entries_before_oldest_live() -> None:
    # ARRANGE — fill the cache, then expire the two oldest entries
    clock = {"t": 1000.0}
    cache: TTLCache[int, str] = TTLCache(ttl_seconds=30.0, maxsize=3, now=lambda: clock["t"])
    cache.set(1, "a")  # expires at 1030
    cache.set(2, "b")  # expires at 1030
    clock["t"] = 1010.0
    cache.set(3, "c")  # expires at 1040, newest live entry

    # ACT — advance so 1 and 2 are expired, then insert into a full cache
    clock["t"] = 1031.0
    cache.set(4, "d")

    # ASSERT — an expired entry was reclaimed (not the live newest); still bounded
    assert len(cache._store) <= 3  # noqa: SLF001
    assert cache.get(3) == "c"  # live entry preserved
    assert cache.get(4) == "d"  # newest insert present


def test_eviction_drops_oldest_when_none_expired() -> None:
    # ARRANGE — fill to capacity with all-live entries
    clock = {"t": 1000.0}
    cache: TTLCache[int, str] = TTLCache(ttl_seconds=100.0, maxsize=3, now=lambda: clock["t"])
    cache.set(1, "a")  # oldest
    clock["t"] = 1001.0
    cache.set(2, "b")
    clock["t"] = 1002.0
    cache.set(3, "c")

    # ACT — insert a fourth while all three are still live
    clock["t"] = 1003.0
    cache.set(4, "d")

    # ASSERT — the oldest live entry (1) was evicted, newer ones kept
    assert len(cache._store) == 3  # noqa: SLF001
    assert cache.get(1) is None
    assert cache.get(2) == "b"
    assert cache.get(3) == "c"
    assert cache.get(4) == "d"
