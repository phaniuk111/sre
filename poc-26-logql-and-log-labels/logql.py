"""A working model of LogQL's pipeline and metric queries, plus a Loki label-design checker.

A stream is a unique label set with entries (ns timestamp, line). The pipeline is a list of stages,
applied per line in order, exactly as LogQL does: filters drop lines, parsers add labels, label
filters compare typed values, formatters rewrite the line or labels. Metric queries turn the
surviving lines into numbers.
"""
from __future__ import annotations

import ipaddress
import json
import math
import re
from collections import defaultdict
from itertools import product

NS = 1_000_000_000


# ───────────────────────────────────────────── stream selection
def select(streams, matchers):
    """{app="checkout", env=~"prod|stage"}: at least one matcher must NOT match an empty value,
    so {app=~".*"} is rejected and {app=~".+"} is accepted."""
    def hit(op, val, have):
        return {"=": have == val, "!=": have != val, "=~": re.fullmatch(val, have) is not None, "!~": re.fullmatch(val, have) is None}[op]
    if not any(not hit(op, v, "") for _, op, v in matchers):
        raise ValueError("queries require at least one matcher that doesn't match empty values")
    out = []
    for labels, entries in streams:
        if all(hit(op, val, labels.get(name, "")) for name, op, val in matchers):
            out.append((labels, entries))
    return out


# ───────────────────────────────────────────── stages
def line_filter(op, needle):
    if op == "|=":
        return lambda ts, line, lb: (line, lb) if needle in line else None
    if op == "!=":
        return lambda ts, line, lb: (line, lb) if needle not in line else None
    rx = re.compile(needle)
    if op == "|~":
        return lambda ts, line, lb: (line, lb) if rx.search(line) else None
    return lambda ts, line, lb: (line, lb) if not rx.search(line) else None


def ip_filter(cidr):
    net = ipaddress.ip_network(cidr, strict=False)
    cand = re.compile(r"[0-9a-fA-F:.]{3,}")

    def f(ts, line, lb):
        for m in cand.findall(line):
            try:
                if ipaddress.ip_address(m) in net:
                    return line, lb
            except ValueError:
                pass
        return None
    return f


ANSI = re.compile(r"\x1b\[[0-9;]*m")


def decolorize(ts, line, lb):
    return ANSI.sub("", line), lb


def _flatten(prefix, obj, out):
    for k, v in obj.items():
        key = re.sub(r"[^a-zA-Z0-9_]", "_", f"{prefix}{k}")
        if isinstance(v, dict):
            _flatten(key + "_", v, out)
        elif isinstance(v, list):
            continue  # | json skips arrays when extracting everything
        else:
            out[key] = "" if v is None else str(v).lower() if isinstance(v, bool) else str(v)


def json_parser(ts, line, lb):
    try:
        obj = json.loads(line)
    except ValueError:
        return line, {**lb, "__error__": "JSONParserErr"}
    out = {}
    _flatten("", obj, out)
    return line, {**lb, **{k: v for k, v in out.items() if k not in lb}, **{k + "_extracted": v for k, v in out.items() if k in lb}}


LOGFMT = re.compile(r'(\w+)=("(?:[^"\\]|\\.)*"|\S+)')


def logfmt_parser(ts, line, lb):
    pairs = {k: v.strip('"') for k, v in LOGFMT.findall(line)}
    return line, {**lb, **pairs}


def pattern_parser(pattern):
    """'<ip> - <_> [<ts>] "<method> <path> <_>" <status> <size>': captures between < >, <_> ignored."""
    parts = re.split(r"(<[a-zA-Z_][a-zA-Z0-9_]*>)", pattern)
    rx = ""
    names = []
    for p in parts:
        if re.fullmatch(r"<[a-zA-Z_][a-zA-Z0-9_]*>", p):
            name = p[1:-1]
            rx += "(.*?)" if name == "_" else f"(?P<{name}>.*?)"
            if name != "_":
                names.append(name)
        else:
            rx += re.escape(p)
    compiled = re.compile("^" + rx + "$")

    def f(ts, line, lb):
        m = compiled.match(line)
        return (line, {**lb, **m.groupdict()}) if m else (line, lb)
    return f


def regexp_parser(expr):
    rx = re.compile(expr)

    def f(ts, line, lb):
        m = rx.search(line)
        return (line, {**lb, **{k: v for k, v in m.groupdict().items() if v is not None}}) if m else (line, lb)
    return f


UNITS = {"ns": 1e-9, "us": 1e-6, "µs": 1e-6, "ms": 1e-3, "s": 1, "m": 60, "h": 3600}
BYTES = {"b": 1, "kb": 1e3, "kib": 1024, "mb": 1e6, "mib": 1024 ** 2, "gb": 1e9, "gib": 1024 ** 3}


def parse_duration(s):
    total, pos = 0.0, 0
    for m in re.finditer(r"(\d+(?:\.\d+)?)(ns|us|µs|ms|s|m|h)", s):
        if m.start() != pos:
            raise ValueError(s)
        total += float(m.group(1)) * UNITS[m.group(2)]
        pos = m.end()
    if pos != len(s) or pos == 0:
        raise ValueError(s)
    return total


def parse_bytes(s):
    m = re.fullmatch(r"(\d+(?:\.\d+)?)\s*([a-zA-Z]+)", s.strip())
    if not m or m.group(2).lower() not in BYTES:
        raise ValueError(s)
    return float(m.group(1)) * BYTES[m.group(2).lower()]


def label_filter(name, op, value):
    """Typed comparison. The value's type decides how the label is converted: '250ms' is a duration,
    '2MB' bytes, 3 a number, anything else a string. A failed conversion sets __error__."""
    if isinstance(value, (int, float)):
        conv, target = float, float(value)
    elif re.fullmatch(r"(\d+(?:\.\d+)?(ns|us|µs|ms|s|m|h))+", str(value)):
        conv, target = parse_duration, parse_duration(value)
    elif re.fullmatch(r"\d+(?:\.\d+)?\s*(b|kb|kib|mb|mib|gb|gib)", str(value), re.I):
        conv, target = parse_bytes, parse_bytes(value)
    else:
        conv, target = str, value
    cmp = {"=": lambda a, b: a == b, "==": lambda a, b: a == b, "!=": lambda a, b: a != b, ">": lambda a, b: a > b,
           ">=": lambda a, b: a >= b, "<": lambda a, b: a < b, "<=": lambda a, b: a <= b,
           "=~": lambda a, b: re.fullmatch(b, a) is not None, "!~": lambda a, b: re.fullmatch(b, a) is None}[op]

    def f(ts, line, lb):
        if name not in lb:
            return None if op not in ("!=", "!~") else (line, lb)
        try:
            have = conv(lb[name])
        except ValueError:
            return line, {**lb, "__error__": "LabelFilterErr"}
        return (line, lb) if cmp(have, target) else None
    return f


def no_errors(ts, line, lb):
    """| __error__="" : drop lines where a parser or conversion failed."""
    return None if lb.get("__error__") else (line, lb)


def _render(template, ts, line, lb):
    def rep(m):
        expr = m.group(1).strip()
        if expr == "__line__":
            return line
        if expr == "__timestamp__":
            return str(ts)
        parts = [p.strip() for p in expr.split("|")]
        v = lb.get(parts[0].lstrip("."), "")
        for fn in parts[1:]:
            v = {"lower": v.lower(), "upper": v.upper(), "trim": v.strip()}.get(fn, v)
        return v
    return re.sub(r"\{\{(.*?)\}\}", rep, template)


def line_format(template):
    return lambda ts, line, lb: (_render(template, ts, line, lb), lb)


def label_format(**assignments):
    """new=old renames (and drops old); new="{{.a}} {{.b}}" templates (keeps the sources)."""
    def f(ts, line, lb):
        out = dict(lb)
        for new, src in assignments.items():
            if "{{" in src:
                out[new] = _render(src, ts, line, lb)
            else:
                out[new] = lb.get(src, "")
                out.pop(src, None)
        return line, out
    return f


def drop(*names):
    return lambda ts, line, lb: (line, {k: v for k, v in lb.items() if k not in names})


def run(streams, matchers, stages, start=None, end=None):
    """Log query: returns [(labels, ts, line)] after the pipeline."""
    out = []
    for labels, entries in select(streams, matchers):
        for ts, line in entries:
            if (start is not None and ts < start) or (end is not None and ts > end):
                continue
            cur = (line, dict(labels))
            for st in stages:
                cur = st(ts, *cur)
                if cur is None:
                    break
            if cur is not None:
                out.append((cur[1], ts, cur[0]))
    return out


# ───────────────────────────────────────────── metric queries
def count_over_time(rows, end, rng):
    groups = defaultdict(int)
    for lb, ts, _ in rows:
        if end - rng < ts <= end:
            groups[tuple(sorted(lb.items()))] += 1
    return {k: v for k, v in groups.items()}


def rate(rows, end, rng):
    return {k: v / (rng / NS) for k, v in count_over_time(rows, end, rng).items()}


def sum_by(vector, by):
    out = defaultdict(float)
    for key, v in vector.items():
        d = dict(key)
        out[tuple((b, d.get(b, "")) for b in by)] += v
    return dict(out)


def unwrap_quantile(rows, end, rng, label, q, by=(), conv=float):
    """quantile_over_time(q, {...} | json | unwrap duration_seconds(label) [rng]) by (...)"""
    groups = defaultdict(list)
    for lb, ts, _ in rows:
        if end - rng < ts <= end and label in lb:
            try:
                groups[tuple((b, lb.get(b, "")) for b in by)].append(conv(lb[label]))
            except ValueError:
                continue
    out = {}
    for k, vs in groups.items():
        vs.sort()
        pos = q * (len(vs) - 1)
        lo, hi = math.floor(pos), math.ceil(pos)
        out[k] = vs[lo] + (vs[hi] - vs[lo]) * (pos - lo)
    return out


def topk(k, vector):
    return dict(sorted(vector.items(), key=lambda kv: -kv[1])[:k])


# ───────────────────────────────────────────── label design
BAD_NAMES = re.compile(r"(user_?id|userid|trace_?id|span_?id|request_?id|session|path|url|status_?code|ip|email|date|timestamp)", re.I)


def label_design(proposed):
    """proposed: {label: estimated distinct values}. Streams multiply, so a label with thousands of
    values creates thousands of tiny streams and chunks. Keep labels as locators, put content in the line."""
    streams = 1
    for n in proposed.values():
        streams *= max(1, n)
    verdict = {}
    for name, n in proposed.items():
        if BAD_NAMES.search(name) or n > 100:
            verdict[name] = "extract at query time with a parser instead"
        else:
            verdict[name] = "good locator"
    return streams, verdict


# ───────────────────────────────────────────── AWS equivalents
CLOUDWATCH_INSIGHTS = {
    'sum by (app) (count_over_time({env="prod"} |= "error" [5m]))':
        "filter @message like /error/ | stats count(*) by app, bin(5m)",
    'quantile_over_time(0.99, {app="web"} | json | unwrap duration_seconds(latency) [5m])':
        "stats pct(latency, 99) by bin(5m)",
    '{app="web"} | json | status >= 500 | line_format "{{.method}} {{.path}}"':
        "filter status >= 500 | fields method, path",
}
