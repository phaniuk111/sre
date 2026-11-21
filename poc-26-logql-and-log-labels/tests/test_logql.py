import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import logql as Q  # noqa: E402
from logql import NS  # noqa: E402

T0 = 1_700_000_000 * NS


def line(i, **kw):
    return json.dumps({"level": "info", "method": "GET", "path": f"/api/cart/{i}", "status": 200, "latency": "120ms",
                       "resources": {"k8s": {"container_restart_count": 0}}, **kw})


STREAMS = [
    ({"app": "checkout", "env": "prod", "namespace": "shop"}, [(T0 + i * NS, line(i, status=500 if i % 10 == 0 else 200, latency="900ms" if i % 10 == 0 else "120ms")) for i in range(100)]),
    ({"app": "email", "env": "prod", "namespace": "shop"}, [(T0 + i * NS, line(i, resources={"k8s": {"container_restart_count": 2}})) for i in range(20)]),
    ({"app": "web", "env": "prod", "namespace": "edge"}, [(T0 + i * NS, f'10.0.{i % 3}.7 - - [x] "GET /index.html HTTP/1.1" {404 if i % 5 == 0 else 200} 512') for i in range(50)]),
    ({"app": "legacy", "env": "prod", "namespace": "shop"}, [(T0, "\x1b[31mERROR\x1b[0m payment failed level=error"), (T0 + NS, "not json at all")]),
]


def test_selector_must_not_match_empty():
    with pytest.raises(ValueError):
        Q.select(STREAMS, [("app", "=~", ".*")])
    assert len(Q.select(STREAMS, [("app", "=~", ".+")])) == 4
    assert [l["app"] for l, _ in Q.select(STREAMS, [("namespace", "=", "shop"), ("app", "!=", "email")])] == ["checkout", "legacy"]


def test_book_pipeline_json_label_filter_line_format_and_errors():
    rows = Q.run(STREAMS, [("app", "=~", ".+")], [
        Q.line_filter("|=", "cart"), Q.json_parser,
        Q.label_filter("resources_k8s_container_restart_count", ">", 0),
        Q.line_format("{{.method}} {{.path}}"), Q.no_errors])
    assert len(rows) == 20 and {r[0]["app"] for r in rows} == {"email"}
    assert rows[0][2] == "GET /api/cart/0"


def test_typed_label_filters_duration_and_bytes():
    rows = Q.run(STREAMS, [("app", "=", "checkout")], [Q.json_parser, Q.label_filter("latency", ">", "500ms")])
    assert len(rows) == 10 and all(r[0]["status"] == "500" for r in rows)
    assert Q.parse_bytes("2.4KiB") == pytest.approx(2457.6)
    assert Q.parse_duration("2h30m") == 9000


def test_failed_parse_sets_error_and_can_be_filtered_out():
    rows = Q.run(STREAMS, [("app", "=", "legacy")], [Q.json_parser])
    assert all(r[0].get("__error__") == "JSONParserErr" for r in rows)
    assert Q.run(STREAMS, [("app", "=", "legacy")], [Q.json_parser, Q.no_errors]) == []


def test_pattern_parser_for_unstructured_access_logs_and_ip_filter():
    pat = Q.pattern_parser('<ip> - - [<_>] "<method> <uri> <_>" <status> <size>')
    rows = Q.run(STREAMS, [("app", "=", "web")], [pat, Q.label_filter("status", ">=", 400)])
    assert len(rows) == 10 and rows[0][0]["uri"] == "/index.html"
    assert len(Q.run(STREAMS, [("app", "=", "web")], [Q.ip_filter("10.0.1.0/24")])) == 17


def test_decolorize_and_logfmt():
    rows = Q.run(STREAMS, [("app", "=", "legacy")], [Q.decolorize, Q.line_filter("|=", "ERROR"), Q.logfmt_parser])
    assert rows[0][2].startswith("ERROR payment") and rows[0][0]["level"] == "error"


def test_label_format_rename_vs_template():
    rows = Q.run(STREAMS, [("app", "=", "checkout")], [Q.json_parser, Q.label_format(code="status"), Q.label_format(summary="{{.method}} {{.code}}")])
    assert "status" not in rows[0][0] and rows[0][0]["summary"] == "GET 500"


def test_metric_queries():
    rows = Q.run(STREAMS, [("namespace", "=", "shop")], [Q.json_parser, Q.no_errors, Q.label_filter("status", ">=", 500)])
    errors = Q.sum_by(Q.count_over_time(rows, T0 + 99 * NS, 100 * NS), ["app"])
    assert errors == {(("app", "checkout"),): 10}
    per_sec = Q.sum_by(Q.rate(rows, T0 + 99 * NS, 100 * NS), ["app"])
    assert per_sec[(("app", "checkout"),)] == pytest.approx(0.1)
    ok = Q.run(STREAMS, [("app", "=", "checkout")], [Q.json_parser])
    p99 = Q.unwrap_quantile(ok, T0 + 99 * NS, 100 * NS, "latency", 0.99, by=("app",), conv=Q.parse_duration)
    assert p99[(("app", "checkout"),)] == pytest.approx(0.9)
    vol = Q.sum_by(Q.count_over_time(Q.run(STREAMS, [("env", "=", "prod")], []), T0 + 99 * NS, 100 * NS), ["app"])
    assert list(Q.topk(2, vol)) == [(("app", "checkout"),), (("app", "web"),)]


def test_label_design_flags_high_cardinality():
    streams, verdict = Q.label_design({"namespace": 20, "app": 60, "cluster": 3, "user_id": 50_000, "status_code": 40})
    assert streams == 20 * 60 * 3 * 50_000 * 40
    assert verdict["user_id"].startswith("extract") and verdict["status_code"].startswith("extract")
    assert verdict["app"] == "good locator"


def test_cloudwatch_equivalents_exist_for_each_example():
    assert all("|" in v or "stats" in v for v in Q.CLOUDWATCH_INSIGHTS.values())
