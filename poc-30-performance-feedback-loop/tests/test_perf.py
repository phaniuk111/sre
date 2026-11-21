import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import perf as P  # noqa: E402


def test_load_profiles_have_the_right_shape():
    assert P.profile("smoke")[0]["target"] <= 5
    spike = P.profile("spike", 50)
    assert spike[0]["target"] == 500 and spike[0]["duration"] == "1m"
    assert P.profile("soak")[1]["duration"] == "48h"
    assert P.profile("breakpoint")[0]["target"] > P.profile("stress")[0]["target"]


def test_thresholds_come_from_the_slo_and_gate_the_run():
    th = P.thresholds_from_slo(99.9, 300)
    assert th == {"http_req_failed": ["rate<0.001"], "http_req_duration": ["p(95)<300"]}
    ok = {"metrics": {"http_req_failed": {"value": 0.0004}, "http_req_duration": {"p(95)": 240.0, "avg": 120}}}
    bad = {"metrics": {"http_req_failed": {"value": 0.004}, "http_req_duration": {"p(95)": 410.0, "avg": 180}}}
    assert P.gate(ok, th) == (True, [])
    passed, failures = P.gate(bad, th)
    assert not passed and len(failures) == 2


def test_generated_k6_script_is_current():
    here = os.path.join(os.path.dirname(__file__), "..", "k6", "checkout-average.js")
    assert open(here).read() == P.k6_script("http://frontend-proxy:8080")


def test_deployment_verification_rolls_back_on_two_bad_readings():
    def healthy(expr, step):
        return 0.002 if "error" in expr else 3 if "login" in expr else 0
    assert P.verify_deployment(healthy, P.DEPLOY_CHECKS)["decision"] == "promote"

    def broken_logins(expr, step):
        if "login" in expr:
            return 0.0 if step >= 2 else 3
        return 0.002 if "error" in expr else 0
    r = P.verify_deployment(broken_logins, P.DEPLOY_CHECKS)
    assert r["decision"] == "rollback" and r["at_step"] == 3 and "login" in r["reason"]

    def one_blip(expr, step):
        return 0.05 if ("error" in expr and step == 1) else (3 if "login" in expr else 0)
    assert P.verify_deployment(one_blip, P.DEPLOY_CHECKS)["decision"] == "promote"


def test_web_vitals_are_scored_at_p75():
    assert P.rate_vital("LCP", [1.2, 1.9, 2.1, 2.3, 2.4])[1] == "good"
    assert P.rate_vital("LCP", [1.2, 3.1, 3.5, 3.9, 6.0])[1] == "needs improvement"
    assert P.rate_vital("CLS", [0.01, 0.3, 0.4, 0.5])[1] == "poor"
    assert P.rate_vital("INP", [0.05, 0.1, 0.15, 0.18])[1] == "good"


STACKS = """main;foo 10
main;bar;baz 70
main;bar;qux 15
main;bar 5"""


def test_top_table_self_versus_total():
    rows = {f: (s, t) for f, s, t in P.top_table(P.parse_collapsed(STACKS))}
    assert rows["baz"] == (70, 70)
    assert rows["bar"] == (5, 90)       # little time in bar itself, most in its children
    assert rows["main"] == (0, 100)


def test_flame_widths_are_shares_of_samples():
    f = P.flame(P.parse_collapsed(STACKS))
    assert f["main"] == 1.0 and f["main;bar"] == 0.9 and f["main;bar;baz"] == 0.7
