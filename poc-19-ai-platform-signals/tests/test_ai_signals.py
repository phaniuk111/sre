import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ai_signals import confidence_gate, drift_status, freshness, model_slo, promotion_gate, psi  # noqa: E402

EDGES = [50, 100, 250, 500]  # transaction value buckets
TRAIN = [20] * 20 + [80] * 30 + [180] * 30 + [400] * 20          # the model learned on $10-$500
POLICY = {"min_eval_score": 0.9, "max_regression": 0.01}


def test_similar_traffic_is_stable():
    live = [25] * 22 + [75] * 28 + [200] * 31 + [450] * 19
    assert drift_status(psi(TRAIN, live, EDGES)) == "stable"


def test_a_wave_of_large_transactions_is_drift():
    live = [80] * 20 + [180] * 20 + [400] * 10 + [5000] * 50      # the chapter's $5,000 example
    score = psi(TRAIN, live, EDGES)
    assert score > 0.25 and drift_status(score) == "drifted"


def test_freshness_objective():
    now = datetime(2026, 11, 21)
    assert freshness(datetime(2026, 11, 10), now, timedelta(days=14))["fresh"]
    stale = freshness(datetime(2026, 9, 1), now, timedelta(days=14))
    assert not stale["fresh"] and stale["age_days"] == 81


def test_confidence_gate_trades_availability_for_correctness():
    preds = ([{"confidence": 0.95, "correct": True}] * 80 + [{"confidence": 0.9, "correct": False}] * 2
             + [{"confidence": 0.5, "correct": True}] * 8 + [{"confidence": 0.4, "correct": False}] * 10)
    out = confidence_gate(preds, threshold=0.7)
    assert out == {"answered_share": 0.82, "error_rate_ungated": 0.12, "error_rate_gated": 0.024, "wrong_answers_avoided": 10}


def test_silent_failure_pages_even_though_the_api_is_up():
    ok = {"available": True, "latency_ok": True, "fresh": True, "drift": "stable", "quality_ok": True}
    assert model_slo(ok) == {"state": "healthy", "page": False}
    assert model_slo({**ok, "drift": "drifted"}) == {"state": "silent failure", "page": True}
    assert model_slo({**ok, "fresh": False})["state"] == "silent failure"
    assert model_slo({**ok, "available": False})["state"] == "outage"


def test_promotion_gate():
    good = {"signed": True, "lineage": {"code": "abc", "data": "s3://…/v7", "hyperparameters": "h3"}, "eval_score": 0.93,
            "baseline_score": 0.92, "safety_checks_passed": True, "canary": {"quality_delta": 0.004}}
    assert promotion_gate(good, POLICY) == {"promote": True, "reasons": []}
    bad = promotion_gate({**good, "signed": False, "canary": {"quality_delta": -0.05}}, POLICY)
    assert not bad["promote"] and len(bad["reasons"]) == 2
    assert "lineage" in promotion_gate({**good, "lineage": None}, POLICY)["reasons"][0]
