"""Automated canary analysis (ch. 14 "Canaries", ch. 17 "Change Supervision").

Compare the canary (new version) against the control (current version) serving
the same traffic mix at the same time. Do NOT compare the canary against
yesterday: diurnal and mix changes fool you.

Checks:
  * error rate: one-sided two-proportion z-test (is canary worse?)
  * latency: ratio of p95s with a tolerance, and a rank-based test
    (Mann-Whitney U, normal approximation) that is robust to the long tail
  * minimum sample size, so we never pass a canary that saw no traffic
    (the 'silent canary' unsafe control action from the STPA worksheet)

Verdict: PASS / FAIL / INCONCLUSIVE (INCONCLUSIVE extends the bake time).
AWS: run from a CodeDeploy BeforeAllowTraffic/AfterAllowTraffic hook Lambda or
a Step Functions step, reading metrics split by version
(Lambda alias/version dimension, or the x-served-by-version label from POC 02).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Sequence


@dataclass
class ArmStats:
    requests: int
    errors: int
    latencies_ms: Sequence[float]


def _norm_sf(z: float) -> float:
    return 0.5 * math.erfc(z / math.sqrt(2))


def error_rate_pvalue(canary: ArmStats, control: ArmStats) -> float:
    """One-sided p-value that canary error rate > control error rate."""
    p1 = canary.errors / canary.requests
    p0 = control.errors / control.requests
    pooled = (canary.errors + control.errors) / (canary.requests + control.requests)
    se = math.sqrt(pooled * (1 - pooled) * (1 / canary.requests + 1 / control.requests))
    if se == 0:
        return 1.0 if p1 <= p0 else 0.0
    return _norm_sf((p1 - p0) / se)


def percentile(xs: Sequence[float], q: float) -> float:
    s = sorted(xs)
    idx = min(len(s) - 1, max(0, int(round(q * (len(s) - 1)))))
    return s[idx]


def mann_whitney_pvalue(canary: Sequence[float], control: Sequence[float]) -> float:
    """One-sided p-value that canary latencies are stochastically larger."""
    combined = sorted([(v, 1) for v in canary] + [(v, 0) for v in control])
    ranks: List[float] = [0.0] * len(combined)
    i = 0
    while i < len(combined):
        j = i
        while j + 1 < len(combined) and combined[j + 1][0] == combined[i][0]:
            j += 1
        avg = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[k] = avg
        i = j + 1
    r1 = sum(r for r, (_, g) in zip(ranks, combined) if g == 1)
    n1, n0 = len(canary), len(control)
    u = r1 - n1 * (n1 + 1) / 2
    mu = n1 * n0 / 2
    sigma = math.sqrt(n1 * n0 * (n1 + n0 + 1) / 12)
    return _norm_sf((u - mu) / sigma) if sigma else 1.0


def judge(canary: ArmStats, control: ArmStats, *, min_requests: int = 500, alpha: float = 0.01,
          max_p95_ratio: float = 1.2) -> str:
    if canary.requests < min_requests or control.requests < min_requests:
        return "INCONCLUSIVE"
    reasons = []
    if error_rate_pvalue(canary, control) < alpha:
        reasons.append("error rate significantly higher")
    p95_ratio = percentile(canary.latencies_ms, 0.95) / max(1e-9, percentile(control.latencies_ms, 0.95))
    if p95_ratio > max_p95_ratio and mann_whitney_pvalue(canary.latencies_ms, control.latencies_ms) < alpha:
        reasons.append(f"latency regression (p95 x{p95_ratio:.2f})")
    return "FAIL: " + "; ".join(reasons) if reasons else "PASS"
