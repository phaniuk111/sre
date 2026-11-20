"""Exponential backoff with full jitter.

Without jitter, every client that was shed at the same moment retries at the
same moment: a synchronized thundering herd. Full jitter spreads retries
uniformly in [0, cap]. The AWS SDKs use the same idea in their 'standard'
and 'adaptive' retry modes.
"""
from __future__ import annotations

import random
import time
from typing import Callable, Optional, Tuple, Type, TypeVar

from .budgets import RetryBudget

T = TypeVar("T")


def backoff_with_jitter(attempt: int, base: float = 0.1, cap: float = 20.0, rng: random.Random = random) -> float:
    return rng.uniform(0, min(cap, base * (2 ** attempt)))


def retry(
    fn: Callable[[], T],
    *,
    attempts: int = 3,
    retry_on: Tuple[Type[BaseException], ...] = (Exception,),
    budget: Optional[RetryBudget] = None,
    sleep: Callable[[float], None] = time.sleep,
    base: float = 0.1,
    cap: float = 20.0,
) -> T:
    """Retry `fn` with jittered backoff, but only while the retry budget allows it.

    Retries multiply load: with 3 attempts at each of 3 layers, one user request
    can become 27 backend requests. A per-client budget (e.g. retries <= 10% of
    requests) stops retries from turning an overload into a cascade.
    """
    last_exc: Optional[BaseException] = None
    for attempt in range(attempts):
        if budget:
            budget.record_request(is_retry=attempt > 0)
        try:
            return fn()
        except retry_on as exc:  # noqa: PERF203
            last_exc = exc
            if getattr(exc, "retryable", True) is False:
                raise
            if attempt == attempts - 1:
                break
            if budget and not budget.can_retry():
                break
            sleep(backoff_with_jitter(attempt, base, cap))
    assert last_exc is not None
    raise last_exc
