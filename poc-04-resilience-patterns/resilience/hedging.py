"""Request hedging (ch. 9 'Increasing resilience with hedging', appendix E).

Send to the primary; if no answer within `hedge_after_s` (often ~p95 latency),
send the same idempotent request to a second replica and take the first
success. Availability: 1 - p_fail(A) * p_fail(B) if failures are independent.
Only hedge IDEMPOTENT reads, and cap the extra load (it adds roughly 5% load if
you hedge at p95).
"""
from __future__ import annotations

import concurrent.futures as cf
from typing import Callable, Sequence, TypeVar

T = TypeVar("T")


def hedged_call(backends: Sequence[Callable[[], T]], hedge_after_s: float, pool: cf.ThreadPoolExecutor) -> T:
    if not backends:
        raise ValueError("need at least one backend")
    futures = [pool.submit(backends[0])]
    errors = []
    done, _ = cf.wait(futures, timeout=hedge_after_s)
    if not done or futures[0].exception():
        futures += [pool.submit(b) for b in backends[1:]]
    pending = set(futures)
    while pending:
        done, pending = cf.wait(pending, return_when=cf.FIRST_COMPLETED)
        for f in done:
            if f.exception() is None:
                for p in pending:
                    p.cancel()
                return f.result()
            errors.append(f.exception())
    raise errors[-1]
