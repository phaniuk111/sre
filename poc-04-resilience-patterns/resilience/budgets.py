"""Per-client (per-service) retry budget: retries may be at most `ratio` of
first-attempt requests over a sliding window. (ch. 17 "Isolating Overload")."""
from __future__ import annotations

import time
from collections import deque
from typing import Callable, Deque, Tuple


class RetryBudget:
    def __init__(self, ratio: float = 0.1, window_s: float = 10.0, min_retries_per_window: int = 3, clock: Callable[[], float] = time.monotonic):
        self.ratio = ratio
        self.window_s = window_s
        self.min_retries = min_retries_per_window
        self.clock = clock
        self._events: Deque[Tuple[float, bool]] = deque()

    def _trim(self) -> None:
        cutoff = self.clock() - self.window_s
        while self._events and self._events[0][0] < cutoff:
            self._events.popleft()

    def record_request(self, is_retry: bool) -> None:
        self._events.append((self.clock(), is_retry))

    def can_retry(self) -> bool:
        self._trim()
        retries = sum(1 for _, r in self._events if r)
        firsts = len(self._events) - retries
        return retries < max(self.min_retries, self.ratio * firsts)
