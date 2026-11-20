"""Client-side adaptive throttling (ch. 17, and ch. 21 of the 1st edition).

The client tracks, over a trailing window:
    requests = attempts made by the application layer
    accepts  = attempts the backend accepted
and rejects new requests *locally* with probability

    p_reject = max(0, (requests - K * accepts) / (requests + 1))

K = 2 means "allow twice as many requests as the backend has been accepting".
When the backend is healthy, accepts ~= requests and p_reject ~= 0. When it is
shedding load, the client stops sending traffic that will just be rejected and
the backend spends nothing on it. Use it per error category and respect
criticality: never throttle CRITICAL traffic as hard as background traffic.

AWS analogue: botocore `retries = {"mode": "adaptive"}` adds a client-side
token bucket that slows down when it sees throttling errors.
"""
from __future__ import annotations

import random
import time
from collections import deque
from typing import Callable, Deque, Tuple


class AdaptiveThrottler:
    def __init__(self, k: float = 2.0, window_s: float = 120.0, clock: Callable[[], float] = time.monotonic, rng: random.Random = random):
        self.k = k
        self.window_s = window_s
        self.clock = clock
        self.rng = rng
        self._events: Deque[Tuple[float, bool]] = deque()  # (t, accepted)

    def _trim(self) -> None:
        cutoff = self.clock() - self.window_s
        while self._events and self._events[0][0] < cutoff:
            self._events.popleft()

    def reject_probability(self) -> float:
        self._trim()
        requests = len(self._events)
        accepts = sum(1 for _, a in self._events if a)
        return max(0.0, (requests - self.k * accepts) / (requests + 1))

    def should_send(self) -> bool:
        return self.rng.random() >= self.reject_probability()

    def record(self, accepted: bool) -> None:
        self._events.append((self.clock(), accepted))
