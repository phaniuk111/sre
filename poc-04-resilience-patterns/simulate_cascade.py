"""Toy discrete-time simulation of overload -> cascading failure (ch. 17).

Server: processes CAPACITY requests per tick from a FIFO queue. Requests whose
deadline has passed while queued still consume capacity when dequeued: this is
wasted work, which is exactly what kills goodput in a real cascade.

Scenario: steady demand at 80% of capacity, then a spike to 150% for 20 ticks.

Naive    : unbounded queue, clients retry every failure immediately, 3 times.
Protected: server sheds early once the queue exceeds what it can serve before
           the deadline; clients use a retry budget + adaptive throttling.

Run: python simulate_cascade.py
"""
from __future__ import annotations

import random
from collections import deque
from dataclasses import dataclass, field

from resilience import AdaptiveThrottler, RetryBudget

CAPACITY = 100
DEADLINE = 3  # ticks a request may wait before the client gives up
TICKS = 120


def demand(t: int) -> int:
    return 150 if 30 <= t < 50 else 80


@dataclass
class Result:
    goodput: list = field(default_factory=list)
    wasted: list = field(default_factory=list)
    offered: list = field(default_factory=list)


def run(protected: bool, seed: int = 1) -> Result:
    rng = random.Random(seed)
    clock = [0.0]
    budget = RetryBudget(ratio=0.1, window_s=10, clock=lambda: clock[0])
    throttler = AdaptiveThrottler(k=2.0, window_s=10, clock=lambda: clock[0], rng=rng)
    queue: deque = deque()  # (enqueue_tick, attempt)
    retries_next: list = []
    res = Result()
    for t in range(TICKS):
        clock[0] = float(t)
        arrivals = [(t, 0)] * demand(t) + retries_next
        retries_next = []
        offered = 0
        for _, attempt in arrivals:
            if protected and not throttler.should_send():
                continue  # rejected locally, costs the server nothing
            offered += 1
            if protected:
                budget.record_request(is_retry=attempt > 0)
                if len(queue) >= CAPACITY * DEADLINE:  # can't possibly serve in time -> shed now
                    throttler.record(False)
                    if attempt < 3 and budget.can_retry():
                        retries_next.append((t, attempt + 1))
                    continue
            queue.append((t, attempt))
        good = wasted = 0
        for _ in range(min(CAPACITY, len(queue))):
            enq, attempt = queue.popleft()
            if t - enq <= DEADLINE:
                good += 1
                if protected:
                    throttler.record(True)
            else:
                wasted += 1  # client already timed out: work thrown away
                if protected:
                    throttler.record(False)
                if attempt < 3 and (not protected or budget.can_retry()):
                    retries_next.append((t, attempt + 1))
        # requests still queued past deadline also trigger client retries (naive clients don't wait)
        if not protected:
            expired_waiting = sum(1 for enq, _ in queue if t - enq == DEADLINE + 1)
            retries_next += [(t, 1)] * expired_waiting
        res.goodput.append(good)
        res.wasted.append(wasted)
        res.offered.append(offered)
    return res


def summary(name: str, r: Result) -> str:
    after = r.goodput[60:]
    return (f"{name:9s} total goodput={sum(r.goodput):6d} wasted={sum(r.wasted):6d} "
            f"min goodput after spike={min(after):3d} recovered_by_tick="
            f"{next((60 + i for i, g in enumerate(after) if g >= 78), 'never')}")


if __name__ == "__main__":
    print(summary("naive", run(False)))
    print(summary("protected", run(True)))
