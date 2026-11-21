"""Distributed tracing mechanics: context propagation headers (W3C, B3, Jaeger, AWS X-Ray), baggage,
head and tail sampling, a small TraceQL evaluator, and the span-metrics and service-graph
connectors that turn traces into RED metrics.
"""
from __future__ import annotations

import hashlib
import re
import urllib.parse
from collections import defaultdict
from dataclasses import dataclass, field

HEX = re.compile(r"^[0-9a-f]+$")


# ───────────────────────────────────────────── W3C Trace Context
def parse_traceparent(h):
    """traceparent: {version}-{trace-id 32 hex}-{parent-id 16 hex}-{flags 2 hex}. Returns None if invalid."""
    parts = h.strip().split("-")
    if len(parts) != 4:
        return None
    ver, tid, pid, flags = parts
    if ver != "00" or len(tid) != 32 or len(pid) != 16 or len(flags) != 2:
        return None
    if not all(HEX.match(x) for x in (tid, pid, flags)) or set(tid) == {"0"} or set(pid) == {"0"}:
        return None
    return {"trace_id": tid, "parent_id": pid, "sampled": int(flags, 16) & 1 == 1}


def traceparent(trace_id, span_id, sampled):
    return f"00-{trace_id}-{span_id}-{'01' if sampled else '00'}"


def new_id(seed, nbytes):
    return hashlib.sha256(seed.encode()).hexdigest()[: nbytes * 2]


# ───────────────────────────────────────────── other formats
def to_b3_single(ctx):
    return f"{ctx['trace_id']}-{ctx['parent_id']}-{1 if ctx['sampled'] else 0}"


def to_b3_multi(ctx):
    return {"X-B3-TraceId": ctx["trace_id"], "X-B3-SpanId": ctx["parent_id"], "X-B3-Sampled": "1" if ctx["sampled"] else "0"}


def to_uber(ctx, parent_span="0"):
    return f"{ctx['trace_id']}:{ctx['parent_id']}:{parent_span}:{'1' if ctx['sampled'] else '0'}"


def to_xray(ctx):
    """X-Ray: Root=1-{8 hex epoch seconds}-{24 hex};Parent={16 hex};Sampled=0|1. A W3C trace ID maps
    directly when its first 8 hex digits are a recent epoch time, which is why ADOT uses an X-Ray
    compatible ID generator when traces go to X-Ray."""
    t = ctx["trace_id"]
    return f"Root=1-{t[:8]}-{t[8:]};Parent={ctx['parent_id']};Sampled={1 if ctx['sampled'] else 0}"


def from_xray(h):
    f = dict(p.split("=", 1) for p in h.split(";"))
    _, epoch, rest = f["Root"].split("-")
    return {"trace_id": epoch + rest, "parent_id": f["Parent"], "sampled": f.get("Sampled") == "1"}


def xray_id_valid(trace_id, now_epoch, max_age_days=30):
    return 0 <= now_epoch - int(trace_id[:8], 16) <= max_age_days * 86400


# ───────────────────────────────────────────── baggage
MAX_MEMBERS, MAX_BYTES = 64, 8192


def encode_baggage(items):
    """W3C baggage: comma-separated key=value, values percent-encoded; at most 64 members and 8192 bytes.
    Visible to anyone on the wire: never put secrets or personal data in it."""
    if len(items) > MAX_MEMBERS:
        raise ValueError("baggage may hold at most 64 members")
    h = ",".join(f"{k}={urllib.parse.quote(str(v), safe='')}" for k, v in items.items())
    if len(h.encode()) > MAX_BYTES:
        raise ValueError("baggage header larger than 8192 bytes")
    return h


def decode_baggage(h):
    out = {}
    for member in filter(None, (m.strip() for m in h.split(","))):
        kv = member.split(";")[0]
        k, _, v = kv.partition("=")
        out[k.strip()] = urllib.parse.unquote(v.strip())
    return out


# ───────────────────────────────────────────── sampling
def ratio_decision(trace_id, ratio):
    """TraceIdRatioBased: deterministic from the trace ID, so every service agrees."""
    return int(trace_id[-14:], 16) / float(16 ** 14) < ratio


def propagate(services, n_requests, ratio, parent_based=True):
    """Fraction of traces that arrive complete when each service samples on its own versus when
    children follow the parent's sampled flag."""
    complete = 0
    for i in range(n_requests):
        tid = new_id(f"req{i}", 16)
        if parent_based:
            kept = [ratio_decision(tid, ratio)] * len(services)
        else:
            kept = [ratio_decision(new_id(f"{tid}{s}", 16), ratio) for s in services]
        complete += all(kept) or not any(kept)
    return complete / n_requests


def tail_keep(trace, slow_ms=500, base_ratio=0.01, slow_ratio=0.5):
    """Tail sampling after the trace is complete: all errors, half the slow ones, 1% of the rest."""
    if any(s.status == "error" for s in trace):
        return True
    root = min(trace, key=lambda s: s.start)
    tid = root.trace_id
    if max(s.end for s in trace) - root.start > slow_ms:
        return ratio_decision(tid, slow_ratio)
    return ratio_decision(tid, base_ratio)


# ───────────────────────────────────────────── spans and TraceQL
@dataclass
class Span:
    trace_id: str
    span_id: str
    parent_id: str | None
    service: str
    name: str
    start: float
    end: float
    status: str = "ok"
    kind: str = "server"
    attrs: dict = field(default_factory=dict)

    @property
    def duration(self):
        return self.end - self.start


def _field(span, key):
    if key in ("status", "name", "kind", "duration"):
        return getattr(span, key)
    if key in ("resource.service.name", ".service.name"):
        return span.service
    return span.attrs.get(key.split(".", 1)[1] if key.startswith(("span.", "resource.")) else key.lstrip("."))


def spanset(trace, cond):
    """cond: list of (field, op, value) ANDed, like {span.http.method="GET" && duration > 100}."""
    ops = {"=": lambda a, b: a == b, "!=": lambda a, b: a != b, ">": lambda a, b: a is not None and a > b,
           "<": lambda a, b: a is not None and a < b, "=~": lambda a, b: a is not None and re.fullmatch(b, str(a)) is not None}
    return [s for s in trace if all(ops[op](_field(s, f), v) for f, op, v in cond)]


def _ancestors(trace, span):
    by = {s.span_id: s for s in trace}
    p = by.get(span.parent_id)
    while p:
        yield p
        p = by.get(p.parent_id)


def structural(trace, left, op, right):
    """TraceQL {left} > {right} (child), >> (descendant), ~ (sibling): returns matching right-hand spans."""
    L, R = spanset(trace, left), spanset(trace, right)
    lid = {s.span_id for s in L}
    if op == ">":
        return [s for s in R if s.parent_id in lid]
    if op == ">>":
        return [s for s in R if any(a.span_id in lid for a in _ancestors(trace, s))]
    if op == "~":
        parents = {s.parent_id for s in L}
        return [s for s in R if s.parent_id in parents and s.span_id not in lid]
    raise ValueError(op)


def count_gt(trace, cond, n):
    """{cond} | count() > n"""
    return len(spanset(trace, cond)) > n


def avg_duration_gt(trace, cond, ms):
    ss = spanset(trace, cond)
    return bool(ss) and sum(s.duration for s in ss) / len(ss) > ms


# ───────────────────────────────────────────── connectors
BUCKETS = [2, 4, 6, 8, 10, 50, 100, 200, 400, 800, 1000, 1400, 2000, 5000, 10000, 15000]


def span_metrics(spans):
    """spanmetrics connector: calls_total and a duration histogram per service, span name, kind, status."""
    calls, hist = defaultdict(int), defaultdict(lambda: [0] * (len(BUCKETS) + 1))
    for s in spans:
        key = (s.service, s.name, s.kind, s.status)
        calls[key] += 1
        i = next((k for k, b in enumerate(BUCKETS) if s.duration <= b), len(BUCKETS))
        hist[key][i] += 1
    return dict(calls), dict(hist)


def service_graph(spans):
    """servicegraph connector: an edge for every client span whose child server span is in another service."""
    by = {s.span_id: s for s in spans}
    edges = defaultdict(lambda: {"requests": 0, "failed": 0})
    for s in spans:
        if s.kind == "server" and s.parent_id in by:
            parent = by[s.parent_id]
            if parent.service != s.service:
                e = edges[(parent.service, s.service)]
                e["requests"] += 1
                e["failed"] += s.status == "error"
    return dict(edges)
