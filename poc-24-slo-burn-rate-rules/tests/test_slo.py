import os
import sys

import yaml

HERE = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, HERE)
import generate as G  # noqa: E402

SPEC = yaml.safe_load(open(os.path.join(HERE, "slo.yml")))


def test_budget_numbers():
    assert round(G.downtime_minutes(99.9), 1) == 43.2
    assert round(G.downtime_minutes(99.99), 2) == 4.32
    assert 14.4 * 60 / 43200 == 0.02  # 14.4x for one hour spends 2% of a 30-day budget
    assert 6 * 360 / 43200 == 0.05
    assert 3 * 1440 / 43200 == 0.10


def test_generated_rules_have_every_window_and_compare_error_ratios():
    out = G.generate(SPEC)
    recs = [r for g in out["groups"] for r in g["rules"] if "record" in r]
    names = {r["record"] for r in recs}
    for w in G.WINDOWS + ["30d"]:
        assert "slo:sli_error:ratio_rate" + w in names
    alerts = [r for g in out["groups"] for r in g["rules"] if "alert" in r]
    assert len(alerts) == 4  # page + ticket for each SLO
    page = alerts[0]["expr"]
    assert "slo:sli_error:ratio_rate5m" in page and "(14.4 * 0.001)" in page and "(6.0 * 0.001)" in page
    assert "success" not in page


def test_committed_output_is_current():
    committed = yaml.safe_load(open(os.path.join(HERE, "generated", "slo-rules.yml")))
    assert committed == G.generate(SPEC)


def _traffic(minutes, rpm=1000):
    return [0.0] * minutes, [float(rpm)] * minutes


def test_full_outage_pages_within_minutes_and_resets_soon_after():
    err, tot = _traffic(600)
    for i in range(300, 330):  # 30-minute total outage
        err[i] = tot[i]
    fired = G.simulate(err, tot, 99.9, G.PAGE)
    first = fired.index(True)
    assert first - 300 <= 2  # 1h ratio passes 1.44% within a minute of a full outage
    last = len(fired) - 1 - fired[::-1].index(True)
    assert last - 329 <= 30  # short windows let it resolve within 30 minutes, not after the 1h or 6h windows drain
    fast_only = G.simulate(err, tot, 99.9, G.PAGE[:1])
    assert len(fast_only) - 1 - fast_only[::-1].index(True) - 329 <= 5  # the 5m window clears in minutes


def test_slow_burn_doesnt_page_but_tickets():
    err, tot = _traffic(4 * 1440)
    for i in range(len(tot)):
        err[i] = tot[i] * 0.004  # 4x burn: budget gone in 7.5 days
    assert not any(G.simulate(err, tot, 99.9, G.PAGE))
    assert any(G.simulate(err, tot, 99.9, G.TICKET))


def test_a_brief_blip_pages_nobody():
    err, tot = _traffic(240)
    for i in range(100, 103):
        err[i] = tot[i] * 0.1  # three minutes at 10% errors
    assert not any(G.simulate(err, tot, 99.9, G.PAGE))


def test_budget_consumed_when_the_fast_page_fires():
    err, tot = _traffic(240)
    for i in range(60, 240):
        err[i] = tot[i] * 0.0144  # exactly 14.4x
    err[60:] = [e * 1.01 for e in err[60:]]
    fired = G.simulate(err, tot, 99.9, G.PAGE[:1])  # the 1h / 14.4x pair on its own
    at = fired.index(True)
    used = G.budget_consumed(err[: at + 1], tot[: at + 1], 99.9, steady_rps_minute=1000)
    assert 0.019 < used < 0.022  # about 2% of the 30-day budget, as the table promises


def test_window_based_recovers_in_hours_request_based_in_weeks():
    days, hours = G.recovery(good_rpm=20, bad_rps=500)
    assert 15 < days < 16.5 and hours == 3.75  # the book's "almost 16 days" vs 15 windows


def test_window_based_rule_uses_bool_and_a_subquery():
    r = G.window_based_rule("prometheus", "availability", "slo:sli_success:ratio5m", 0.999)
    assert ">= bool 0.999" in r["expr"] and "[30d:5m]" in r["expr"]
