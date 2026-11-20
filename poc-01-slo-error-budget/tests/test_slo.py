import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from slo import (  # noqa: E402
    BadMinuteSLO,
    ErrorBudget,
    burn_rate,
    google_default_policy,
    k_of_n_availability,
    min_failures_to_alert,
    parallel_availability,
    serial_availability,
    time_to_exhaustion_hours,
    wilson_interval,
    workbook_policy,
)
from slo.bad_minutes import cuj_bad_minutes  # noqa: E402
from slo.budget import budget_consumed_fraction, burn_rate_for_consumption  # noqa: E402


def test_error_budget_minutes():
    assert ErrorBudget(0.999, 30).allowed_downtime_minutes == pytest.approx(43.2)
    # four nines ~ 4m19s per 30d (book quotes ~4m23s for a calendar month)
    assert ErrorBudget(0.9999, 30).allowed_downtime_minutes == pytest.approx(4.32)


def test_slo_must_not_be_100():
    with pytest.raises(ValueError):
        ErrorBudget(1.0)


def test_burn_rate_and_consumption():
    assert burn_rate(0.0144, 0.999) == pytest.approx(14.4)
    assert budget_consumed_fraction(14.4, 1) == pytest.approx(0.02)
    assert burn_rate_for_consumption(0.10, 72) == pytest.approx(1.0)
    assert time_to_exhaustion_hours(14.4) == pytest.approx(50.0)


def test_remaining_budget():
    b = ErrorBudget(0.99)
    assert b.remaining_fraction(good=995, total=1000) == pytest.approx(0.5)
    assert b.remaining_fraction(good=980, total=1000) == pytest.approx(-1.0)


def test_fast_burn_pages_and_recovers():
    policy = google_default_policy(0.999)
    # Outage: 2% errors right now and over the last hour -> page
    assert "fast-burn-2pct-1h" in policy.evaluate(lambda h: 0.02)["page"]
    # Recovered: last hour still bad, but last 5 minutes are clean -> no page
    recovered = policy.evaluate(lambda h: 0.02 if h >= 1 else 0.0)
    assert recovered["page"] == []


def test_slow_burn_tickets():
    policy = google_default_policy(0.999)
    res = policy.evaluate(lambda h: 0.0012)  # burn rate 1.2 everywhere
    assert res["page"] == [] and res["ticket"] == ["slow-burn-10pct-3d"]


def test_workbook_policy_thresholds():
    p = workbook_policy(0.999)
    rates = [round(w.burn_rate_threshold, 2) for w in p.windows]
    assert rates == [14.4, 6.0, 3.0, 1.0]


@pytest.mark.parametrize("n,expected", [(1000, 173), (200, 42), (100, 24)])
def test_book_wilson_examples(n, expected):
    # 99% SLO, detect burn rate 14.4 -> 14.4% error rate, 99% confidence
    assert min_failures_to_alert(n, 0.144) == expected


def test_wilson_bounds_are_sane():
    lo, hi = wilson_interval(1, 20)
    assert 0 <= lo < 0.05 < hi <= 1


def test_composition_matches_appendix_e():
    assert serial_availability([0.8, 0.9]) == pytest.approx(0.72)
    assert parallel_availability([0.8, 0.9]) == pytest.approx(0.98)
    # 2-of-3 quorum with 99% AZs
    assert k_of_n_availability([0.99] * 3, 2) == pytest.approx(0.999702, rel=1e-5)


def test_bad_minute_model():
    slo = BadMinuteSLO(bad_minute_error_threshold=0.06, slo=0.999)
    minutes = [(5, 100)] * 98 + [(30, 100)] * 2  # 5% noise floor, 2 bad minutes
    assert slo.compliance(minutes) == pytest.approx(0.98)
    assert math.floor(slo.allowed_bad_minutes(30 * 24 * 60)) == 43


def test_cuj_aggregation():
    flags = cuj_bad_minutes({"search": [False, True, False], "route": [False, False, True]})
    assert flags == [False, True, True]
