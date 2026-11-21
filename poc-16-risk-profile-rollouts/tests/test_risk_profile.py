import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from risk_profile import Rejected, allowed_downtime_minutes, guard_drain, platform_slo, rollout_plan  # noqa: E402

REGIONS = {r: {"capacity": 100, "drained": False} for r in ("eu-west-1", "eu-central-1", "us-east-1", "us-west-2")}


def test_the_nines():
    assert round(allowed_downtime_minutes(0.99) / 60, 1) == 87.7      # the chapter rounds to 87.6 h with a 365-day year
    assert round(allowed_downtime_minutes(0.999) / 60, 2) == 8.77
    assert allowed_downtime_minutes(0.9999) == 52.6
    assert allowed_downtime_minutes(0.99999) == 5.26


def test_risk_profile_sets_the_rollout():
    critical = rollout_plan(1, 0.9)
    tool = rollout_plan(3, 0.9)
    assert critical["stages"] == [1, 10, 50, 100] and critical["canary_analysis"] == "required" and critical["regions_at_once"] == 1
    assert tool["stages"] == [100] and tool["minimum_minutes"] == 5
    assert critical["minimum_minutes"] > 40 * tool["minimum_minutes"]  # strict where it matters, fast where it doesn't


def test_low_budget_tightens_and_spent_budget_pauses_features():
    assert rollout_plan(2, 0.9)["bake_minutes"] == 10
    low = rollout_plan(2, 0.1)
    assert low["stages"][0] == 1 and low["bake_minutes"] == 40
    spent = rollout_plan(1, -0.2)
    assert spent["allowed"] == "reliability-fixes-only"
    assert rollout_plan(3, -0.2)["allowed"] == "all"  # an internal tool is not frozen


def test_config_changes_get_the_same_care():
    assert "same staged rollout" in rollout_plan(1, 0.9, "config")["notes"][0]


def test_drain_of_one_region_is_fine():
    assert guard_drain(REGIONS, ["eu-west-1"], peak_demand=180)["decision"] == "allow"


def test_multi_region_drain_is_rejected():
    with pytest.raises(Rejected, match="limit is 1"):
        guard_drain(REGIONS, ["eu-west-1", "eu-central-1"], peak_demand=100)


def test_drain_that_breaks_n_plus_one_is_rejected():
    regions = {**REGIONS, "us-west-2": {"capacity": 100, "drained": True}}  # one already out for maintenance
    with pytest.raises(Rejected, match="cannot serve peak"):
        guard_drain(regions, ["us-east-1"], peak_demand=150)


def test_break_glass_overrides_with_an_audit_record():
    bg = {"who": "oncall-sam", "incident": "INC-77", "reason": "evacuating two regions ahead of a storm"}
    out = guard_drain(REGIONS, ["us-east-1", "us-west-2"], peak_demand=100, break_glass=bg)
    assert out["decision"] == "allow-break-glass" and out["audit"]["review_required"]
    with pytest.raises(Rejected):
        guard_drain(REGIONS, ["us-east-1", "us-west-2"], peak_demand=100, break_glass={"who": "x"})


def test_platform_slo_ignores_user_caused_failures():
    events = [{"ok": True, "cause": "system"}] * 990 + [{"ok": False, "cause": "user"}] * 200 + [{"ok": False, "cause": "system"}] * 10
    out = platform_slo(events, target=0.995)
    assert out["sli"] == 0.99 and not out["met"] and out["excluded_user_failures"] == 200 and out["budget_spent"] == 2.0
