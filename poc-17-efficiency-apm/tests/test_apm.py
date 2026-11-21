import json
import os
import sys

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, ".."))

from apm import classify, default_on_decision, suspicious_work_metrics, wasted_work  # noqa: E402

DATA = json.load(open(os.path.join(HERE, "..", "examples", "fleet.json")))


def verdict(name):
    c = DATA["changes"][name]
    return classify(c["before"], c["after"])


def test_same_cpu_increase_two_different_stories():
    busier, slower = verdict("video-transcode"), verdict("search-frontend")
    assert busier["cpu_change"] == slower["cpu_change"] == 0.2      # the bill looks identical
    assert busier["verdict"] == "growth" and busier["productivity_change"] == 0.0
    assert slower["verdict"] == "regression" and slower["productivity_change"] == -0.167


def test_optimisation_and_steady():
    assert verdict("checkout")["verdict"] == "optimisation"
    assert verdict("reports")["verdict"] == "steady"


def test_work_metric_that_does_not_track_usage_is_flagged():
    flagged = suspicious_work_metrics(DATA["series"])
    assert [f["service"] for f in flagged] == ["nightly-batch"]  # it counts batches, not items


def test_on_by_default_absorbs_small_regressions_and_opts_out_large_ones():
    d = default_on_decision(DATA["optimisation"])
    assert d["ship_on_by_default"] and d["net_fleet_cpu_change"] < -0.015
    assert d["absorbed"] == ["checkout"] and d["opt_out"] == ["ledger"]
    assert "ledger" in d["follow_up"][0]


def test_do_not_ship_when_it_hurts_too_much_of_the_fleet():
    effects = [{"service": "a", "fleet_share": 0.5, "cpu_change": 0.05}, {"service": "b", "fleet_share": 0.5, "cpu_change": -0.06}]
    assert not default_on_decision(effects)["ship_on_by_default"]


def test_wasted_work():
    reqs = [{"cpu_seconds": 6, "finished_ms": 80, "deadline_ms": 100, "kind": "user"},
            {"cpu_seconds": 3, "finished_ms": 400, "deadline_ms": 100, "kind": "user"},   # caller already gave up
            {"cpu_seconds": 1, "finished_ms": 20, "deadline_ms": 100, "kind": "probe"}]
    assert wasted_work(reqs) == {"past_deadline_share": 0.3, "non_user_share": 0.1}
