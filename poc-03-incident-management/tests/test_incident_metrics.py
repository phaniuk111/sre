import json
import os
import sys

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, ".."))

from incident_metrics import Incident, summarise  # noqa: E402


def load():
    with open(os.path.join(HERE, "..", "examples", "incidents.json")) as f:
        return [Incident.from_dict(d) for d in json.load(f)]


def test_durations():
    inc = load()[0]
    assert (inc.ttd, inc.ttm, inc.ttr) == (4, 15, 146)


def test_summary_flags_coordination_cost():
    s = summarise(load())
    assert s["median_ttm_min"] == 15
    assert s["pct_manually_detected"] == 33.3
    assert s["pct_without_ic"] == 33.3  # INC-102 had 5 people and no IC
    assert s["pages_per_incident"] == 4.0
