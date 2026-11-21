"""Reliability shifted down: risk profiles, operation invariants and platform SLOs.

Reliability chapter:
  * "risk profiles": a service's criticality and remaining error budget set its
    deployment policy, so nobody has to judge how careful to be with each change.
  * "preventing unsafe operations": invariants are enforced by the platform, not
    by documentation. Example: a drain that would take out several regions is
    rejected. Break-glass exists, and is loud.
  * "reliability of the platform": the platform needs its own, stricter SLOs,
    counting system-caused failures only.

AWS: stages map to CodeDeploy deployment configurations or AppConfig deployment
strategies (see terraform/); drains are Route 53 ARC zonal shifts / routing
control changes guarded by ARC safety rules; platform SLOs live in CloudWatch.
Canary statistics themselves are in POC 05.
"""
from __future__ import annotations

MIN_PER_YEAR = 365.25 * 24 * 60


def allowed_downtime_minutes(slo: float, minutes: float = MIN_PER_YEAR) -> float:
    """99.9% -> about 526 minutes (8.77 hours) a year."""
    return round((1 - slo) * minutes, 2)


# tier -> base policy. Tier 1 = critical user-facing, 3 = internal tool.
_BASE = {
    1: {"stages": [1, 10, 50, 100], "bake_minutes": 60, "canary_analysis": "required", "auto_rollback": True, "regions_at_once": 1, "approvals": 1},
    2: {"stages": [10, 50, 100], "bake_minutes": 20, "canary_analysis": "required", "auto_rollback": True, "regions_at_once": 1, "approvals": 0},
    3: {"stages": [100], "bake_minutes": 5, "canary_analysis": "advisory", "auto_rollback": True, "regions_at_once": "all", "approvals": 0},
}


def rollout_plan(tier: int, budget_remaining: float, change_kind: str = "binary") -> dict:
    """Deployment policy for one change.

    budget_remaining: share of the error budget left in the window (1.0 = untouched, <= 0 = spent).
    """
    if tier not in _BASE:
        raise ValueError("tier must be 1, 2 or 3")
    plan = {k: (list(v) if isinstance(v, list) else v) for k, v in _BASE[tier].items()}
    plan["tier"], plan["notes"] = tier, []
    if change_kind in ("config", "schema", "data"):
        # these have caused as many outages as binaries and are often rolled out less carefully
        plan["notes"].append(f"{change_kind} change: same staged rollout as a binary")
    if budget_remaining <= 0:
        if tier < 3:
            plan["allowed"] = "reliability-fixes-only"
            plan["notes"].append("error budget spent: feature rollouts paused by policy")
        else:
            plan["allowed"] = "all"
        plan["bake_minutes"] *= 2
    elif budget_remaining < 0.25:
        plan["allowed"] = "all"
        plan["bake_minutes"] *= 2
        if plan["stages"][0] > 1:
            plan["stages"].insert(0, 1)
        plan["notes"].append("budget below 25%: smaller first stage and longer bake")
    else:
        plan["allowed"] = "all"
        if tier == 2 and budget_remaining > 0.75:
            plan["bake_minutes"] = 10
            plan["notes"].append("plenty of budget: faster path")
    plan["minimum_minutes"] = plan["bake_minutes"] * len(plan["stages"])
    return plan


class Rejected(Exception):
    pass


def guard_drain(regions: dict, drain: list, peak_demand: float, break_glass: dict | None = None) -> dict:
    """Decide whether a drain may proceed.

    regions: {name: {"capacity": units, "drained": bool}}; drain: region names to take out now.
    Invariants: (1) never more than one region per operation; (2) what remains must still
    serve peak demand with one further region lost (N+1).
    """
    unknown = [r for r in drain if r not in regions]
    if unknown:
        raise Rejected(f"unknown region(s): {', '.join(unknown)}")
    violations = []
    if len(drain) > 1:
        violations.append(f"drains {len(drain)} regions in one operation; the limit is 1")
    left = {r: v["capacity"] for r, v in regions.items() if not v.get("drained") and r not in drain}
    after_one_more_loss = sum(left.values()) - (max(left.values()) if left else 0)
    if after_one_more_loss < peak_demand:
        violations.append(f"remaining capacity {sum(left.values())} cannot serve peak {peak_demand} after losing one more region")
    if not violations:
        return {"decision": "allow", "violations": [], "audit": None}
    if break_glass and all(break_glass.get(k) for k in ("who", "incident", "reason")):
        return {"decision": "allow-break-glass", "violations": violations,
                "audit": {"event": "BREAK_GLASS_DRAIN", **break_glass, "regions": drain, "alert": "page platform on-call", "review_required": True}}
    raise Rejected("; ".join(violations))


def platform_slo(events: list, target: float) -> dict:
    """SLO for a platform service such as CI or deploy.

    events: [{"ok": bool, "cause": "system"|"user"}]. A build that fails because the user's
    tests fail is the platform working. Only system-caused failures spend the budget.
    """
    counted = [e for e in events if e["ok"] or e["cause"] == "system"]
    bad = sum(1 for e in counted if not e["ok"])
    sli = 1 - bad / len(counted) if counted else 1.0
    budget = (1 - target) * len(counted)
    return {"sli": round(sli, 4), "target": target, "met": sli >= target, "excluded_user_failures": len(events) - len(counted),
            "budget_spent": round(bad / budget, 2) if budget else None}


if __name__ == "__main__":
    for slo in (0.99, 0.999, 0.9999, 0.99999):
        m = allowed_downtime_minutes(slo)
        print(f"{slo * 100:g}%: {m / 60:.2f} h/year" if m > 120 else f"{slo * 100:g}%: {m:.2f} min/year")
    for tier, budget in ((1, 0.9), (1, 0.1), (1, -0.2), (3, 0.9)):
        print(tier, budget, rollout_plan(tier, budget))
