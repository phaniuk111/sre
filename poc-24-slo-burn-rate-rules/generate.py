"""Generate SLO recording rules and multiwindow, multi-burn-rate alerts, and simulate them.

Windows and factors are the Google SRE Workbook's (chapter 5), used by Sloth and quoted in
Mastering Prometheus chapter 13:
    page:   5m and 1h above 14.4x  (2% of a 30-day budget in an hour)
            30m and 6h above 6x    (5% in six hours)
    ticket: 2h and 1d above 3x     (10% in a day)
            6h and 3d above 1x     (10% in three days)

The alert compares ERROR ratios with burn × (1 − objective). Comparing a success ratio, as one
printed example in the book does, would fire all the time.
"""
from __future__ import annotations

import sys

import yaml

WINDOWS = ["5m", "30m", "1h", "2h", "6h", "1d", "3d"]
PAGE = [("5m", "1h", 14.4), ("30m", "6h", 6.0)]
TICKET = [("2h", "1d", 3.0), ("6h", "3d", 1.0)]
MINUTES = {"5m": 5, "30m": 30, "1h": 60, "2h": 120, "6h": 360, "1d": 1440, "3d": 4320, "30d": 43200}


def budget(objective):
    return round(1 - objective / 100, 10)


def _sel(service, slo):
    return f'sloth_service="{service}",sloth_slo="{slo}"'


def rules_for(service, s):
    name, obj = s["name"], s["objective"]
    err, tot = s["sli"]["events"]["error_query"].strip(), s["sli"]["events"]["total_query"].strip()
    labels = {"sloth_service": service, "sloth_slo": name}
    rec = []
    for w in WINDOWS:
        rec.append({"record": "slo:sli_error:ratio_rate" + w,
                    "expr": f"({err.replace('{{.window}}', w)})\n/\n(clamp_min({tot.replace('{{.window}}', w)}, 1e-9))",
                    "labels": {**labels, "sloth_window": w}})
    rec.append({"record": "slo:sli_error:ratio_rate30d",
                "expr": f"sum_over_time(slo:sli_error:ratio_rate5m{{{_sel(service, name)}}}[30d])\n/ ignoring (sloth_window)\n"
                        f"count_over_time(slo:sli_error:ratio_rate5m{{{_sel(service, name)}}}[30d])",
                "labels": {**labels, "sloth_window": "30d"}})
    rec.append({"record": "slo:objective:ratio", "expr": f"vector({obj / 100})", "labels": labels})
    rec.append({"record": "slo:error_budget:ratio", "expr": f"vector(1 - {obj / 100})", "labels": labels})
    rec.append({"record": "slo:period_error_budget_remaining:ratio",
                "expr": f"1 - slo:sli_error:ratio_rate30d{{{_sel(service, name)}}} / ignoring (sloth_window) slo:error_budget:ratio{{{_sel(service, name)}}}",
                "labels": labels})

    def cond(pairs):
        parts = []
        for short, long, f in pairs:
            parts.append(f"(\n  max(slo:sli_error:ratio_rate{short}{{{_sel(service, name)}}} > ({f} * {budget(obj)})) without (sloth_window)\n  and\n"
                         f"  max(slo:sli_error:ratio_rate{long}{{{_sel(service, name)}}} > ({f} * {budget(obj)})) without (sloth_window)\n)")
        return "\nor\n".join(parts)

    a = s["alerting"]
    alerts = [
        {"alert": a["name"], "expr": cond(PAGE), "labels": {**a["page_labels"], "sloth_severity": "page"},
         "annotations": {"summary": f"{service} is burning its {name} error budget fast.",
                         "description": f"{s['description']} Burn rate is above 6x on both a short and a long window; at this rate the 30-day budget is gone in under five days. Current 1h error ratio {{{{ $value | humanizePercentage }}}}.",
                         "runbook_url": f"https://runbooks.example.com/slo/{service}/{name}"}},
        {"alert": a["name"], "expr": cond(TICKET), "labels": {**a["ticket_labels"], "sloth_severity": "ticket"},
         "annotations": {"summary": f"{service} is slowly burning its {name} error budget.",
                         "description": f"{s['description']} The error budget will run out before the end of the 30-day window at the current rate ({{{{ $value | humanizePercentage }}}}).",
                         "runbook_url": f"https://runbooks.example.com/slo/{service}/{name}"}},
    ]
    return [{"name": f"slo-sli-recordings-{service}-{name}", "rules": rec},
            {"name": f"slo-alerts-{service}-{name}", "rules": alerts}]


def window_based_rule(service, name, sli_success_expr, window_threshold, window="5m", period="30d"):
    """A window-based SLO: each window is good (1) or bad (0) via `>= bool`, averaged by a subquery."""
    return {"record": "slo:sli_good_windows:ratio" + period,
            "expr": f"avg_over_time((({sli_success_expr}) >= bool {window_threshold})[{period}:{window}])",
            "labels": {"sloth_service": service, "sloth_slo": name}}


def generate(spec):
    groups = []
    for s in spec["slos"]:
        groups += rules_for(spec["service"], s)
    return {"groups": groups}


# ───────────────────────────────────────────── simulation
def error_ratio(errors, totals, end, minutes):
    """Error ratio over the trailing `minutes` ending at minute index `end` (inclusive)."""
    lo = max(0, end - minutes + 1)
    e, t = sum(errors[lo:end + 1]), sum(totals[lo:end + 1])
    return e / t if t else 0.0


def simulate(errors, totals, objective, pairs):
    """Minute by minute: does any (short, long, factor) pair fire?"""
    b = budget(objective)
    out = []
    for i in range(len(totals)):
        out.append(any(error_ratio(errors, totals, i, MINUTES[s]) > f * b and error_ratio(errors, totals, i, MINUTES[l]) > f * b for s, l, f in pairs))
    return out


def budget_consumed(errors, totals, objective, period_minutes=43200, steady_rps_minute=None):
    """Fraction of a 30-day budget consumed so far, assuming the observed traffic rate continues."""
    per_minute = steady_rps_minute or (sum(totals) / len(totals))
    allowed = per_minute * period_minutes * budget(objective)
    return sum(errors) / allowed


def downtime_minutes(objective, days=30):
    return days * 24 * 60 * budget(objective)


def recovery(good_rpm, bad_rps, window_minutes=15, good_windows_before=4, target=0.95):
    """Mastering Prometheus ch13: a spike of bad_rps for one window among quiet good windows.
    Returns (days of normal traffic for request-based availability to climb back to 50%,
             hours of good windows for window-based availability to reach the target)."""
    bad = bad_rps * 60 * window_minutes
    days_requests = bad / good_rpm / 60 / 24  # need as many good requests as bad ones for 50%
    total, good, extra = good_windows_before + 1, good_windows_before, 0
    while (good + extra) / (total + extra) < target:
        extra += 1
    return days_requests, extra * window_minutes / 60


if __name__ == "__main__":
    spec = yaml.safe_load(open(sys.argv[1] if len(sys.argv) > 1 else "slo.yml"))
    yaml.safe_dump(generate(spec), sys.stdout, sort_keys=False, width=200)
