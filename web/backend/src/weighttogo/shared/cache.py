"""Generic in-memory TTL cache (NFR-P-5, ADR-0023).

Framework-free, stdlib-only.  Stores each key against a value and a monotonic
expiry deadline; reads treat an expired entry as a miss and evict it lazily.

Time complexity:  get / invalidate are O(1) average (single dict op).  set is
O(1) average; when the cache is at ``maxsize`` it first evicts, which is O(n)
worst case (n = maxsize) to scan for an expired entry, otherwise O(1) to drop
the oldest insertion.
Space complexity: O(maxsize) — growth is bounded by the configured cap, so a
flood of distinct keys cannot exhaust memory.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass

# Default time-to-live for cached computed values.  See ADR-0023 for rationale:
# short enough to bound staleness to seconds, long enough to absorb refresh bursts.
DEFAULT_TTL_SECONDS = 30.0

# Default upper bound on distinct live keys.  One entry per active user in a
# worker process, so 1024 comfortably covers concurrent users while capping the
# memory an unauthenticated key flood could pin (memory-DoS guard).  See ADR-0023.
DEFAULT_MAX_SIZE = 1024


@dataclass(frozen=True)
class _Entry[V]:
    """A cached value paired with its monotonic expiry deadline.

    Attributes:
        value: The cached value.
        expires_at: Monotonic-clock deadline (seconds) at and after which the
            entry is considered expired.
    """

    value: V
    expires_at: float


class TTLCache[K, V]:
    """A minimal time-to-live cache keyed by ``K`` holding values of type ``V``.

    Expiry is lazy: an entry is removed when a ``get`` finds it past its
    deadline.  The deadline uses ``time.monotonic`` so it is immune to wall-clock
    adjustments.

    Growth is bounded by ``maxsize``.  When a ``set`` would exceed the cap, the
    cache first reclaims any single expired entry (free space, no useful data
    lost); if none is expired it drops the oldest-inserted entry.  This keeps the
    structure a memory-DoS-resistant bound rather than an unbounded dict.

    Args:
        ttl_seconds: Lifetime of each entry in seconds.  Defaults to
            ``DEFAULT_TTL_SECONDS``.
        maxsize: Maximum number of distinct live keys.  Defaults to
            ``DEFAULT_MAX_SIZE``.  Must be >= 1.
        now: Monotonic time source returning seconds; injectable for tests.

    Raises:
        ValueError: If ``maxsize`` is less than 1.
    """

    def __init__(
        self,
        ttl_seconds: float = DEFAULT_TTL_SECONDS,
        maxsize: int = DEFAULT_MAX_SIZE,
        now: Callable[[], float] = time.monotonic,
    ) -> None:
        """Initialise an empty cache with the given TTL, cap, and time source."""
        if maxsize < 1:
            raise ValueError("maxsize must be >= 1")
        self._ttl = ttl_seconds
        self._maxsize = maxsize
        self._now = now
        # Insertion order is significant: ``dict`` preserves it, so the first
        # key is the oldest insertion — the fallback eviction victim.
        self._store: dict[K, _Entry[V]] = {}

    def get(self, key: K) -> V | None:
        """Return the live value for *key*, or ``None`` on miss or expiry.

        Expiry uses ``>=`` against the monotonic deadline.  This is a magnitude
        comparison, never a float-equality test: the deadline was produced by
        adding ``ttl_seconds`` to a reading of the *same* monotonic clock, so
        ``now >= deadline`` is exact and safe at the boundary.  An expired entry
        is deleted here (lazy eviction) so memory is reclaimed without a sweeper.

        Args:
            key: The lookup key.

        Returns:
            The cached value, or ``None`` when the key is absent or expired.
        """
        entry = self._store.get(key)
        if entry is None:
            return None
        if self._now() >= entry.expires_at:
            # ``pop(key, None)`` (not ``del``) makes lazy eviction idempotent:
            # under the AnyIO threadpool that runs sync endpoints, two threads
            # can read the same expired entry and both attempt eviction; ``del``
            # would raise ``KeyError`` on the loser (a 500), whereas ``pop`` is a
            # no-op.  Mirrors ``invalidate``.
            self._store.pop(key, None)
            return None
        return entry.value

    def set(self, key: K, value: V) -> None:
        """Store *value* under *key* with a fresh TTL deadline.

        Enforces the ``maxsize`` bound: when inserting a *new* key into a full
        cache, one entry is evicted first — an expired entry if any, otherwise
        the oldest insertion.  Overwriting an existing key never grows the store,
        so it skips eviction.

        Args:
            key: The key to store under.
            value: The value to cache.
        """
        if key not in self._store and len(self._store) >= self._maxsize:
            self._evict_one()
        self._store[key] = _Entry(value=value, expires_at=self._now() + self._ttl)

    def _evict_one(self) -> None:
        """Free one slot, preferring an expired entry over the oldest live one.

        Expired entries hold no useful data, so reclaiming one is lossless.  Only
        when nothing is expired do we drop the oldest insertion (``dict`` keeps
        insertion order, so the first key is the oldest).  Scanning for an expired
        entry is O(n) worst case in the size of the cache, incurred only on a
        ``set`` into a full cache.
        """
        now = self._now()
        for candidate, entry in self._store.items():
            if now >= entry.expires_at:
                self._store.pop(candidate, None)
                return
        oldest = next(iter(self._store))
        self._store.pop(oldest, None)

    def invalidate(self, key: K) -> None:
        """Remove *key* from the cache; a no-op when the key is absent.

        Args:
            key: The key to evict.
        """
        self._store.pop(key, None)

    def clear(self) -> None:
        """Remove all entries from the cache."""
        self._store.clear()
