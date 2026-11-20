import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from capacity import (  # noqa: E402
    forecast_with_uncertainty, peak_of_sums, plan_supply, redundancy_overhead,
    stranded_capacity, sum_of_peaks,
)


def test_forecast_includes_inorganic_and_band():
    history = [1000 + 50 * w + (30 if w % 4 == 0 else -10) for w in range(30)]
    fc = forecast_with_uncertainty(history, horizon=8, inorganic={7: 2000})
    median, upper = fc[0]
    assert 2400 < median < 2700 and upper >= median
    assert fc[7][0] - fc[6][0] > 1900  # Black Friday bump


def test_n_plus_one_survives_az_loss():
    plan = plan_supply(peak_demand_qps=9000, qps_per_instance=100, failure_domains=3, target_utilisation=0.7)
    # lose one AZ: remaining 2 domains must still carry the peak below 100%
    remaining = plan.per_domain * (plan.domains - 1) * 100
    assert remaining >= 9000 / 0.7
    assert plan.utilisation_at_peak < 0.7


def test_more_domains_cheaper_redundancy():
    assert redundancy_overhead(3) == pytest.approx(0.5)
    assert redundancy_overhead(6) == pytest.approx(0.2)


def test_pooling_saves_capacity():
    # Three services peaking at different times of day
    eu = [10, 80, 30, 10]
    us = [10, 20, 80, 30]
    ap = [80, 30, 10, 10]
    s = {"eu": eu, "us": us, "ap": ap}
    assert sum_of_peaks(s) == 240
    assert peak_of_sums(s) == 130


def test_stranded_capacity():
    assert stranded_capacity(100, [90, 40, 30, 80]) == 40
