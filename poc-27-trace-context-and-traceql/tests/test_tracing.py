import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import tracing as T  # noqa: E402
from tracing import Span  # noqa: E402

TID = "4bf92f3577b34da6a3ce929d0e0e4736"


def test_traceparent_roundtrip_and_validation():
    h = T.traceparent(TID, "00f067aa0ba902b7", True)
    assert h == "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"
    assert T.parse_traceparent(h) == {"trace_id": TID, "parent_id": "00f067aa0ba902b7", "sampled": True}
    assert T.parse_traceparent("00-" + "0" * 32 + "-00f067aa0ba902b7-01") is None   # all-zero trace id
    assert T.parse_traceparent("01-" + TID + "-00f067aa0ba902b7-01") is None        # unknown version
    assert T.parse_traceparent("00-" + TID.upper() + "-00f067aa0ba902b7-01") is None  # must be lowercase


def test_other_header_formats():
    ctx = T.parse_traceparent(T.traceparent(TID, "00f067aa0ba902b7", False))
    assert T.to_b3_single(ctx) == f"{TID}-00f067aa0ba902b7-0"
    assert T.to_b3_multi(ctx)["X-B3-Sampled"] == "0"
    assert T.to_uber(ctx).count(":") == 3


def test_xray_header_roundtrip():
    xray_style = "5759e988bd862e3fe1be46a994272793"
    ctx = {"trace_id": xray_style, "parent_id": "53995c3f42cd8ad8", "sampled": True}
    h = T.to_xray(ctx)
    assert h == "Root=1-5759e988-bd862e3fe1be46a994272793;Parent=53995c3f42cd8ad8;Sampled=1"
    assert T.from_xray(h) == ctx
    assert T.xray_id_valid(xray_style, now_epoch=0x5759e988 + 3600)
    assert not T.xray_id_valid(TID, now_epoch=0x5759e988)  # a random W3C id isn't a valid X-Ray time prefix


def test_baggage_limits_and_encoding():
    h = T.encode_baggage({"tenantId": "acme corp", "plan": "gold"})
    assert h == "tenantId=acme%20corp,plan=gold"
    assert T.decode_baggage(h + ";prop=1") == {"tenantId": "acme corp", "plan": "gold"}
    with pytest.raises(ValueError):
        T.encode_baggage({f"k{i}": "v" for i in range(65)})
    with pytest.raises(ValueError):
        T.encode_baggage({"big": "x" * 9000})


def test_parent_based_sampling_keeps_traces_whole():
    services = ["frontend", "checkout", "payment", "email"]
    assert T.propagate(services, 2000, 0.1, parent_based=True) == 1.0
    assert T.propagate(services, 2000, 0.1, parent_based=False) < 0.8  # many partial traces


def trace():
    return [
        Span(TID, "a", None, "frontend", "GET /cart", 0, 420, kind="server", attrs={"http.method": "GET"}),
        Span(TID, "b", "a", "frontend", "call checkout", 10, 400, kind="client"),
        Span(TID, "c", "b", "checkout", "PlaceOrder", 20, 390, kind="server"),
        Span(TID, "d", "c", "checkout", "call cart", 30, 120, kind="client"),
        Span(TID, "e", "d", "cartservice", "GetCart", 40, 110, kind="server"),
        Span(TID, "f", "c", "checkout", "call payment", 130, 380, kind="client"),
        Span(TID, "g", "f", "payment", "Charge", 140, 370, kind="server", status="error"),
    ]


def test_traceql_selection_and_structure():
    t = trace()
    assert [s.span_id for s in T.spanset(t, [("resource.service.name", "=", "checkout"), ("kind", "=", "server")])] == ["c"]
    assert [s.span_id for s in T.structural(t, [(".service.name", "=", "checkout")], ">", [(".service.name", "=", "cartservice")])] == ["e"]
    assert [s.span_id for s in T.structural(t, [(".service.name", "=", "frontend"), ("kind", "=", "server")], ">>", [(".service.name", "=", "payment")])] == ["g"]
    assert [s.span_id for s in T.structural(t, [("name", "=", "call cart")], "~", [("name", "=", "call payment")])] == ["f"]
    assert T.count_gt(t, [(".service.name", "=", "checkout")], 2)
    assert T.avg_duration_gt(t, [("status", "=", "error")], 200)


def test_tail_sampling_keeps_every_error_trace():
    assert T.tail_keep(trace())
    fast_ok = [Span("ffffffffffffffffffffffffffffffff", "x", None, "web", "GET", 0, 10)]
    assert not T.tail_keep(fast_ok)


def test_span_metrics_and_service_graph():
    calls, hist = T.span_metrics(trace())
    assert calls[("payment", "Charge", "server", "error")] == 1
    assert sum(hist[("frontend", "GET /cart", "server", "ok")]) == 1
    g = T.service_graph(trace())
    # client spans sit in the caller's service, so the server span's parent is the caller's client span
    assert g == {("frontend", "checkout"): {"requests": 1, "failed": 0},
                 ("checkout", "cartservice"): {"requests": 1, "failed": 0},
                 ("checkout", "payment"): {"requests": 1, "failed": 1}}
