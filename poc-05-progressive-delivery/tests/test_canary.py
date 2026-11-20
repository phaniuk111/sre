import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from canary_analysis import ArmStats, judge  # noqa: E402

rng = random.Random(3)


def arm(n, err, p50, slow=1.0):
    return ArmStats(n, sum(rng.random() < err for _ in range(n)),
                    [rng.lognormvariate(0, 0.4) * p50 * slow for _ in range(n)])


def test_healthy_canary_passes():
    assert judge(arm(5000, 0.001, 50), arm(50000, 0.001, 50)) == "PASS"


def test_error_regression_fails():
    assert judge(arm(5000, 0.02, 50), arm(50000, 0.001, 50)).startswith("FAIL: error rate")


def test_latency_regression_fails():
    assert "latency regression" in judge(arm(5000, 0.001, 50, slow=1.5), arm(50000, 0.001, 50))


def test_silent_canary_is_inconclusive():
    assert judge(arm(20, 0.0, 50), arm(50000, 0.001, 50)) == "INCONCLUSIVE"
