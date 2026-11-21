"""Platform as a product: a three-view scorecard and a deprecation brownout plan.

Developer-experience and platform-as-a-product chapters:
  user view      adoption, retention, time to first "hello world", first-attempt success
  system view    platform SLO attainment, cost of goods sold per active service
  business view  delivery metrics for teams on the platform against teams off it
A falling cost per service with rising adoption is healthy. Rising cost without
either is a red flag. "Total deployments" is a vanity metric and is not here.

Deprecation is a launch in reverse. A brownout breaks the old service briefly,
on purpose, to find callers nobody knew about.

AWS: adoption from template or tag usage; TTFHW from repository-created to first
successful production deploy (EventBridge pipeline events); cost from Cost and
Usage Reports with cost allocation tags; callers of an old API from CloudTrail
or access logs.
"""
from __future__ import annotations

import json
import statistics
import sys
from datetime import date, timedelta


def user_view(teams: list) -> dict:
    """teams: [{"name", "onboarded": bool, "active_last_30d": bool, "ttfhw_minutes", "first_try": bool, "nps": -100..100}]"""
    on = [t for t in teams if t["onboarded"]]
    active = [t for t in on if t["active_last_30d"]]
    return {
        "adoption": round(len(on) / len(teams), 2),
        "retention": round(len(active) / len(on), 2) if on else None,      # tried it once and left?
        "median_ttfhw_minutes": statistics.median(t["ttfhw_minutes"] for t in on) if on else None,
        "first_attempt_success": round(sum(t["first_try"] for t in on) / len(on), 2) if on else None,
        "recommend_score": round(statistics.mean(t["nps"] for t in on)) if on else None,
    }


def system_view(platform: dict) -> dict:
    """platform: {"slo_target", "slo_actual", "monthly_cost", "active_services", "prev_monthly_cost", "prev_active_services"}"""
    cogs = platform["monthly_cost"] / platform["active_services"]
    prev = platform["prev_monthly_cost"] / platform["prev_active_services"]
    return {"slo_met": platform["slo_actual"] >= platform["slo_target"], "cost_per_active_service": round(cogs, 2),
            "cost_per_service_change": round(cogs / prev - 1, 3),
            "flag": "cost per service rising without more adoption" if cogs > prev * 1.05 and platform["active_services"] <= platform["prev_active_services"] else None}


def delivery_metrics(deploys: list) -> dict:
    """deploys: [{"lead_time_hours", "failed": bool, "recovery_minutes" (if failed), "rework": bool}] over 30 days.

    The five DORA software-delivery metrics: lead time, deployment frequency, change failure
    rate, failed-deployment recovery time, rework rate.
    """
    failed = [d for d in deploys if d["failed"]]
    return {
        "deploys_per_week": round(len(deploys) / (30 / 7), 1),
        "median_lead_time_hours": statistics.median(d["lead_time_hours"] for d in deploys),
        "change_failure_rate": round(len(failed) / len(deploys), 3),
        "median_recovery_minutes": statistics.median(d["recovery_minutes"] for d in failed) if failed else 0,
        "rework_rate": round(sum(d.get("rework", False) for d in deploys) / len(deploys), 3),
    }


def business_view(on_platform: list, off_platform: list) -> dict:
    a, b = delivery_metrics(on_platform), delivery_metrics(off_platform)
    return {"on_platform": a, "off_platform": b,
            "lead_time_ratio": round(b["median_lead_time_hours"] / a["median_lead_time_hours"], 1),
            "frequency_ratio": round(a["deploys_per_week"] / b["deploys_per_week"], 1)}


def scorecard(data: dict) -> dict:
    user = user_view(data["teams"])
    out = {"user": user, "system": system_view(data["platform"]), "business": business_view(data["deploys_on"], data["deploys_off"])}
    # read the views in order: if developers do not use it, the other two do not matter yet
    out["headline"] = ("fix adoption first" if user["adoption"] < 0.3 or (user["retention"] or 0) < 0.6
                       else "fix the first-run experience" if user["first_attempt_success"] < 0.7
                       else "healthy: report business impact")
    return out


def brownout_plan(callers: dict, today: date, off_date: date) -> dict:
    """callers: {team: last_seen_iso_date} from access logs of the service being retired.

    Escalating brownouts before the final switch-off, and who to contact first.
    """
    recent = sorted(t for t, seen in callers.items() if (today - date.fromisoformat(seen)).days <= 30)
    stale = sorted(set(callers) - set(recent))
    days = (off_date - today).days
    steps = [(round(days * f), dur) for f, dur in ((0.4, "5 minutes"), (0.6, "1 hour"), (0.8, "8 hours"), (0.9, "24 hours"))]
    return {"contact_now": recent, "probably_gone": stale,
            "brownouts": [{"date": (today + timedelta(days=d)).isoformat(), "duration": dur, "response": "410 with a link to the replacement"} for d, dur in steps],
            "off": off_date.isoformat()}


if __name__ == "__main__":
    json.dump(scorecard(json.load(open(sys.argv[1]))), sys.stdout, indent=2)
    print()
