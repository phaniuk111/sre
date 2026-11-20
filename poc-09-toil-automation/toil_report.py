"""Measure toil before automating it (book ch. 13).

Input: a ticket/page export (CSV) with columns
    id, created, category, minutes_spent, actionable (true/false), automated_fix_available (true/false)
Output:
  * operational load % of team capacity  (book: must stay < 50%; it's a threshold, not a target)
  * % unactionable alerts                 (noise to delete or tune)
  * top toil classes                      (fix whole classes, not single tickets)
  * automation priority list using two strategies:
      - ROI-first:     biggest (minutes saved/year) / build cost
      - snowball:      fastest-first quick wins, to build trust and buy-in
"""
from __future__ import annotations

import csv
import sys
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class ClassStats:
    category: str
    count: int
    minutes: float
    unactionable: int


def load(path: str) -> List[dict]:
    with open(path) as f:
        return list(csv.DictReader(f))


def analyse(rows: List[dict], team_size: int, weeks: float, hours_per_week: float = 40) -> Dict:
    by_cat: Dict[str, ClassStats] = {}
    for r in rows:
        c = by_cat.setdefault(r["category"], ClassStats(r["category"], 0, 0.0, 0))
        c.count += 1
        c.minutes += float(r["minutes_spent"])
        c.unactionable += r["actionable"].strip().lower() != "true"
    total_minutes = sum(c.minutes for c in by_cat.values())
    capacity_minutes = team_size * weeks * hours_per_week * 60
    classes = sorted(by_cat.values(), key=lambda c: c.minutes, reverse=True)
    return {
        "ops_load_pct": round(100 * total_minutes / capacity_minutes, 1),
        "over_50pct_threshold": total_minutes / capacity_minutes > 0.5,
        "unactionable_pct": round(100 * sum(c.unactionable for c in classes) / max(1, len(rows)), 1),
        "top_classes": [(c.category, c.count, round(c.minutes / 60, 1)) for c in classes[:5]],
    }


def prioritise(rows: List[dict], build_cost_hours: Dict[str, float], weeks: float) -> Dict[str, List[str]]:
    yearly_minutes: Dict[str, float] = defaultdict(float)
    for r in rows:
        yearly_minutes[r["category"]] += float(r["minutes_spent"]) * 52 / weeks
    roi = sorted(build_cost_hours, key=lambda c: (yearly_minutes[c] / 60) / build_cost_hours[c], reverse=True)
    snowball = sorted(build_cost_hours, key=lambda c: build_cost_hours[c])
    return {"roi_first": roi, "snowball_fastest_first": snowball}


if __name__ == "__main__":
    rows = load(sys.argv[1] if len(sys.argv) > 1 else "examples/tickets.csv")
    import json
    print(json.dumps(analyse(rows, team_size=6, weeks=4), indent=2))
    print(json.dumps(prioritise(rows, {"disk-full": 16, "cert-renewal": 8, "restart-stuck-worker": 40, "quota-increase": 4}, 4), indent=2))
