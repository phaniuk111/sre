import json
import os
import sys

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, ".."))

from coupling_discovery import analyse, fail_open  # noqa: E402

DATA = json.load(open(os.path.join(HERE, "..", "examples", "evidence.json")))


def test_shared_database_ranks_multi_writer_highest():
    rep = analyse(DATA)["shared_database"]
    by = {r["table"]: r for r in rep}
    assert by["orders"]["severity"] == "high" and by["orders"]["writers"] == ["orders", "shipping"]
    assert by["payments"]["severity"] == "medium"
    assert "prices" not in by  # one owner: fine


def test_unregistered_topic_is_implicit_coupling():
    topics = [r["topic"] for r in analyse(DATA)["implicit_queue_coupling"]]
    assert topics == ["order-events"]  # payment-events has a registered schema


def test_distributed_monolith_and_release_rate():
    rep = analyse(DATA)
    assert rep["distributed_monolith"] == [{"services": ["orders", "shipping"], "together": 5, "of": 5, "ratio": 1.0}]
    assert rep["independent_release_rate"] == 0.38


def test_megamorphic_config():
    rep = analyse(DATA)["megamorphic_artifacts"]
    assert [r["artifact"] for r in rep] == ["platform-settings.yaml"]
    assert rep[0]["consumers"] == 7 and rep[0]["largest_share_read"] <= 0.5


def test_cycle_and_hidden_physical_dependency():
    rep = analyse(DATA)
    assert rep["call_cycles"] == [["orders", "pricing", "orders"]]
    assert rep["hidden_physical_dependencies"] == [{"domain": "eu-west-1a", "unexpected": ["ledger"]}]


def test_fail_open_returns_default():
    def boom():
        raise TimeoutError

    assert fail_open(boom, []) == []
    assert fail_open(lambda: ["a"], []) == ["a"]
