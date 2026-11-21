"""Fast feedback on performance: k6 load profiles and an SLO-based gate, automated deployment
verification against telemetry, Web Vitals scoring for RUM data, and flame-graph maths for
continuous profiles. From Observability with Grafana chapters 12, 13 and 14.
"""
from __future__ import annotations

import json
import math
from collections import defaultdict

# ───────────────────────────────────────────── k6 load profiles
def profile(kind, avg_vus=50):
    """k6 `stages` for the six load test types (k6 docs, quoted in chapter 13)."""
    a = avg_vus
    return {
        "smoke": [{"duration": "1m", "target": 2}],
        "average": [{"duration": "5m", "target": a}, {"duration": "30m", "target": a}, {"duration": "5m", "target": 0}],
        "stress": [{"duration": "10m", "target": int(a * 1.5)}, {"duration": "60m", "target": int(a * 1.5)}, {"duration": "10m", "target": 0}],
        "spike": [{"duration": "1m", "target": a * 10}, {"duration": "1m", "target": 0}],
        "breakpoint": [{"duration": "2h", "target": a * 40}],
        "soak": [{"duration": "5m", "target": a}, {"duration": "48h", "target": a}, {"duration": "5m", "target": 0}],
    }[kind]


def thresholds_from_slo(error_slo=99.9, latency_ms=300, latency_pct=95):
    """Use the team's SLOs as k6 thresholds, so a load test fails for the same reasons production pages."""
    return {"http_req_failed": [f"rate<{round(1 - error_slo / 100, 6)}"], "http_req_duration": [f"p({latency_pct})<{latency_ms}"]}


def gate(summary, thresholds):
    """Evaluate a k6 `--summary-export` JSON against thresholds. Returns (passed, failures)."""
    failures = []
    for metric, rules in thresholds.items():
        m = summary["metrics"][metric]
        for rule in rules:
            stat, op_val = rule.split("<")
            limit = float(op_val)
            value = m["value"] if stat == "rate" else m[stat.strip()]
            if not value < limit:
                failures.append(f"{metric} {stat}={value} not < {limit}")
    return not failures, failures


# ───────────────────────────────────────────── deployment verification
def verify_deployment(query, checks, steps=5):
    """Chapter 14: let the CD job watch the dashboard. `query(expr, step)` returns a number (from the
    Prometheus/Loki/Tempo HTTP API in real life). Any check failing twice in a row rolls back."""
    strikes = defaultdict(int)
    for step in range(steps):
        for c in checks:
            v = query(c["expr"], step)
            bad = v > c["max"] if "max" in c else v < c["min"]
            strikes[c["name"]] = strikes[c["name"]] + 1 if bad else 0
            if strikes[c["name"]] >= 2:
                return {"decision": "rollback", "reason": f"{c['name']}={v}", "at_step": step}
    return {"decision": "promote", "reason": "all checks held", "at_step": steps - 1}


DEPLOY_CHECKS = [
    {"name": "error ratio (logs)", "expr": 'sum(rate({app="checkout"} |= "level=error" [2m])) / sum(rate({app="checkout"} [2m]))', "max": 0.01},
    {"name": "login success (smoke test)", "expr": 'sum(rate(login_success_total{app="web"}[2m]))', "min": 0.5},
    {"name": "downstream errors", "expr": 'sum(rate(rpc_client_requests_total{app="checkout",code!="OK"}[2m]))', "max": 1},
]


# ───────────────────────────────────────────── Web Vitals
VITALS = {  # good up to, needs improvement up to (web.dev); assessed at the 75th percentile of page loads
    "LCP": (2.5, 4.0), "INP": (0.2, 0.5), "CLS": (0.1, 0.25), "FCP": (1.8, 3.0), "TTFB": (0.8, 1.8), "FID": (0.1, 0.3)}


def p75(values):
    v = sorted(values)
    k = 0.75 * (len(v) - 1)
    lo, hi = math.floor(k), math.ceil(k)
    return v[lo] + (v[hi] - v[lo]) * (k - lo)


def rate_vital(name, samples):
    good, ni = VITALS[name]
    x = p75(samples)
    return x, ("good" if x <= good else "needs improvement" if x <= ni else "poor")


# ───────────────────────────────────────────── flame graphs
def parse_collapsed(text):
    """Brendan Gregg's collapsed format: 'main;bar;baz 70' per line (stack and sample count)."""
    out = []
    for line in text.strip().splitlines():
        stack, n = line.rsplit(" ", 1)
        out.append((stack.split(";"), int(n)))
    return out


def top_table(stacks):
    """Pyroscope's Top Table: self = samples where the function is the leaf, total = samples where it
    is anywhere on the stack."""
    self_, total = defaultdict(int), defaultdict(int)
    for frames, n in stacks:
        self_[frames[-1]] += n
        for f in set(frames):
            total[f] += n
    return sorted(((f, self_[f], total[f]) for f in total), key=lambda r: (-r[1], -r[2], r[0]))


def flame(stacks):
    """Width of each box = share of all samples spent in it (and its children); depth = stack depth.
    The x-axis is not time: siblings are sorted alphabetically."""
    all_n = sum(n for _, n in stacks)
    boxes = defaultdict(int)
    for frames, n in stacks:
        for d in range(len(frames)):
            boxes[tuple(frames[: d + 1])] += n
    return {";".join(k): round(v / all_n, 4) for k, v in sorted(boxes.items())}


def k6_script(base_url, kind="average", avg_vus=50, error_slo=99.9, latency_ms=300):
    opts = {"stages": profile(kind, avg_vus), "thresholds": thresholds_from_slo(error_slo, latency_ms)}
    return ("import http from 'k6/http';\nimport { check, sleep } from 'k6';\n\n"
            f"export const options = {json.dumps(opts, indent=2)};\n\n"
            "export function setup() {\n  return { product: 'OLJCESPC7Z' };\n}\n\n"
            "export default function (data) {\n"
            f"  const res = http.get(`{base_url}/api/products/${{data.product}}`);\n"
            "  check(res, { 'status is 200': (r) => r.status === 200 });\n  sleep(1);\n}\n")
