"""Sliding-window per-user rate limiter."""
import time
from collections import defaultdict


class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int) -> None:
        self.max_requests = max_requests
        self.window = window_seconds
        self._buckets: dict[int, list[float]] = defaultdict(list)

    def hit(self, user_id: int) -> bool:
        """Record a request — returns True if the user is over the limit."""
        now = time.time()
        bucket = [t for t in self._buckets[user_id] if now - t < self.window]
        if len(bucket) >= self.max_requests:
            self._buckets[user_id] = bucket
            return True
        bucket.append(now)
        self._buckets[user_id] = bucket
        return False
