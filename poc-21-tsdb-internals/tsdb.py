"""How the Prometheus TSDB stores samples and finds series, small enough to read in one sitting.

1. Gorilla-style compression as Prometheus' XOR chunk does it: delta-of-delta timestamps and
   XOR'd float values, counted in bits so you can see why scrape jitter costs disk.
2. The timestamp tolerance fix (--scrape.timestamp-tolerance): snap near-perfect intervals.
3. The inverted index: postings lists per label pair, intersected for a selector.
4. Block compaction ranges: 2h blocks merged in steps of three, capped at 31 days or 10% of retention.
5. A cardinality report over the text exposition format, like /tsdb-status, and scrape limits.
"""
from __future__ import annotations

import bisect
import re
import struct
from collections import Counter, defaultdict

HOUR = 3600 * 1000  # the TSDB works in milliseconds


# ───────────────────────────────────────────── 1. compression
def _uvarint_bits(x):
    n = 1
    while x >= 0x80:
        x >>= 7
        n += 1
    return 8 * n


def _varint_bits(x):
    return _uvarint_bits((x << 1) ^ (x >> 63) if x >= 0 else ((-x) << 1) - 1)


def _fits(v, nbits):
    return -(1 << (nbits - 1)) + 1 <= v <= (1 << (nbits - 1))


def timestamp_bits(ts):
    """Bits Prometheus' XOR chunk spends on timestamps (ms)."""
    bits = _varint_bits(ts[0])
    if len(ts) > 1:
        bits += _uvarint_bits(ts[1] - ts[0])
    prev_delta = ts[1] - ts[0] if len(ts) > 1 else 0
    for a, b in zip(ts[1:], ts[2:]):
        d = b - a
        dod = d - prev_delta
        prev_delta = d
        if dod == 0:
            bits += 1
        elif _fits(dod, 14):
            bits += 2 + 14
        elif _fits(dod, 17):
            bits += 3 + 17
        elif _fits(dod, 20):
            bits += 4 + 20
        else:
            bits += 4 + 64
    return bits


def _f2i(v):
    return struct.unpack(">Q", struct.pack(">d", float(v)))[0]


def value_bits(vals):
    """Bits for float values: XOR with the previous value, reuse the previous leading/trailing window."""
    bits = 64
    prev = _f2i(vals[0])
    lead, trail = 0xFF, 0
    for v in vals[1:]:
        cur = _f2i(v)
        x = prev ^ cur
        prev = cur
        if x == 0:
            bits += 1
            continue
        nl = min(64 - x.bit_length(), 31)
        nt = (x & -x).bit_length() - 1
        if lead != 0xFF and nl >= lead and nt >= trail:
            bits += 2 + (64 - lead - trail)
        else:
            lead, trail = nl, nt
            bits += 2 + 5 + 6 + (64 - nl - nt)
    return bits


def bytes_per_sample(ts, vals):
    return (timestamp_bits(ts) + value_bits(vals)) / 8 / len(ts)


def snap_timestamps(ts, interval_ms, tolerance_ms=2):
    """--scrape.timestamp-tolerance: if a scrape lands within tolerance of the expected time, store
    the expected time. Max allowed tolerance is 1% of the scrape interval."""
    tolerance_ms = min(tolerance_ms, interval_ms // 100)
    out = [ts[0]]
    for t in ts[1:]:
        expected = out[-1] + interval_ms
        out.append(expected if abs(t - expected) <= tolerance_ms else t)
    return out


def jitter_report(ts, interval_ms, tolerance_ms=2):
    """Like oy-scrape-jitter for one target: is it aligned within tolerance, and the max offset."""
    offsets = [abs((b - a) - interval_ms) for a, b in zip(ts, ts[1:])]
    return {"aligned": max(offsets) <= tolerance_ms, "max_ms": max(offsets)}


# ───────────────────────────────────────────── 3. inverted index
class Index:
    """Series IDs are assigned in sorted label order, so every postings list is sorted and
    intersecting them is a merge, which is why a selector with a rare label is fast."""

    def __init__(self, series):
        ordered = sorted(series, key=lambda s: sorted(s.items()))
        self.series = ordered
        self.postings = defaultdict(list)
        for sid, labels in enumerate(ordered):
            for k, v in labels.items():
                self.postings[(k, v)].append(sid)
        self.values = defaultdict(set)
        for k, v in self.postings:
            self.values[k].add(v)

    def _list_for(self, name, op, val):
        if op == "=":
            return self.postings.get((name, val), [])
        rx = re.compile(f"^(?:{val})$")
        ids = set()
        for v in self.values.get(name, ()):
            if bool(rx.match(v)) == (op == "=~"):
                ids.update(self.postings[(name, v)])
        return sorted(ids)

    def select(self, matchers):
        """matchers: list of (name, op, value) with op in = =~ !~. Returns (labels, comparisons)."""
        lists = sorted((self._list_for(*m) for m in matchers), key=len)
        result, work = lists[0], 0
        for other in lists[1:]:
            merged, lo = [], 0
            for sid in result:  # Seek(): binary search forward in the longer list instead of walking it
                lo = bisect.bisect_left(other, sid, lo)
                work += max(1, len(other).bit_length())
                if lo < len(other) and other[lo] == sid:
                    merged.append(sid)
            result = merged
        return [self.series[i] for i in result], work


# ───────────────────────────────────────────── 4. compaction
def compaction_ranges(retention_days, base_hours=2, step=3, max_days=31):
    """Block durations the compactor will create: 2h, 6h, 18h, 54h ... capped at 31 days or 10% of retention."""
    cap = min(max_days * 24, retention_days * 24 * 0.10)
    out, r = [], base_hours
    while r <= cap:
        out.append(r)
        r *= step
    return out


# ───────────────────────────────────────────── 5. cardinality
LINE = re.compile(r'^([a-zA-Z_:][a-zA-Z0-9_:]*)(?:\{(.*)\})?\s+(\S+)')
PAIR = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*)="((?:[^"\\]|\\.)*)"')


def parse_exposition(text):
    out = []
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue
        m = LINE.match(line)
        if m:
            labels = {"__name__": m.group(1), **dict(PAIR.findall(m.group(2) or ""))}
            out.append((labels, float(m.group(3))))
    return out


def cardinality_report(series, top=10):
    by_metric = Counter(s["__name__"] for s, _ in series)
    values = defaultdict(set)
    pairs = Counter()
    for s, _ in series:
        for k, v in s.items():
            values[k].add(v)
            pairs[f"{k}={v}"] += 1
    return {
        "series": len(series),
        "label_value_counts": sorted(((k, len(v)) for k, v in values.items() if k != "__name__"), key=lambda x: -x[1])[:top],
        "series_by_metric": by_metric.most_common(top),
        "series_by_pair": pairs.most_common(top),
        "everywhere": [p for p, n in pairs.items() if n == len(series) and not p.startswith("__name__")],
    }


def apply_limits(series, sample_limit=0, label_limit=0, label_value_length_limit=0, label_name_length_limit=0):
    """Limits are checked after metric relabeling. Any breach fails the WHOLE scrape: nothing is stored
    and up becomes 0, so alert on failed scrapes when you turn limits on."""
    if sample_limit and len(series) > sample_limit:
        return False, f"sample_limit exceeded: {len(series)} > {sample_limit}"
    for s, _ in series:
        names = [k for k in s if k != "__name__"]
        if label_limit and len(names) > label_limit:
            return False, f"label_limit exceeded on {s['__name__']}"
        if label_value_length_limit and any(len(v) > label_value_length_limit for k, v in s.items() if k != "__name__"):
            return False, f"label_value_length_limit exceeded on {s['__name__']}"
        if label_name_length_limit and any(len(k) > label_name_length_limit for k in names):
            return False, f"label_name_length_limit exceeded on {s['__name__']}"
    return True, "ok"
