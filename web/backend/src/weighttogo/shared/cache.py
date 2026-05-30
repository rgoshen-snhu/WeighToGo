"""Generic in-memory TTL cache (NFR-P-5, ADR-0023).

Framework-free, stdlib-only.  Stores each key against a value and a monotonic
expiry deadline; reads treat an expired entry as a miss and evict it lazily.

Time complexity:  get / set / invalidate are O(1) average (single dict op).
Space complexity: O(k) where k is the number of distinct live keys.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass

# Default time-to-live for cached computed values.  See ADR-0023 for rationale:
# short enough to bound staleness to seconds, long enough to absorb refresh bursts.
DEFAULT_TTL_SECONDS = 30.0


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

    Args:
        ttl_seconds: Lifetime of each entry in seconds.  Defaults to
            ``DEFAULT_TTL_SECONDS``.
        now: Monotonic time source returning seconds; injectable for tests.
    """

    def __init__(
        self,
        ttl_seconds: float = DEFAULT_TTL_SECONDS,
        now: Callable[[], float] = time.monotonic,
    ) -> None:
        """Initialise an empty cache with the given TTL and time source."""
        self._ttl = ttl_seconds
        self._now = now
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
            del self._store[key]
            return None
        return entry.value

    def set(self, key: K, value: V) -> None:
        """Store *value* under *key* with a fresh TTL deadline.

        Args:
            key: The key to store under.
            value: The value to cache.
        """
        self._store[key] = _Entry(value=value, expires_at=self._now() + self._ttl)

    def invalidate(self, key: K) -> None:
        """Remove *key* from the cache; a no-op when the key is absent.

        Args:
            key: The key to evict.
        """
        self._store.pop(key, None)

    def clear(self) -> None:
        """Remove all entries from the cache."""
        self._store.clear()
