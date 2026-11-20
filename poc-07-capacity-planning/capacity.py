"""Capacity planning maths (book ch. 15).

demand forecast = organic trend + inorganic events, with an uncertainty band
                  from backtesting the model's past errors
supply plan     = convert demand (QPS) to resources via a measured
                  'resources per unit of demand' ratio, then add redundancy
                  (N+1 failure domains) and headroom
pooling         = peak of sums <= sum of peaks: the reason shared pools
                  (Google's Flex, AWS's on-demand fleet) are cheaper
"""
from __future__ import annotations

import math
import statistics
from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple


def linear_fit(ys: Sequence[float]) -> Tuple[float, float]:
    """Least squares y = a + b*t for t = 0..n-1."""
    n = len(ys)
    ts = range(n)
    t_mean = (n - 1) / 2
    y_mean = statistics.fmean(ys)
    b = sum((t - t_mean) * (y - y_mean) for t, y in zip(ts, ys)) / sum((t - t_mean) ** 2 for t in ts)
    return y_mean - b * t_mean, b


def forecast_organic(history: Sequence[float], horizon: int) -> List[float]:
    a, b = linear_fit(history)
    n = len(history)
    return [a + b * (n + h) for h in range(horizon)]


def backtest_errors(history: Sequence[float], train: int, horizon: int) -> List[float]:
    """Rolling-origin backtest: relative error of each h-step-ahead forecast."""
    errs = []
    for origin in range(train, len(history) - horizon + 1):
        fc = forecast_organic(history[:origin], horizon)
        actual = history[origin + horizon - 1]
        errs.append((actual - fc[-1]) / fc[-1])
    return errs


def forecast_with_uncertainty(history: Sequence[float], horizon: int, inorganic: Dict[int, float] | None = None,
                              confidence: float = 0.9, train: int = 12) -> List[Tuple[float, float]]:
    """Return (median, upper-bound) per future period.

    inorganic: {period_index: extra_demand} for known launches / marketing
    campaigns / Black Friday. Unplanned inorganic demand (COVID for Google Meet,
    up to 400x) is what the upper band and the pooled-capacity escape hatch are for.
    """
    inorganic = inorganic or {}
    base = forecast_organic(history, horizon)
    errs = sorted(backtest_errors(history, train, min(horizon, max(1, len(history) - train))))
    q = errs[min(len(errs) - 1, int(confidence * len(errs)))] if errs else 0.2
    out = []
    for i, b in enumerate(base):
        median = b + inorganic.get(i, 0.0)
        out.append((median, median * (1 + max(q, 0.0))))
    return out


@dataclass
class SupplyPlan:
    per_domain: int
    domains: int
    total: int
    utilisation_at_peak: float


def plan_supply(peak_demand_qps: float, qps_per_instance: float, failure_domains: int = 3,
                target_utilisation: float = 0.7) -> SupplyPlan:
    """N+1 across failure domains: survive the loss of one AZ with no scaling action
    (AWS 'static stability'), while keeping utilisation below the target."""
    if failure_domains < 2:
        raise ValueError("need at least two failure domains for N+1")
    needed = math.ceil(peak_demand_qps / (qps_per_instance * target_utilisation))
    per_domain = math.ceil(needed / (failure_domains - 1))  # N = domains-1 must carry the peak
    total = per_domain * failure_domains
    return SupplyPlan(per_domain, failure_domains, total, peak_demand_qps / (total * qps_per_instance))


def redundancy_overhead(failure_domains: int) -> float:
    """Fraction of capacity that is N+1 insurance: 1/N. More, smaller domains = cheaper insurance (ch. 20)."""
    return 1 / (failure_domains - 1)


def sum_of_peaks(series: Dict[str, Sequence[float]]) -> float:
    return sum(max(s) for s in series.values())


def peak_of_sums(series: Dict[str, Sequence[float]]) -> float:
    return max(sum(vals) for vals in zip(*series.values()))


def stranded_capacity(capacity: float, usage: Sequence[float]) -> float:
    """Average idle capacity across a diurnal cycle: what latency-tolerant batch
    work could reclaim (but never reclaim ALL of it: low-priority work would then
    fail outright at peak)."""
    return statistics.fmean(capacity - u for u in usage)
