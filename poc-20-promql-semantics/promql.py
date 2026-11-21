"""A small, exact model of how PromQL evaluates the parts interviewers ask about.

Not a parser: each function takes series as Python data so the arithmetic is visible.
A series is (labels: dict, samples: list[(t_seconds, value)]). A vector element is (labels, value).

Covers: instant selection with the 5-minute lookback, rate/increase with counter resets and
Prometheus' extrapolation, irate, delta, changes, histogram_quantile, aggregation with by/without,
and binary operators with one-to-one, many-to-one (group_left/group_right) and set matching.
"""
from __future__ import annotations

import math
from collections import defaultdict

LOOKBACK = 300.0  # seconds: an instant selector returns the newest sample at most 5 minutes old
NAME = "__name__"


def _key(labels, keep=None, drop=None):
    items = labels.items()
    if keep is not None:
        items = [(k, v) for k, v in items if k in keep]
    if drop is not None:
        items = [(k, v) for k, v in items if k not in drop]
    return tuple(sorted(items))


def without_name(labels):
    return {k: v for k, v in labels.items() if k != NAME}


# ───────────────────────────────────────────── selection
def instant(series, t, lookback=LOOKBACK):
    """Instant vector at time t: newest sample in (t - lookback, t] for each series.
    A series whose last sample is older than the lookback has gone stale and drops out."""
    out = []
    for labels, samples in series:
        inside = [s for s in samples if t - lookback < s[0] <= t]
        if inside:
            out.append((labels, inside[-1][1]))
    return out


def window(samples, t, rng):
    """Samples of a range selector [rng] evaluated at t: the left-open interval (t - rng, t]."""
    return [s for s in samples if t - rng < s[0] <= t]


# ───────────────────────────────────────────── counter functions
def _extrapolated(samples, t, rng, is_counter, is_rate):
    """Port of Prometheus' extrapolatedRate (promql/functions.go)."""
    pts = window(samples, t, rng)
    if len(pts) < 2:
        return None  # rate() needs at least two samples in the window
    first_t, first_v = pts[0]
    last_t, last_v = pts[-1]
    result = last_v - first_v
    if is_counter:  # a drop means the process restarted and the counter went back to zero
        prev = first_v
        for _, v in pts[1:]:
            if v < prev:
                result += prev
            prev = v
    range_start, range_end = t - rng, t
    to_start, to_end = first_t - range_start, range_end - last_t
    sampled = last_t - first_t
    avg_step = sampled / (len(pts) - 1)
    if is_counter and result > 0 and first_v >= 0:
        # a counter can't be extrapolated below zero: stop where it would have hit zero
        to_zero = sampled * (first_v / result)
        to_start = min(to_start, to_zero)
    threshold = avg_step * 1.1
    span = sampled
    span += to_start if to_start < threshold else avg_step / 2
    span += to_end if to_end < threshold else avg_step / 2
    result *= span / sampled
    return result / rng if is_rate else result


def rate(samples, t, rng):
    """Per-second average increase over the whole window, reset-aware and extrapolated."""
    return _extrapolated(samples, t, rng, True, True)


def increase(samples, t, rng):
    """rate() × range. Can be fractional for integer counters because of extrapolation."""
    return _extrapolated(samples, t, rng, True, False)


def delta(samples, t, rng):
    """For gauges: last minus first, extrapolated, can be negative, no reset handling."""
    return _extrapolated(samples, t, rng, False, False)


def irate(samples, t, rng):
    """Uses only the last two samples in the window: responsive, noisy, for graphs not alerts."""
    pts = window(samples, t, rng)
    if len(pts) < 2:
        return None
    (t1, v1), (t2, v2) = pts[-2], pts[-1]
    d = v2 if v2 < v1 else v2 - v1  # after a reset the new value is the increase
    return d / (t2 - t1)


def changes(samples, t, rng):
    pts = window(samples, t, rng)
    return sum(1 for a, b in zip(pts, pts[1:]) if a[1] != b[1])


# ───────────────────────────────────────────── histograms
def histogram_quantile(q, buckets):
    """buckets: list of (le, cumulative_count) for ONE series group, le may be math.inf.
    Linear interpolation inside the bucket that contains the rank, as Prometheus does."""
    if q < 0:
        return -math.inf
    if q > 1:
        return math.inf
    b = sorted(buckets, key=lambda x: x[0])
    if len(b) < 2 or b[-1][0] != math.inf:
        return math.nan
    fixed, top = [], 0.0  # Prometheus forces bucket counts to be monotonic
    for le, c in b:
        top = max(top, c)
        fixed.append((le, top))
    total = fixed[-1][1]
    if total == 0:
        return math.nan
    rank = q * total
    i = next(k for k, (_, c) in enumerate(fixed) if c >= rank)
    if i == len(fixed) - 1:  # rank fell in +Inf: the best answer is the highest finite bound
        return fixed[-2][0]
    end, count = fixed[i]
    if i == 0:
        start, prev = (0.0 if end > 0 else end), 0.0
    else:
        start, prev = fixed[i - 1]
    if count == prev:
        return end
    return start + (end - start) * (rank - prev) / (count - prev)


# ───────────────────────────────────────────── aggregation
def aggregate(op, vector, by=None, without=None):
    groups = defaultdict(list)
    for labels, v in vector:
        base = without_name(labels)
        key = _key(base, keep=by) if by is not None else _key(base, drop=set(without or ()))
        groups[key].append(v)
    fn = {"sum": sum, "count": len, "max": max, "min": min, "avg": lambda xs: sum(xs) / len(xs)}[op]
    return [(dict(k), fn(groups[k])) for k in sorted(groups)]


# ───────────────────────────────────────────── binary operators
OPS = {"+": lambda a, b: a + b, "-": lambda a, b: a - b, "*": lambda a, b: a * b, "/": lambda a, b: a / b if b else math.nan}


def _match_key(labels, on, ignoring):
    base = without_name(labels)
    if on is not None:
        return _key(base, keep=set(on))
    return _key(base, drop=set(ignoring or ()))


def binop(op, left, right, on=None, ignoring=None, group_left=None, group_right=None):
    """Arithmetic between two vectors. One-to-one by default: both sides must match on the
    chosen labels and each key may appear once. group_left(extra) allows many on the left and
    copies `extra` labels from the single matching right element (and vice versa)."""
    many_side, one_side, include, flip = left, right, group_left, False
    if group_right is not None:
        many_side, one_side, include, flip = right, left, group_right, True
    one_index = defaultdict(list)
    for labels, v in one_side:
        one_index[_match_key(labels, on, ignoring)].append((labels, v))
    for k, els in one_index.items():
        if len(els) > 1:
            raise ValueError(f"many-to-many matching not allowed: duplicate {dict(k)} on the 'one' side")
    if group_left is None and group_right is None:
        seen = defaultdict(int)
        for labels, _ in many_side:
            seen[_match_key(labels, on, ignoring)] += 1
        dup = [dict(k) for k, n in seen.items() if n > 1 and k in one_index]
        if dup:
            raise ValueError(f"multiple matches for labels {dup}: use group_left or group_right")
    out = []
    for labels, v in many_side:
        k = _match_key(labels, on, ignoring)
        if k not in one_index:
            continue  # unmatched elements are silently dropped
        other_labels, w = one_index[k][0]
        a, b = (w, v) if flip else (v, w)
        if include is None:  # one-to-one: result keeps only the matching labels
            res = dict(k) if on is not None else without_name(labels)
        else:
            res = without_name(labels)
            for extra in include:
                if extra in other_labels:
                    res[extra] = other_labels[extra]
        out.append((res, OPS[op](a, b)))
    return sorted(out, key=lambda e: sorted(e[0].items()))


def set_op(op, left, right, on=None, ignoring=None):
    """and / or / unless: many-to-many allowed; values always come from the side that is kept."""
    rkeys = {_match_key(l, on, ignoring) for l, _ in right}
    if op == "and":
        return [e for e in left if _match_key(e[0], on, ignoring) in rkeys]
    if op == "unless":
        return [e for e in left if _match_key(e[0], on, ignoring) not in rkeys]
    if op == "or":
        lkeys = {_match_key(l, on, ignoring) for l, _ in left}
        return left + [e for e in right if _match_key(e[0], on, ignoring) not in lkeys]
    raise ValueError(op)


def compare(vector, op, threshold, as_bool=False):
    """Comparison filters a vector unless `bool` is used, which returns 0/1 for every element."""
    f = {">": lambda v: v > threshold, "<": lambda v: v < threshold, ">=": lambda v: v >= threshold,
         "<=": lambda v: v <= threshold, "==": lambda v: v == threshold, "!=": lambda v: v != threshold}[op]
    if as_bool:
        return [(without_name(l), 1.0 if f(v) else 0.0) for l, v in vector]
    return [(l, v) for l, v in vector if f(v)]
