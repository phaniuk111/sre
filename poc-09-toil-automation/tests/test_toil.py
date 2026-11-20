import os
import sys

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, ".."))

from toil_report import analyse, load, prioritise  # noqa: E402


def test_report_and_priorities():
    rows = load(os.path.join(HERE, "..", "examples", "tickets.csv"))
    r = analyse(rows, team_size=6, weeks=4)
    assert 0 < r["ops_load_pct"] < 100
    assert r["unactionable_pct"] > 30  # the flappy alert dominates by count
    p = prioritise(rows, {"disk-full": 16, "cert-renewal": 8, "restart-stuck-worker": 40, "quota-increase": 4}, 4)
    assert p["snowball_fastest_first"][0] == "quota-increase"
