"""Circuit breaker: stop calling a dependency that is clearly failing, give it
room to recover, then probe with a few half-open requests. Combine with a
fallback (cached / degraded response) so OPTIONAL dependencies stay optional."""
from __future__ import annotations

import time
from typing import Callable, Optional, TypeVar

T = TypeVar("T")


class CircuitOpenError(RuntimeError):
    retryable = False


class CircuitBreaker:
    CLOSED, OPEN, HALF_OPEN = "closed", "open", "half_open"

    def __init__(self, failure_threshold: int = 5, reset_timeout_s: float = 30.0, half_open_max: int = 1, clock: Callable[[], float] = time.monotonic):
        self.failure_threshold = failure_threshold
        self.reset_timeout_s = reset_timeout_s
        self.half_open_max = half_open_max
        self.clock = clock
        self.state = self.CLOSED
        self.failures = 0
        self.opened_at = 0.0
        self.half_open_in_flight = 0

    def _maybe_half_open(self) -> None:
        if self.state == self.OPEN and self.clock() - self.opened_at >= self.reset_timeout_s:
            self.state = self.HALF_OPEN
            self.half_open_in_flight = 0

    def call(self, fn: Callable[[], T], fallback: Optional[Callable[[], T]] = None) -> T:
        self._maybe_half_open()
        if self.state == self.OPEN or (self.state == self.HALF_OPEN and self.half_open_in_flight >= self.half_open_max):
            if fallback:
                return fallback()
            raise CircuitOpenError("circuit open")
        if self.state == self.HALF_OPEN:
            self.half_open_in_flight += 1
        try:
            result = fn()
        except Exception:
            self._on_failure()
            if fallback:
                return fallback()
            raise
        self._on_success()
        return result

    def _on_success(self) -> None:
        self.failures = 0
        self.state = self.CLOSED

    def _on_failure(self) -> None:
        self.failures += 1
        if self.state == self.HALF_OPEN or self.failures >= self.failure_threshold:
            self.state = self.OPEN
            self.opened_at = self.clock()
