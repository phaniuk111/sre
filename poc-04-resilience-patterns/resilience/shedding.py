"""Server-side, criticality-aware load shedding (ch. 15 & 17).

Design expectations from the book:
  * detect overload from objective signals (queue length, in-flight, memory)
  * label traffic by criticality and shed the least critical first
  * return an explicit 'overloaded' error that says whether to retry
    (HTTP 503 + Retry-After / gRPC RESOURCE_EXHAUSTED)
  * reject EARLY: a request rejected at the door costs almost nothing; one that
    times out after doing half its work costs everything.
"""
from __future__ import annotations

from enum import IntEnum
from typing import Callable, Optional


class Criticality(IntEnum):
    # Lower value = shed first
    SHEDDABLE = 0        # batch, prefetch, analytics
    SHEDDABLE_PLUS = 1   # background user-visible (thumbnails)
    CRITICAL = 2         # default interactive traffic
    CRITICAL_PLUS = 3    # checkout/payment, health checks of the LB


class OverloadedError(RuntimeError):
    status = 503

    def __init__(self, retry_after_s: Optional[float] = 1.0, retryable: bool = True):
        super().__init__("overloaded")
        self.retry_after_s = retry_after_s
        self.retryable = retryable


class LoadShedder:
    """Admits requests while utilisation < limit for their criticality band."""

    # utilisation thresholds above which each band is rejected
    DEFAULT_LIMITS = {
        Criticality.SHEDDABLE: 0.70,
        Criticality.SHEDDABLE_PLUS: 0.80,
        Criticality.CRITICAL: 0.95,
        Criticality.CRITICAL_PLUS: 1.00,
    }

    def __init__(self, max_in_flight: int, limits=None, queue_len: Callable[[], int] = lambda: 0, max_queue: int = 100):
        self.max_in_flight = max_in_flight
        self.limits = limits or self.DEFAULT_LIMITS
        self.in_flight = 0
        self.queue_len = queue_len
        self.max_queue = max_queue
        self.shed_count = {c: 0 for c in Criticality}

    @property
    def utilisation(self) -> float:
        return max(self.in_flight / self.max_in_flight, self.queue_len() / self.max_queue)

    def admit(self, criticality: Criticality) -> None:
        if self.utilisation >= self.limits[criticality]:
            self.shed_count[criticality] += 1
            # Sheddable traffic is told not to retry soon; critical traffic may retry.
            raise OverloadedError(retry_after_s=5.0 if criticality <= Criticality.SHEDDABLE_PLUS else 1.0,
                                  retryable=criticality >= Criticality.CRITICAL)
        self.in_flight += 1

    def release(self) -> None:
        self.in_flight = max(0, self.in_flight - 1)
