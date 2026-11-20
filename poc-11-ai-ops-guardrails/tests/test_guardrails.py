import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agent_guardrails import (  # noqa: E402
    Guardrails, IrreversibleDelete, Level, Proposal, RollbackLambdaAlias, TrackRecord, ZonalShift, earned_level,
)

EVIDENCE = ["5xx up 30x since deploy 42", "only version 7 errors"]


def test_levels_are_earned_and_capped():
    assert earned_level(TrackRecord(), Level.L4_FULL) == Level.L1_ASSISTED
    assert earned_level(TrackRecord(19, 1), Level.L4_FULL) == Level.L2_PARTIAL
    assert earned_level(TrackRecord(995, 5), Level.L4_FULL) == Level.L3_HIGH
    assert earned_level(TrackRecord(995, 5), Level.L2_PARTIAL) == Level.L2_PARTIAL  # policy ceiling wins


def test_new_scenario_is_suggest_only():
    g = Guardrails()
    p = Proposal("bad-deploy", RollbackLambdaAlias("checkout", "live", "6", "7"), "rollback", EVIDENCE, 0.9)
    assert g.execute(p, validate=lambda: True).startswith("suggest-only")


def test_l2_needs_human_approval():
    g = Guardrails(records={"bad-deploy": TrackRecord(30, 1)})
    action = RollbackLambdaAlias("checkout", "live", "6", "7")
    p = Proposal("bad-deploy", action, "rollback", EVIDENCE, 0.9)
    assert "awaiting" in g.execute(p, validate=lambda: True)
    assert "approved by human" in g.execute(p, validate=lambda: True, human_approves=lambda *_: True)
    assert action.active_version == "6"


def test_l3_auto_acts_and_rolls_back_on_failed_validation():
    g = Guardrails(records={"az-impairment": TrackRecord(500, 0)})
    shift = ZonalShift("arn:aws:elasticloadbalancing:...:loadbalancer/app/x/1", "euw2-az1")
    out = g.execute(Proposal("az-impairment", shift, "AZ errors only", EVIDENCE, 0.95), validate=lambda: False)
    assert "auto-approved" in out and "rolled back" in out and shift.applied is False


def test_refuses_irreversible_and_kill_switch():
    g = Guardrails(records={"x": TrackRecord(5000, 0)}, ceilings={"x": Level.L4_FULL})
    assert "not reversible" in g.execute(Proposal("x", IrreversibleDelete(), "free space", EVIDENCE, 0.99), lambda: True)
    g.kill_switch = True
    assert "kill switch" in g.execute(Proposal("x", ZonalShift("a", "b"), "r", EVIDENCE, 0.99), lambda: True)
    assert len(g.audit) == 2
