"""Backup SLOs (book ch. 16): RPO, RTO and RWO compliance across a fleet.

Book example SLO: "backups for 99% of data sources are within RPO 99% of the time".

Inputs are what AWS Backup gives you:
  * ListRecoveryPointsByResource  -> recovery point creation times per resource
  * restore testing jobs          -> restore durations (the RTO you actually have)
Pass `--live` to read from your account with boto3; otherwise it reads sample JSON.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Sequence

TIER_OBJECTIVES = {
    # tier: (RPO, RTO, RWO)
    "tier0": (timedelta(hours=1), timedelta(hours=2), timedelta(days=35)),
    "tier1": (timedelta(hours=24), timedelta(hours=12), timedelta(days=30)),
    "tier2": (timedelta(days=7), timedelta(days=2), timedelta(days=90)),
}


@dataclass
class DataSource:
    arn: str
    tier: str
    recovery_points: List[datetime]
    restore_durations: List[timedelta]


def rpo_compliance(src: DataSource, start: datetime, end: datetime, step: timedelta = timedelta(hours=1)) -> float:
    """Fraction of sampled instants at which the newest recovery point was younger than RPO."""
    rpo = TIER_OBJECTIVES[src.tier][0]
    pts = sorted(src.recovery_points)
    t, ok, total = start, 0, 0
    while t <= end:
        newest = max((p for p in pts if p <= t), default=None)
        ok += newest is not None and t - newest <= rpo
        total += 1
        t += step
    return ok / total if total else 0.0


def rwo_ok(src: DataSource, now: datetime) -> bool:
    """Can we restore to a point as old as the RWO requires?"""
    rwo = TIER_OBJECTIVES[src.tier][2]
    return bool(src.recovery_points) and min(src.recovery_points) <= now - rwo + timedelta(days=1)


def rto_ok(src: DataSource) -> bool:
    """Untested restores count as failures: no evidence, no RTO."""
    rto = TIER_OBJECTIVES[src.tier][1]
    return bool(src.restore_durations) and max(src.restore_durations) <= rto


def fleet_report(sources: Sequence[DataSource], start: datetime, end: datetime, per_source_target: float = 0.99) -> Dict:
    per = {s.arn: rpo_compliance(s, start, end) for s in sources}
    meeting = [a for a, c in per.items() if c >= per_source_target]
    return {
        "sources": len(sources),
        "pct_sources_meeting_rpo_slo": round(100 * len(meeting) / len(sources), 1),
        "slo_met": len(meeting) / len(sources) >= 0.99,
        "untested_or_slow_restores": [s.arn for s in sources if not rto_ok(s)],
        "rwo_gaps": [s.arn for s in sources if not rwo_ok(s, end)],
        "per_source_rpo_compliance": {a: round(c, 4) for a, c in per.items()},
    }


def load_sample(path: str) -> List[DataSource]:
    raw = json.load(open(path))
    p = lambda s: datetime.fromisoformat(s.replace("Z", "+00:00"))  # noqa: E731
    return [DataSource(d["arn"], d["tier"], [p(x) for x in d["recovery_points"]],
                       [timedelta(minutes=m) for m in d.get("restore_minutes", [])]) for d in raw]


def load_live(tier_tag: str = "data-tier") -> List[DataSource]:  # pragma: no cover - needs AWS
    import boto3
    backup = boto3.client("backup")
    tagging = boto3.client("resourcegroupstaggingapi")
    out = []
    for page in tagging.get_paginator("get_resources").paginate(TagFilters=[{"Key": tier_tag}]):
        for r in page["ResourceTagMappingList"]:
            tier = next(t["Value"] for t in r["Tags"] if t["Key"] == tier_tag)
            pts = []
            for rp in backup.get_paginator("list_recovery_points_by_resource").paginate(ResourceArn=r["ResourceARN"]):
                pts += [x["CreationDate"] for x in rp["RecoveryPoints"] if x.get("Status") == "COMPLETED"]
            out.append(DataSource(r["ResourceARN"], tier, pts, []))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--sample", default="examples/recovery_points.json")
    ap.add_argument("--days", type=int, default=7)
    a = ap.parse_args()
    srcs = load_live() if a.live else load_sample(a.sample)
    end = datetime.now(timezone.utc) if a.live else max(max(s.recovery_points) for s in srcs)
    print(json.dumps(fleet_report(srcs, end - timedelta(days=a.days), end), indent=2))
