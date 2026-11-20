"""Failure concentration: who is actually being hurt? (ch. 8 "Measuring SLO
Failure Concentration").

A single 99.9% compliance number can hide a cohort (say Firefox + Enterprise
users) that fails 95% of the time. The book uses entropy loss with a decision
tree (scikit-learn DecisionTreeClassifier) to surface the feature split that
"surprises" you. This is a dependency-free version: for every label value and
every pair of label values, compute information gain on the success/failure
outcome and stack-rank them.
"""
from __future__ import annotations

import math
from collections import Counter
from itertools import combinations
from typing import Dict, List, Sequence, Tuple

Event = Tuple[Dict[str, str], bool]  # (labels, failed?)


def _entropy(failed: int, total: int) -> float:
    if total == 0 or failed in (0, total):
        return 0.0
    p = failed / total
    return -(p * math.log2(p) + (1 - p) * math.log2(1 - p))


def information_gain(events: Sequence[Event], predicate) -> Tuple[float, float, int]:
    """Return (gain, error_rate_inside_split, size_of_split)."""
    total = len(events)
    failed = sum(f for _, f in events)
    inside = [f for labels, f in events if predicate(labels)]
    outside_failed = failed - sum(inside)
    outside_total = total - len(inside)
    h_before = _entropy(failed, total)
    h_after = (len(inside) / total) * _entropy(sum(inside), len(inside)) + (outside_total / total) * _entropy(outside_failed, outside_total)
    rate = sum(inside) / len(inside) if inside else 0.0
    return h_before - h_after, rate, len(inside)


def rank_cohorts(events: Sequence[Event], max_depth: int = 2, min_size: int = 20) -> List[Tuple[str, float, float, int]]:
    """Stack-rank label combinations by how much they explain failures."""
    values: Counter = Counter()
    for labels, _ in events:
        for k, v in labels.items():
            values[(k, v)] += 1
    singles = [kv for kv, c in values.items() if c >= min_size]
    candidates = [(kv,) for kv in singles]
    if max_depth >= 2:
        candidates += [pair for pair in combinations(singles, 2) if pair[0][0] != pair[1][0]]
    results = []
    for combo in candidates:
        pred = lambda labels, combo=combo: all(labels.get(k) == v for k, v in combo)  # noqa: E731
        gain, rate, size = information_gain(events, pred)
        if size >= min_size:
            results.append((" & ".join(f"{k}={v}" for k, v in combo), gain, rate, size))
    return sorted(results, key=lambda r: r[1], reverse=True)
