"""Dashboards as code for Amazon Managed Grafana, with the design rules from Observability with
Grafana chapter 8 built in and a linter that enforces them; plus the Jsonnet "mixin" override idea
from Mastering Prometheus chapter 11, done with a deep merge.
"""
from __future__ import annotations

import copy
import json
import re

DEFAULTS = {
    "datasource_uid": "amp",
    "selector": 'namespace="$namespace", service="$service"',
    "latency_slo_seconds": 0.3,
    "error_threshold": 0.01,
    "teams": [],
    "time_from": "now-6h",
}


# ───────────────────────────────────────────── mixin-style overrides
def merge(base, override):
    """Jsonnet's `+:` semantics: nested objects merge; a key written as 'name+' appends to a list;
    anything else replaces. Hidden config (_config) is overridden the same way."""
    out = copy.deepcopy(base)
    for k, v in override.items():
        if k.endswith("+"):
            out[k[:-1]] = out.get(k[:-1], []) + list(v)
        elif isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = merge(out[k], v)
        else:
            out[k] = copy.deepcopy(v)
    return out


# ───────────────────────────────────────────── builders
_ids = [0]


def _panel(kind, title, desc, expr, unit, x, y, w=6, h=4, thresholds=None, legend=None):
    _ids[0] += 1
    return {"id": _ids[0], "type": kind, "title": title, "description": desc,
            "datasource": {"type": "prometheus", "uid": "${datasource}"},
            "gridPos": {"x": x, "y": y, "w": w, "h": h},
            "targets": [{"refId": "A", "expr": expr, "legendFormat": legend or "", "range": True, "instant": False}],
            "fieldConfig": {"defaults": {"unit": unit, "thresholds": {"mode": "absolute", "steps": thresholds or [{"color": "green", "value": None}]}}},
            "options": {"graphMode": "area"} if kind == "stat" else {"legend": {"displayMode": "list"}}}


def golden_signals_dashboard(service, config=None):
    """Top row: the four golden signals as Stats with sparklines, most important first, left to right.
    Then one collapsed row per owning team, starting with a text panel saying how to reach them."""
    c = merge(DEFAULTS, config or {})
    s = c["selector"]
    _ids[0] = 0
    panels = [
        _panel("stat", "Traffic", "Requests per second across all pods. Compare with the same time last week.",
               f"sum(rate(http_server_requests_total{{{s}}}[$__rate_interval]))", "reqps", 0, 0),
        _panel("stat", "Errors", "Share of requests answered with a 5xx. Turns red above the SLO's error budget rate.",
               f'sum(rate(http_server_requests_total{{{s}, code=~"5.."}}[$__rate_interval])) / sum(rate(http_server_requests_total{{{s}}}[$__rate_interval]))',
               "percentunit", 6, 0, thresholds=[{"color": "green", "value": None}, {"color": "red", "value": c["error_threshold"]}]),
        _panel("stat", "Latency p95", f"95th percentile request duration. The SLO target is {int(c['latency_slo_seconds'] * 1000)} ms.",
               f"histogram_quantile(0.95, sum by (le) (rate(http_server_request_duration_seconds_bucket{{{s}}}[$__rate_interval])))",
               "s", 12, 0, thresholds=[{"color": "green", "value": None}, {"color": "orange", "value": c["latency_slo_seconds"]}]),
        _panel("gauge", "Saturation", "CPU used as a share of the CPU limit, busiest pod. Above 80% the service throttles.",
               f'max(sum by (pod) (rate(container_cpu_usage_seconds_total{{namespace="$namespace", container="{service}"}}[$__rate_interval])) / sum by (pod) (kube_pod_container_resource_limits{{namespace="$namespace", container="{service}", resource="cpu"}}))',
               "percentunit", 18, 0, thresholds=[{"color": "green", "value": None}, {"color": "orange", "value": 0.7}, {"color": "red", "value": 0.8}]),
        _panel("timeseries", "Requests by status", "Request rate split by status code, to see whether errors replace or add to traffic.",
               f"sum by (code) (rate(http_server_requests_total{{{s}}}[$__rate_interval]))", "reqps", 0, 4, w=24, h=8, legend="{{code}}"),
    ]
    y = 12
    for team in c["teams"]:
        _ids[0] += 1
        row = {"id": _ids[0], "type": "row", "title": f"{team['name']} — {team['owns']}", "collapsed": True, "gridPos": {"x": 0, "y": y, "w": 24, "h": 1},
               "panels": [{"id": _ids[0] + 1000, "type": "text", "title": f"Contact {team['name']}",
                           "description": "How to engage this team during an incident.",
                           "gridPos": {"x": 0, "y": y + 1, "w": 6, "h": 4},
                           "options": {"mode": "markdown", "content": f"**On call:** {team['oncall']}  \n**Chat:** {team['channel']}  \n**Runbook:** {team['runbook']}"}}]}
        panels.append(row)
        y += 1
    return {
        "uid": f"{service}-golden-signals", "title": f"{service}: golden signals", "tags": ["golden-signals", service],
        "description": f"Is {service} healthy right now, and who can fix it if not. For on-call and service managers.",
        "time": {"from": c["time_from"], "to": "now"}, "refresh": "1m", "schemaVersion": 39,
        "templating": {"list": [
            {"name": "datasource", "type": "datasource", "query": "prometheus", "current": {"value": c["datasource_uid"]}},
            {"name": "namespace", "type": "query", "datasource": {"uid": "${datasource}"}, "query": "label_values(kube_namespace_labels, namespace)"},
            {"name": "service", "type": "query", "datasource": {"uid": "${datasource}"}, "query": 'label_values(http_server_requests_total{namespace="$namespace"}, service)',
             "current": {"value": service}}]},
        "annotations": {"list": [{"name": "Deployments", "enable": True, "datasource": {"uid": "${datasource}"},
                                  "expr": 'changes(kube_deployment_status_observed_generation{namespace="$namespace", deployment="$service"}[2m]) > 0',
                                  "iconColor": "purple", "titleFormat": "Deployed $service"}]},
        "links": [{"title": "Runbook", "url": f"https://runbooks.example.com/{service}", "type": "link"}],
        "panels": panels,
    }


# ───────────────────────────────────────────── linter
def _all_panels(d):
    for p in d["panels"]:
        yield p
        yield from p.get("panels", [])


def lint_dashboard(d, max_panels=24):
    """Rules from the dashboards chapter: a purpose (description), titled and described panels with
    units, variables instead of hard-coded values, $__rate_interval, collapsed detail rows, a relative
    default time range, deployment annotations, and not too many panels."""
    problems = []
    if not d.get("description"):
        problems.append("dashboard has no description: say who it is for and what question it answers")
    if not str(d.get("time", {}).get("from", "")).startswith("now-"):
        problems.append("use a relative default time range such as now-6h")
    if not d.get("annotations", {}).get("list"):
        problems.append("add deployment annotations")
    panels = [p for p in _all_panels(d) if p["type"] != "row"]
    if len(panels) > max_panels:
        problems.append(f"{len(panels)} panels: split into linked dashboards")
    var_names = {v["name"] for v in d.get("templating", {}).get("list", [])}
    for p in panels:
        if not p.get("title"):
            problems.append(f"panel {p['id']} has no title")
        if not p.get("description"):
            problems.append(f"panel '{p.get('title')}' has no description")
        if p["type"] in ("stat", "gauge", "timeseries") and not p.get("fieldConfig", {}).get("defaults", {}).get("unit"):
            problems.append(f"panel '{p['title']}' has no unit")
        for t in p.get("targets", []):
            e = t.get("expr", "")
            for m in re.finditer(r"\brate\([^\[]*\[([^\]]+)\]", e):
                if m.group(1) != "$__rate_interval":
                    problems.append(f"panel '{p['title']}' uses rate(...[{m.group(1)}]); use $__rate_interval")
            for v in ("namespace", "service"):
                if v in var_names and re.search(rf'\b{v}="(?!\$)', e):
                    problems.append(f"panel '{p['title']}' hard-codes {v}; use ${v}")
            if t.get("instant") and t.get("range") and p["type"] == "timeseries":
                problems.append(f"panel '{p['title']}' runs range and instant queries on a time series")
    rows = [p for p in d["panels"] if p["type"] == "row"]
    if rows and not all(r.get("collapsed") for r in rows):
        problems.append("collapse detail rows so their queries run only when opened")
    return problems


def write(d, path):
    with open(path, "w") as f:
        json.dump(d, f, indent=2, sort_keys=False)
