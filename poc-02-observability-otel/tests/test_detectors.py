import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from detectors.cohort_latency import build_baselines, coverage, is_regression, outlier_fraction  # noqa: E402
from detectors.failure_concentration import rank_cohorts  # noqa: E402

random.seed(7)


def synth(method: str, p50: float, n: int, slowdown: float = 1.0):
    return [(method, random.lognormvariate(0, 0.3) * p50 * slowdown) for _ in range(n)]


def test_cohort_regression_detected_only_when_slower():
    history = synth("Login", 80, 5000) + synth("Report", 6000, 5000)
    baselines = build_baselines(history, min_samples=1000)
    assert set(baselines) == {"Login", "Report"}
    assert coverage(history, baselines) == 1.0

    healthy = synth("Login", 80, 2000) + synth("Report", 6000, 2000)
    f_ok = outlier_fraction(healthy, baselines)
    assert 0.0 < f_ok < 0.06 and not is_regression(f_ok)

    # Login gets 1.8x slower: a 144ms login is still "fast" in absolute terms,
    # but it's way outside its own cohort's normal.
    regressed = synth("Login", 80, 2000, slowdown=1.8) + synth("Report", 6000, 2000)
    f_bad = outlier_fraction(regressed, baselines)
    assert is_regression(f_bad)


def test_small_cohorts_are_not_meaningful():
    history = synth("Rare", 50, 10)
    assert build_baselines(history, min_samples=1000) == {}


def test_failure_concentration_finds_hidden_cohort():
    events = []
    for _ in range(5000):
        labels = {
            "browser": random.choice(["chrome", "safari", "firefox"]),
            "user_type": random.choice(["consumer", "enterprise"]),
            "region": random.choice(["eu-west-2", "us-east-1"]),
        }
        p_fail = 0.95 if (labels["browser"] == "firefox" and labels["user_type"] == "enterprise") else 0.001
        events.append((labels, random.random() < p_fail))
    top_name, _gain, rate, _size = rank_cohorts(events)[0]
    assert set(top_name.split(" & ")) == {"browser=firefox", "user_type=enterprise"}
    assert rate > 0.9
