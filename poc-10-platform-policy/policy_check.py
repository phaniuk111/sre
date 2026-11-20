"""Platform policy compliance checker (book ch. 18 'Platform Policies',
'Legibility and Introspection', 'Green Fields and Brown Fields').

Introspects a service catalog (what Backstage/your IDP or AWS Service Catalog
AppRegistry knows about each service) and evaluates platform policies like:
  * customer-facing services run in >= 2 points of presence (AZs)
  * alerts route to an ACTIVE team, not into the void
  * every service defines SLOs
  * on-call load is below a threshold
  * deployments are progressive (no all-at-once)

Enforcement levels mirror paths & guardrails:
  advise -> warn -> block   (block = CI fails for NEW services / substantive changes)
Brownfield services get explicit, time-boxed EXEMPTIONS (policy, service, bug,
valid_until, reason) that are legible to leadership, never silent waivers.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import date
from typing import Callable, Dict, List

import yaml


@dataclass
class Policy:
    id: str
    description: str
    level: str  # advise | warn | block
    check: Callable[[dict, dict], bool]


def _teams_active(svc: dict, ctx: dict) -> bool:
    return svc.get("alert_route") in ctx.get("active_teams", [])


POLICIES: List[Policy] = [
    Policy("location/multi-az", "Customer-facing services run in >= 2 AZs", "block",
           lambda s, c: not s.get("customer_facing") or len(s.get("azs", [])) >= 2),
    Policy("alerting/routes-to-active-team", "Alerts route to an active on-call team", "block", _teams_active),
    Policy("slo/defined", "Service defines at least one committed SLO", "warn",
           lambda s, c: any(x.get("lifecycle") == "committed" for x in s.get("slos", []))),
    Policy("oncall/load", "On-call load <= 2 incidents per shift", "warn",
           lambda s, c: s.get("incidents_per_shift", 0) <= 2),
    Policy("release/progressive", "Deployments are progressive (canary/linear)", "block",
           lambda s, c: s.get("deploy_strategy") in {"canary", "linear", "blue_green"}),
    Policy("data/backups-tagged", "Stateful services have a data-tier tag (POC 08)", "warn",
           lambda s, c: not s.get("stateful") or s.get("data_tier") in {"tier0", "tier1", "tier2"}),
]


def exemption_for(policy_id: str, service: str, exemptions: List[dict], today: date):
    for e in exemptions:
        if e["policy"] == policy_id and service in e["services"]:
            return e if date.fromisoformat(e["valid_until"]) >= today else {**e, "expired": True}
    return None


def evaluate(catalog: dict, exemptions: List[dict], today: date) -> Dict[str, List[dict]]:
    ctx = {"active_teams": catalog.get("active_teams", [])}
    report: Dict[str, List[dict]] = {"block": [], "warn": [], "advise": [], "exempt": []}
    for svc in catalog["services"]:
        for p in POLICIES:
            if p.check(svc, ctx):
                continue
            ex = exemption_for(p.id, svc["name"], exemptions, today)
            finding = {"service": svc["name"], "policy": p.id, "why": p.description}
            if ex and not ex.get("expired"):
                report["exempt"].append({**finding, "reason": ex["reason"], "bug": ex["bug"], "valid_until": ex["valid_until"]})
                continue
            level = p.level
            # Greenfield: new services can't merge non-compliant config at all.
            if svc.get("greenfield") and level == "warn":
                level = "block"
            if ex and ex.get("expired"):
                finding["note"] = f"exemption expired {ex['valid_until']}"
            report[level].append(finding)
    return report


if __name__ == "__main__":
    catalog = yaml.safe_load(open(sys.argv[1] if len(sys.argv) > 1 else "examples/catalog.yaml"))
    exemptions = yaml.safe_load(open(sys.argv[2] if len(sys.argv) > 2 else "examples/exemptions.yaml"))
    rep = evaluate(catalog, exemptions, date.today())
    for level in ("block", "warn", "advise", "exempt"):
        for f in rep[level]:
            print(f"[{level.upper():6}] {f['service']:12} {f['policy']:32} {f.get('reason', f.get('note', ''))}")
    sys.exit(1 if rep["block"] else 0)
