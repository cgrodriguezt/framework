from __future__ import annotations
import time
from collections import defaultdict, deque

class MemoryRateLimitStore:

    # Using __slots__ to reduce memory overhead since we expect many instances.
    __slots__ = ("__storage", "__ticks")

    # Trigger a GC pass every this many calls to ``hit``.
    _GC_INTERVAL: int = 1_000

    def __init__(self) -> None:
        """Initialize an empty rate-limit store.

        Returns
        -------
        None
        """
        self.__storage: dict[str, deque[float]] = defaultdict(deque)
        # Counter that drives periodic removal of empty buckets.
        self.__ticks: int = 0

    async def hit( # NOSONAR
        self,
        key: str,
        limit: int,
        window: int,
    ) -> bool:
        """Record a request attempt and decide whether it is allowed.

        Implements a **sliding-window** algorithm: only timestamps
        within the last ``window`` seconds are counted.

        Parameters
        ----------
        key : str
            Unique identifier for the rate-limited entity (e.g. IP,
            user id, route).
        limit : int
            Maximum number of requests allowed within ``window``.
        window : int
            Length of the sliding window in seconds.

        Returns
        -------
        bool
            ``True`` when the request is within the limit,
            ``False`` when the quota is exceeded.
        """
        # monotonic() is immune to wall-clock adjustments and slightly
        # faster than time() for relative comparisons.
        now: float = time.monotonic()
        cutoff: float = now - window
        bucket: deque[float] = self.__storage[key]

        # Evict timestamps that have fallen outside the window (O(1) each).
        while bucket and bucket[0] <= cutoff:
            bucket.popleft()

        count: int = len(bucket)
        if count >= limit:
            return False

        bucket.append(now)

        # Lazily remove empty buckets to prevent unbounded memory growth.
        self.__ticks += 1
        if self.__ticks >= self._GC_INTERVAL:
            self.__ticks = 0
            self.__gc()

        return True

    def __gc(self) -> None:
        """Evict keys whose buckets have been fully drained.

        Called automatically every ``_GC_INTERVAL`` hits; may also be
        invoked explicitly when an external caller needs to reclaim
        memory immediately.

        Returns
        -------
        None
        """
        empty_keys = [k for k, v in self.__storage.items() if not v]
        for k in empty_keys:
            del self.__storage[k]

