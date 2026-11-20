"""Composing SLOs from dependencies (ch. 9 + appendix E).

Serial, fail-closed dependencies multiply availabilities:
    A -> B (80%) -> C (90%)  => best case 72%
Parallel hedged calls (first success wins) multiply FAILURE probabilities:
    1 - (0.2 * 0.1) = 98%

Caveat the book stresses: both formulas assume *independent* failures. Shared
downstream deps (same database, lock service, AZ, network fabric) break this,
so real availability is lower than the parallel formula suggests.

AWS translation: a Lambda behind API Gateway that calls DynamoDB and then SQS is
a serial chain: compose the published service SLAs/SLOs to get your *ceiling*.
"""
from __future__ import annotations

from functools import reduce
from itertools import combinations
from math import prod
from typing import Iterable, Sequence


def serial_availability(availabilities: Iterable[float]) -> float:
    return reduce(lambda a, b: a * b, availabilities, 1.0)


def parallel_availability(availabilities: Iterable[float]) -> float:
    fail = reduce(lambda a, b: a * (1 - b), availabilities, 1.0)
    return 1.0 - fail


def k_of_n_availability(availabilities: Sequence[float], k: int) -> float:
    """Probability that at least k of n independent replicas are up.

    Useful for quorum systems (e.g. 2-of-3 AZs for a consensus store).
    """
    n = len(availabilities)
    total = 0.0
    for up_count in range(k, n + 1):
        for up_set in combinations(range(n), up_count):
            up = set(up_set)
            total += prod(availabilities[i] if i in up else 1 - availabilities[i] for i in range(n))
    return total
