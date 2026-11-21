"""Scaling Prometheus past one server: remote write sizing, HA deduplication in Thanos, Mimir and
VictoriaMetrics, Thanos downsampling and query splitting, and Thanos Receive hashrings.
"""
from __future__ import annotations

import bisect
import hashlib
import math
from collections import defaultdict


# ───────────────────────────────────────────── remote write
def remote_write_plan(samples_per_sec, capacity=2500, max_samples_per_send=500, max_shards=200, wal_hours=2.0):
    """Mastering Prometheus ch9 tuning rules: min_shards ≈ ingestion rate / capacity, capacity at least
    3 × max_samples_per_send, and an outage longer than the WAL (~2h) loses data."""
    warnings = []
    if capacity < 3 * max_samples_per_send:
        warnings.append("capacity should be at least 3x max_samples_per_send")
    min_shards = max(1, math.ceil(samples_per_sec / capacity))
    if min_shards > max_shards:
        warnings.append("ingestion exceeds max_shards x capacity: raise capacity and max_samples_per_send, lower max_shards for memory")
    return {"min_shards": min_shards, "buffered_samples_at_max": max_shards * capacity,
            "tolerated_outage_hours": wal_hours, "warnings": warnings}


def backoff_schedule(min_backoff=0.03, max_backoff=5.0, attempts=12):
    out, d = [], min_backoff
    for _ in range(attempts):
        out.append(round(d, 3))
        d = min(d * 2, max_backoff)
    return out


# ───────────────────────────────────────────── HA deduplication
def dedup_thanos(replicas):
    """Thanos Query style, simplified: stick to one replica and only switch when it has no sample
    where another replica does, so a restart on one replica leaves no gap in the result and the
    output doesn't flip-flop between replicas. replicas: {name: [(t, v)]}."""
    names = sorted(replicas)
    by = {n: dict(replicas[n]) for n in names}
    cur, out = names[0], []
    for t in sorted({t for s in replicas.values() for t, _ in s}):
        if t not in by[cur]:
            cur = next(n for n in names if t in by[n])
        out.append((t, by[cur][t], cur))
    return out


def dedup_mimir(replicas, elected, failover_after, now_series):
    """Mimir HA tracker: accept samples only from the elected replica; if it is silent for
    `failover_after` seconds, elect another. Samples from the gap are lost."""
    accepted, leader, last_seen = [], elected, None
    for t in now_series:
        if t in replicas[leader]:
            accepted.append((t, leader)); last_seen = t
        elif last_seen is not None and t - last_seen > failover_after:
            others = [n for n in replicas if n != leader and t in replicas[n]]
            if others:
                leader = others[0]
                accepted.append((t, leader)); last_seen = t
    return accepted


def dedup_victoria(samples, min_scrape_interval):
    """VictoriaMetrics: identical external labels on both replicas, then keep one sample per interval."""
    out, bucket_seen = [], set()
    for t, v in sorted(samples):
        b = t // min_scrape_interval
        if b not in bucket_seen:
            bucket_seen.add(b); out.append((t, v))
    return out


# ───────────────────────────────────────────── Thanos compactor
def downsample(samples, resolution):
    """One aggregate per resolution window: count, sum, min, max, and a counter value for rate()."""
    buckets = defaultdict(list)
    for t, v in samples:
        buckets[t // resolution * resolution].append(v)
    return [{"t": k, "count": len(v), "sum": sum(v), "min": min(v), "max": max(v), "counter": v[-1]} for k, v in sorted(buckets.items())]


def downsample_plan(age_hours):
    """Which resolutions exist for a block of this age: raw, plus 5m after 40h, plus 1h after 10 days."""
    res = ["raw"]
    if age_hours > 40:
        res.append("5m")
    if age_hours > 24 * 10:
        res.append("1h")
    return res


def queryable(age_days, retention):
    """With per-resolution retention, which resolutions can still answer a query this old?
    retention: {"raw": days, "5m": days, "1h": days}. Different values make old data unreachable at
    fine steps, which is why the book says keep them equal unless you know why."""
    return [r for r in ("raw", "5m", "1h") if age_days <= retention[r]]


# ───────────────────────────────────────────── Thanos Query Frontend
def split_by_interval(start, end, interval):
    out, s = [], start
    while s < end:
        e = min(end, (s // interval + 1) * interval)
        out.append((s, e)); s = e
    return out


class ResultCache:
    """Range-query results cached per split; a longer range only fetches the missing splits."""

    def __init__(self):
        self.store, self.fetches = {}, 0

    def query(self, start, end, interval, compute):
        out = []
        for s, e in split_by_interval(start, end, interval):
            if (s, e) not in self.store:
                self.fetches += 1
                self.store[(s, e)] = compute(s, e)
            out.append(self.store[(s, e)])
        return out


# ───────────────────────────────────────────── Thanos Receive hashring
def _h(key):
    return int.from_bytes(hashlib.md5(key.encode()).digest()[:8], "big")


def hashmod_ring(series, nodes):
    return {s: nodes[_h(s) % len(nodes)] for s in series}


def ketama_ring(series, nodes, vnodes=100):
    ring = sorted((_h(f"{n}-{i}"), n) for n in nodes for i in range(vnodes))
    keys = [k for k, _ in ring]
    out = {}
    for s in series:
        i = bisect.bisect(keys, _h(s)) % len(ring)
        out[s] = ring[i][1]
    return out


def moved(before, after):
    return sum(1 for k in before if before[k] != after[k]) / len(before)


def write_quorum(replication_factor):
    """A write succeeds when (RF + 1) // 2 receivers accept it."""
    return (replication_factor + 1) // 2


# ───────────────────────────────────────────── choosing a backend
def recommend(needs):
    """Turn the trade-offs from the book into a decision. needs: set of strings."""
    if "aws-managed" in needs:
        return "Amazon Managed Service for Prometheus (Cortex-based, object storage, SigV4 remote write)"
    if "global-view-without-central-ingest" in needs:
        return "Thanos (sidecar + query + store + compact)"
    if "lowest-resource-use" in needs and "object-storage" not in needs:
        return "VictoriaMetrics single node (vertically scale first)"
    if "multi-tenant" in needs or "object-storage" in needs:
        return "Grafana Mimir (microservices mode, object storage, X-Scope-OrgID tenants)"
    return "Prometheus with local storage and a Thanos sidecar when you need more"
