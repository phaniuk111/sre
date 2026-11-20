"""Relative latency regression detection by cohort (ch. 9 + appendix F).

Absolute latency thresholds don't work when workloads differ wildly (a 6s
analytics query is normal; a 6s login is a disaster). Instead:

1. Group similar workloads into COHORTS (RPC method, customer, query shape).
2. A cohort is "meaningful" if it has enough samples (B) and low relative
   variance (coefficient of variation below a bound).
3. Baseline each meaningful cohort over 30-60 days: mean and std dev.
4. For new requests compute z = (x - mu) / sigma against their cohort.
5. Detection metric = fraction of requests with z > z_thr.
   A perfect normal gives 2.28% above z=2; the book observes ~4% in practice.
   A significant jump above the baseline fraction => service-wide regression.

Because z-scores are unitless, one detector works across every service.
Latency is roughly log-normal, so we work on log(latency).

AWS: feed this from CloudWatch Logs Insights / Athena over the structured logs
emitted by app.py, run on a schedule (EventBridge -> Lambda), and publish the
detection metric as a custom CloudWatch metric with an alarm.
"""
from __future__ import annotations

import math
import statistics
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Hashable, Iterable, List, Tuple

Sample = Tuple[Hashable, float]  # (cohort key, latency_ms)


@dataclass(frozen=True)
class CohortBaseline:
    mu: float
    sigma: float
    n: int


def build_baselines(history: Iterable[Sample], min_samples: int = 1000, max_cv: float = 1.0) -> Dict[Hashable, CohortBaseline]:
    buckets: Dict[Hashable, List[float]] = defaultdict(list)
    for key, latency in history:
        if latency > 0:
            buckets[key].append(math.log(latency))
    baselines = {}
    for key, values in buckets.items():
        if len(values) < min_samples:
            continue  # not meaningful: too little data
        mu = statistics.fmean(values)
        sigma = statistics.pstdev(values)
        if sigma == 0 or (mu != 0 and sigma / abs(mu) > max_cv):
            continue  # not meaningful: too noisy to compare against
        baselines[key] = CohortBaseline(mu, sigma, len(values))
    return baselines


def coverage(history: Iterable[Sample], baselines: Dict[Hashable, CohortBaseline]) -> float:
    """Fraction of workloads that fall in meaningful cohorts (book aims for >= 65%)."""
    total = covered = 0
    for key, _ in history:
        total += 1
        covered += key in baselines
    return covered / total if total else 0.0


def outlier_fraction(test: Iterable[Sample], baselines: Dict[Hashable, CohortBaseline], z_thr: float = 2.0) -> float:
    n = above = 0
    for key, latency in test:
        b = baselines.get(key)
        if b is None or latency <= 0:
            continue
        n += 1
        above += (math.log(latency) - b.mu) / b.sigma > z_thr
    return above / n if n else 0.0


def is_regression(fraction: float, baseline_fraction: float = 0.04, factor: float = 2.0) -> bool:
    """Flag when the outlier fraction is well above the normal ~4%."""
    return fraction > baseline_fraction * factor
