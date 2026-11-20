"""Statistically sound alerting for LOW-TRAFFIC services (ch. 8 & ch. 9).

Problem: a service doing 20 requests/minute with 1 transient failure shows a 5%
error rate. A static threshold pages someone for noise.

Fix: treat each request as a Bernoulli trial. Compute a confidence interval for
the *true* failure probability p and page only when the LOWER bound of that
interval is above the error rate you care about. With little traffic the
interval is wide, so you need proportionally more failures before paging.

The book's worked example (99% SLO, detect burn rate 14.4 => p = 14.4%, 99%
confidence, z = 2.575) gives: N=1000 -> 173 failures, N=200 -> 42, N=100 -> 24.
`min_failures_to_alert` reproduces those numbers (see tests).
"""
from __future__ import annotations

import math
from typing import Tuple

Z_99 = 2.575829  # two-tailed 99%
Z_95 = 1.959964


def wilson_interval(failures: int, n: int, z: float = Z_99) -> Tuple[float, float]:
    """Wilson score interval for a binomial proportion."""
    if n <= 0:
        return 0.0, 1.0
    p_hat = failures / n
    z2 = z * z
    denom = 1 + z2 / n
    centre = (p_hat + z2 / (2 * n)) / denom
    half = (z * math.sqrt(p_hat * (1 - p_hat) / n + z2 / (4 * n * n))) / denom
    return max(0.0, centre - half), min(1.0, centre + half)


def binomial_should_alert(failures: int, n: int, unacceptable_error_rate: float, z: float = Z_99) -> bool:
    """Page only if we're confident the true error rate exceeds the threshold."""
    lower, _ = wilson_interval(failures, n, z)
    return lower >= unacceptable_error_rate


def min_failures_to_alert(n: int, unacceptable_error_rate: float, z: float = Z_99) -> int:
    """Smallest failure count that triggers the alert for a given sample size."""
    for k in range(n + 1):
        if binomial_should_alert(k, n, unacceptable_error_rate, z):
            return k
    return n + 1  # can never be confident with this little data
