import copy
import json
import os
import sys

HERE = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, HERE)
import dashboards_as_code as D  # noqa: E402

TEAMS = {"teams": [{"name": "Checkout team", "owns": "checkout, cart", "oncall": "Grafana OnCall: checkout-primary", "channel": "#checkout", "runbook": "https://runbooks.example.com/checkout"},
                   {"name": "Payments team", "owns": "payment", "oncall": "PagerDuty: payments", "channel": "#payments", "runbook": "https://runbooks.example.com/payments"}]}


def test_generated_dashboard_passes_the_linter_and_matches_the_committed_file():
    d = D.golden_signals_dashboard("checkout", TEAMS)
    assert D.lint_dashboard(d) == []
    committed = json.load(open(os.path.join(HERE, "dashboards", "checkout-golden-signals.json")))
    assert committed == json.loads(json.dumps(d))


def test_layout_puts_golden_signals_first_and_teams_in_collapsed_rows():
    d = D.golden_signals_dashboard("checkout", TEAMS)
    top = [p["title"] for p in d["panels"] if p["gridPos"]["y"] == 0]
    assert top == ["Traffic", "Errors", "Latency p95", "Saturation"]
    rows = [p for p in d["panels"] if p["type"] == "row"]
    assert len(rows) == 2 and all(r["collapsed"] for r in rows)
    assert rows[0]["panels"][0]["type"] == "text" and "On call" in rows[0]["panels"][0]["options"]["content"]


def test_linter_catches_the_usual_mistakes():
    d = D.golden_signals_dashboard("checkout", TEAMS)
    bad = copy.deepcopy(d)
    bad["description"] = ""
    bad["time"]["from"] = "2024-01-01T00:00:00Z"
    p = bad["panels"][0]
    p["description"] = ""
    p["fieldConfig"]["defaults"]["unit"] = ""
    p["targets"][0]["expr"] = 'sum(rate(http_server_requests_total{service="checkout"}[5m]))'
    bad["panels"][5]["collapsed"] = False
    problems = D.lint_dashboard(bad)
    for needle in ("no description", "relative default", "no unit", "$__rate_interval", "hard-codes service", "collapse"):
        assert any(needle in x for x in problems), needle


def test_mixin_style_overrides():
    base = {"filename": "imported.libsonnet", "monitoringStack": ["prometheus", "grafana"]}
    assert D.merge(base, {"monitoringStack+": ["thanos"]})["monitoringStack"] == ["prometheus", "grafana", "thanos"]
    cfg = D.merge(D.DEFAULTS, {"latency_slo_seconds": 0.5})
    assert cfg["latency_slo_seconds"] == 0.5 and cfg["datasource_uid"] == "amp"
    d = D.golden_signals_dashboard("cart", {"latency_slo_seconds": 0.5})
    assert "500 ms" in d["panels"][2]["description"]


def test_terraform_parses():
    import hcl2
    tf = hcl2.load(open(os.path.join(HERE, "terraform", "amg.tf")))
    names = [list(r)[0].strip('"') for r in tf["resource"]]
    assert {"aws_grafana_workspace", "grafana_dashboard", "grafana_folder_permission", "grafana_rule_group"} <= set(names)
