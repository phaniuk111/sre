import json
import os
import sys
from datetime import date

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, ".."))

from scorecard import brownout_plan, scorecard, system_view  # noqa: E402

DATA = json.load(open(os.path.join(HERE, "..", "examples", "platform.json")))


def test_user_view():
    u = scorecard(DATA)["user"]
    assert u["adoption"] == 0.6 and u["retention"] == 0.83
    assert u["median_ttfhw_minutes"] == 52.5 and u["first_attempt_success"] == 0.67


def test_system_view_cost_per_service():
    s = scorecard(DATA)["system"]
    assert s["slo_met"] and s["cost_per_active_service"] == 300.0 and s["cost_per_service_change"] == -0.1 and s["flag"] is None
    bad = system_view({**DATA["platform"], "monthly_cost": 48000, "active_services": 118})
    assert bad["flag"] == "cost per service rising without more adoption"


def test_business_view_compares_adopters_with_non_adopters():
    b = scorecard(DATA)["business"]
    assert b["on_platform"]["median_lead_time_hours"] == 5 and b["off_platform"]["median_lead_time_hours"] == 72
    assert b["lead_time_ratio"] == 14.4 and b["frequency_ratio"] == 4.0
    assert b["on_platform"]["change_failure_rate"] < b["off_platform"]["change_failure_rate"]
    assert b["on_platform"]["median_recovery_minutes"] == 12


def test_headline_reads_the_views_in_order():
    assert scorecard(DATA)["headline"] == "fix the first-run experience"
    few = {**DATA, "teams": [{**t, "onboarded": t["onboarded"] and i < 4} for i, t in enumerate(DATA["teams"])]}
    assert scorecard(few)["headline"] == "fix adoption first"


def test_brownout_plan():
    callers = {"billing": "2026-11-18", "reports": "2026-11-02", "old-cron": "2026-06-30"}
    plan = brownout_plan(callers, today=date(2026, 11, 21), off_date=date(2027, 3, 1))
    assert plan["contact_now"] == ["billing", "reports"] and plan["probably_gone"] == ["old-cron"]
    assert [b["duration"] for b in plan["brownouts"]] == ["5 minutes", "1 hour", "8 hours", "24 hours"]
    assert plan["brownouts"][0]["date"] == "2026-12-31" and plan["off"] == "2027-03-01"
