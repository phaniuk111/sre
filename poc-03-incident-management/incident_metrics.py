"""Incident effectiveness metrics beyond MTTR (ch. 10 "Measuring the
Effectiveness of Incident Response").

Given an incident timeline (e.g. exported from AWS Incident Manager), compute:
  * TTD  - time to detect   (impact start -> detection)
  * TTM  - time to mitigate (detection -> user impact contained)  <- primary goal
  * TTR  - time to resolve  (detection -> resolved)
  * cost of coordination proxies (Laura Maguire / Courtney Nash's VOID):
      number of distinct responders and teams, pages per incident,
      and handoffs - better improvement signals than MTTR alone.
  * whether it was detected by monitoring or by a human (customer/engineer):
      a high "% manually detected" means SLIs or coverage are wrong (ch. 4).
"""
from __future__ import annotations

import json
import statistics
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional


def _t(s: Optional[str]) -> Optional[datetime]:
    return datetime.fromisoformat(s.replace("Z", "+00:00")) if s else None


@dataclass
class Incident:
    id: str
    impact_start: datetime
    detected: datetime
    mitigated: Optional[datetime]
    resolved: Optional[datetime]
    detected_by: str  # "alert" | "customer" | "engineer"
    responders: List[Dict[str, str]]  # [{"name":..., "team":..., "role":...}]
    pages: int
    handoffs: int = 0

    @classmethod
    def from_dict(cls, d: dict) -> "Incident":
        return cls(
            id=d["id"],
            impact_start=_t(d["impact_start"]),
            detected=_t(d["detected"]),
            mitigated=_t(d.get("mitigated")),
            resolved=_t(d.get("resolved")),
            detected_by=d.get("detected_by", "alert"),
            responders=d.get("responders", []),
            pages=d.get("pages", 1),
            handoffs=d.get("handoffs", 0),
        )

    def minutes(self, a: Optional[datetime], b: Optional[datetime]) -> Optional[float]:
        return (b - a).total_seconds() / 60 if a and b else None

    @property
    def ttd(self) -> float:
        return self.minutes(self.impact_start, self.detected)

    @property
    def ttm(self) -> Optional[float]:
        return self.minutes(self.detected, self.mitigated)

    @property
    def ttr(self) -> Optional[float]:
        return self.minutes(self.detected, self.resolved)

    @property
    def people(self) -> int:
        return len({r["name"] for r in self.responders})

    @property
    def teams(self) -> int:
        return len({r["team"] for r in self.responders})

    @property
    def has_incident_commander(self) -> bool:
        return any(r.get("role") == "IC" for r in self.responders)


def summarise(incidents: List[Incident]) -> Dict[str, float]:
    def med(xs):
        xs = [x for x in xs if x is not None]
        return round(statistics.median(xs), 1) if xs else None

    return {
        "incidents": len(incidents),
        "median_ttd_min": med(i.ttd for i in incidents),
        "median_ttm_min": med(i.ttm for i in incidents),
        "median_ttr_min": med(i.ttr for i in incidents),
        "pct_manually_detected": round(100 * sum(i.detected_by != "alert" for i in incidents) / len(incidents), 1),
        "median_people": med(i.people for i in incidents),
        "median_teams": med(i.teams for i in incidents),
        "pages_per_incident": round(sum(i.pages for i in incidents) / len(incidents), 2),
        "pct_without_ic": round(100 * sum(not i.has_incident_commander for i in incidents) / len(incidents), 1),
    }


if __name__ == "__main__":
    data = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "examples/incidents.json"))
    print(json.dumps(summarise([Incident.from_dict(d) for d in data]), indent=2))
