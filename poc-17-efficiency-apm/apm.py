"""Efficiency shifted down: application productivity metrics and on-by-default rollouts.

Efficiency chapter:
  * Nobody buys servers to allocate memory. Measure useful work per unit of
    resource ("application productivity metric", APM), or you cannot tell a
    regression from a busier service.
  * A work metric that does not track resource use is probably the wrong metric
    (a batch service counting batches when it should count items).
  * Ship optimisations on by default. Absorb small regressions, give a
    per-application opt-out for large ones, and treat opt-outs as information.
  * Not all work is useful: requests finished after the caller gave up are waste
    that deadline propagation removes.

AWS: work counters are custom CloudWatch metrics (EMF), resources come from
Container Insights / Lambda duration / Cost and Usage Reports, and the ratio is
CloudWatch metric math. A continuous profiler shows which shared component to fix.
"""
from __future__ import annotations

import json
import statistics
import sys


def productivity(work: float, cpu_seconds: float) -> float:
    return work / cpu_seconds


def classify(before: dict, after: dict, tolerance: float = 0.05) -> dict:
    """before/after: {"work": units, "cpu_seconds": n}. Is the change growth, a regression or an optimisation?"""
    cpu = after["cpu_seconds"] / before["cpu_seconds"] - 1
    work = after["work"] / before["work"] - 1
    prod = productivity(**after) / productivity(**before) - 1
    if prod < -tolerance:
        verdict = "regression"
    elif prod > tolerance:
        verdict = "optimisation"
    elif abs(cpu) > tolerance:
        verdict = "growth" if cpu > 0 else "shrinkage"
    else:
        verdict = "steady"
    return {"cpu_change": round(cpu, 3), "work_change": round(work, 3), "productivity_change": round(prod, 3), "verdict": verdict}


def suspicious_work_metrics(series: dict, min_correlation: float = 0.5) -> list:
    """series: {service: {"work": [...], "cpu_seconds": [...]}} sampled over the same intervals.

    Useful work and resource use should rise and fall together. Where they do not, the
    service is probably reporting the wrong thing. (Perfect correlation is not the goal:
    reporting CPU itself as "work" would achieve that and mean nothing.)
    """
    out = []
    for svc, s in sorted(series.items()):
        r = statistics.correlation(s["work"], s["cpu_seconds"])
        if r < min_correlation:
            out.append({"service": svc, "correlation": round(r, 2)})
    return out


def default_on_decision(effects: list, absorb_below: float = 0.01) -> dict:
    """Should a platform optimisation ship on by default?

    effects: [{"service", "fleet_share", "cpu_change"}] where cpu_change is the measured
    canary effect on that service (negative is a saving) and fleet_share is its share of
    fleet CPU. Small regressions are absorbed; large ones get an opt-out to be worked down.
    """
    absorbed = [e["service"] for e in effects if 0 < e["cpu_change"] <= absorb_below]
    opt_out = [e["service"] for e in effects if e["cpu_change"] > absorb_below]
    kept = [e for e in effects if e["service"] not in opt_out]
    net = sum(e["fleet_share"] * e["cpu_change"] for e in kept)
    harmed_share = sum(e["fleet_share"] for e in effects if e["cpu_change"] > absorb_below)
    ship = net < 0 and harmed_share < 0.2
    return {"ship_on_by_default": ship, "net_fleet_cpu_change": round(net, 4), "absorbed": absorbed, "opt_out": opt_out,
            "follow_up": [f"investigate {s}: an opt-out marks an edge case worth understanding" for s in opt_out]}


def wasted_work(requests: list) -> dict:
    """requests: [{"cpu_seconds", "finished_ms", "deadline_ms", "kind": "user"|"probe"|"hedge"|...}].

    CPU spent finishing work after the caller's deadline is waste. Probes and hedges are a
    cost of doing business: necessary, and worth knowing the size of.
    """
    total = sum(r["cpu_seconds"] for r in requests)
    late = sum(r["cpu_seconds"] for r in requests if r["finished_ms"] > r["deadline_ms"])
    overhead = sum(r["cpu_seconds"] for r in requests if r["kind"] != "user")
    return {"past_deadline_share": round(late / total, 3), "non_user_share": round(overhead / total, 3)}


if __name__ == "__main__":
    data = json.load(open(sys.argv[1]))
    for name, pair in data["changes"].items():
        print(name, classify(pair["before"], pair["after"]))
    print("suspicious work metrics:", suspicious_work_metrics(data["series"]))
    print("on by default:", default_on_decision(data["optimisation"]))
