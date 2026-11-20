import concurrent.futures as cf
import os
import random
import sys
import time

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from resilience import (  # noqa: E402
    AdaptiveThrottler, CircuitBreaker, CircuitOpenError, Criticality, LoadShedder,
    OverloadedError, RetryBudget, backoff_with_jitter, hedged_call, retry,
)
import simulate_cascade  # noqa: E402


class FakeClock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


def test_backoff_is_bounded_and_jittered():
    rng = random.Random(0)
    values = [backoff_with_jitter(10, base=0.1, cap=5, rng=rng) for _ in range(100)]
    assert max(values) <= 5 and len(set(values)) > 90


def test_retry_respects_budget():
    clock = FakeClock()
    budget = RetryBudget(ratio=0.1, min_retries_per_window=0, clock=clock)
    calls = []

    def always_fail():
        calls.append(1)
        raise ConnectionError()

    for _ in range(10):  # 10 first attempts -> at most 1 retry allowed
        with pytest.raises(ConnectionError):
            retry(always_fail, attempts=3, budget=budget, sleep=lambda s: None)
    assert len(calls) <= 11


def test_adaptive_throttling_formula():
    clock = FakeClock()
    th = AdaptiveThrottler(k=2, clock=clock)
    for _ in range(100):
        th.record(True)
    assert th.reject_probability() == 0
    for _ in range(300):
        th.record(False)  # backend now accepts 100 of 400
    assert th.reject_probability() == pytest.approx((400 - 200) / 401)


def test_circuit_breaker_opens_and_recovers():
    clock = FakeClock()
    cb = CircuitBreaker(failure_threshold=2, reset_timeout_s=10, clock=clock)

    def boom():
        raise TimeoutError()

    for _ in range(2):
        with pytest.raises(TimeoutError):
            cb.call(boom)
    assert cb.state == "open"
    with pytest.raises(CircuitOpenError):
        cb.call(lambda: "x")
    assert cb.call(lambda: "x", fallback=lambda: "cached") == "cached"
    clock.t = 11
    assert cb.call(lambda: "ok") == "ok" and cb.state == "closed"


def test_load_shedder_sheds_least_critical_first():
    s = LoadShedder(max_in_flight=10)
    for _ in range(8):
        s.admit(Criticality.CRITICAL)
    with pytest.raises(OverloadedError) as e:
        s.admit(Criticality.SHEDDABLE)
    assert e.value.retryable is False
    s.admit(Criticality.CRITICAL_PLUS)  # still admitted at 80%


def test_hedging_returns_fast_replica():
    def slow():
        time.sleep(0.3)
        return "slow"

    with cf.ThreadPoolExecutor(4) as pool:
        assert hedged_call([slow, lambda: "fast"], hedge_after_s=0.05, pool=pool) == "fast"


def test_protection_beats_naive_in_simulation():
    naive = simulate_cascade.run(False)
    prot = simulate_cascade.run(True)
    assert sum(prot.goodput) > sum(naive.goodput)
    assert sum(prot.wasted) < sum(naive.wasted)
