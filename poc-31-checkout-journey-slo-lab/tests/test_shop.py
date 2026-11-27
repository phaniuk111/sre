"""Runs the whole shop in-process on free ports and checks each lab exercise's mechanism."""
import json
import os
import shutil
import socket
import subprocess
import sys
import threading
import urllib.error
import urllib.request

import pytest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import shop  # noqa: E402


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class Shop:
    def __init__(self):
        self.ports = {r: free_port() for r in shop.ROLES}
        self.urls = {r: f"http://127.0.0.1:{p}" for r, p in self.ports.items()}
        self.roles, self.servers = {}, {}
        for r in shop.ROLES:
            self.start(r)

    def start(self, r):
        role = shop.make_role(r, self.urls)
        srv = role.serve(self.ports[r], host="127.0.0.1")
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        self.roles[r], self.servers[r] = role, srv

    def stop(self, r):
        self.servers[r].shutdown()
        self.servers[r].server_close()

    def post(self, role, path, payload):
        req = urllib.request.Request(self.urls[role] + path, data=json.dumps(payload).encode(), method="POST",
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e:
            return e.code, {}

    def order(self, card="4000000000000077"):
        return self.post("edge", "/checkout", {"items": ["sku-1"], "card": card})

    def metric(self, role, name, **labels):
        reg = self.roles[role].registry
        return reg.get_sample_value(name, labels) or 0.0


@pytest.fixture()
def s():
    shop_ = Shop()
    yield shop_
    for r in list(shop_.servers):
        try:
            shop_.stop(r)
        except Exception:
            pass


def test_happy_path_confirms_and_declines(s):
    status, body = s.order()
    assert status == 200 and body["status"] == "confirmed"
    status, body = s.order(card="4000000000000002")
    assert status == 200 and body["status"] == "declined"          # a correct answer: a good event
    status, _ = s.post("edge", "/checkout", {"items": []})
    assert status == 400                                            # malformed: left out of valid events
    assert s.metric("edge", "edge_request_duration_seconds_count", route="POST /checkout", code="200") == 2
    assert s.metric("edge", "edge_request_duration_seconds_bucket", route="POST /checkout", code="200", le="2.0") == 2


def test_exercise_2_dead_checkout_is_only_visible_at_the_edge(s):
    s.order()
    s.stop("checkout")
    codes = [s.order()[0] for _ in range(5)]
    assert codes == [502] * 5
    assert s.metric("edge", "edge_request_duration_seconds_count", route="POST /checkout", code="502") == 5
    # checkout counted only the one request it actually handled
    assert s.metric("checkout", "checkout_requests_total", code="200") == 1
    assert s.metric("checkout", "checkout_requests_total", code="503") == 0


def test_exercise_3_payment_failure_is_recorded_by_checkout_and_edge(s):
    s.post("payment", "/chaos", {"error_rate": 1.0})
    assert s.order()[0] == 503
    assert s.metric("checkout", "checkout_requests_total", code="503") == 1
    assert s.metric("checkout", "checkout_dependency_attempts_total", dep="payment", outcome="error") == 1


def test_exercise_4_retries_rescue_random_failures(s):
    s.post("payment", "/chaos", {"error_rate": 0.5, "mode": "random"})
    without = sum(s.order()[0] == 200 for _ in range(200))
    s.post("checkout", "/config", {"retries": {"payment": 1}})
    with_retry = sum(s.order()[0] == 200 for _ in range(200))
    # expected about 100/200 without and 150/200 with one retry (1 - 0.5 x 0.5)
    assert 70 <= without <= 130
    assert 125 <= with_retry <= 175
    assert with_retry > without + 20


def test_exercise_5_retries_do_not_rescue_an_outage():
    c = shop.Chaos()
    c.update({"error_rate": 0.2, "mode": "outage", "period_s": 100})
    # down for the first 20 s of every 100 s: an attempt and its retry 50 ms later fail together
    assert c.fails(now=1005.0) and c.fails(now=1005.05)
    assert not c.fails(now=1050.0)
    share = sum(c.fails(now=float(t)) for t in range(1000)) / 1000
    assert share == pytest.approx(0.2, abs=0.01)


def test_exercise_6_recommendations_hard_vs_soft(s):
    s.post("recommendations", "/chaos", {"error_rate": 1.0})
    assert s.order()[0] == 200                                       # soft: page shown without the panel
    s.post("checkout", "/config", {"recommendations": "hard"})
    assert s.order()[0] == 503                                       # hard: every order now fails with it


def test_exercise_7_slow_dependency_makes_slow_successes(s):
    s.post("payment", "/chaos", {"latency_ms": 2200})
    s.roles["checkout"].timeout_s = 5
    status, _ = s.order()
    assert status == 200
    # confirmed, but outside the 2-second bucket: a bad event for the SLI
    assert s.metric("edge", "edge_request_duration_seconds_bucket", route="POST /checkout", code="200", le="2.0") == 0
    assert s.metric("edge", "edge_request_duration_seconds_count", route="POST /checkout", code="200") == 1


def test_slow_tail_delays_only_its_share():
    c = shop.Chaos()
    c.update({"slow_rate": 0.02, "slow_ms": 1500})
    assert c.delay_s(rnd=lambda: 0.01) == pytest.approx(1.5)
    assert c.delay_s(rnd=lambda: 0.5) == 0.0


def test_chaos_rejects_bad_settings():
    c = shop.Chaos()
    with pytest.raises(ValueError):
        c.update({"error_rate": 2})
    with pytest.raises(ValueError):
        c.update({"mode": "sometimes"})
    with pytest.raises(ValueError):
        c.update({"colour": "red"})
    assert c.update({"error_rate": 0.1, "reset": True})["error_rate"] == 0.0


def _promtool():
    for p in [os.environ.get("PROMTOOL"), os.path.join(HERE, "bin", "promtool"), shutil.which("promtool")]:
        if p and os.path.exists(p):
            return p
    return None


@pytest.mark.skipif(_promtool() is None, reason="promtool not found (make prometheus downloads it)")
def test_rules_pass_promtool_unit_tests():
    rules = os.path.join(HERE, "rules")
    for args in (["check", "rules", "checkout-slo.yml"], ["test", "rules", "checkout-slo.test.yml"]):
        out = subprocess.run([_promtool(), *args], cwd=rules, capture_output=True, text=True)
        assert out.returncode == 0, out.stdout + out.stderr


@pytest.mark.skipif(_promtool() is None, reason="promtool not found")
def test_solutions_parse():
    sol = os.path.join(HERE, "solutions")
    for f in sorted(os.listdir(sol)):
        if f.endswith(".yml"):
            out = subprocess.run([_promtool(), "check", "rules", f], cwd=sol, capture_output=True, text=True)
            assert out.returncode == 0, f + out.stdout + out.stderr


# ------------------------------------------------------------------ synthetic probe (exercise 12)
import probe as probe_mod  # noqa: E402


def test_probe_walks_the_journey_and_fails_when_a_hard_dependency_is_down(s):
    r = probe_mod.run_once(s.urls["edge"])
    assert r["ok"] and [ok for _, ok, _ in r["steps"]] == [True, True]
    s.post("payment", "/chaos", {"error_rate": 1.0})
    r = probe_mod.run_once(s.urls["edge"])
    assert not r["ok"] and "503" in r["steps"][0][2]


def test_probe_orders_stay_out_of_the_customer_sli(s):
    for _ in range(3):
        probe_mod.run_once(s.urls["edge"])
    s.order()
    count = lambda route: s.metric("edge", "edge_request_duration_seconds_count", route=route, code="200")
    assert count("POST /checkout") == 1                  # only the real customer
    assert count("POST /checkout (synthetic)") == 6      # two probe orders per run


def test_a_probes_own_network_fault_is_not_the_shops_fault(s):
    r = probe_mod.run_once(s.urls["edge"], fail_rate=1.0)
    assert not r["ok"] and s.metric("edge", "edge_request_duration_seconds_count", route="POST /checkout (synthetic)", code="200") == 0


@pytest.mark.skipif(_promtool() is None, reason="promtool not found")
def test_probe_rules_pass_promtool_unit_tests():
    rules = os.path.join(HERE, "rules")
    for args in (["check", "rules", "checkout-probe.yml"], ["test", "rules", "checkout-probe.test.yml"]):
        out = subprocess.run([_promtool(), *args], cwd=rules, capture_output=True, text=True)
        assert out.returncode == 0, out.stdout + out.stderr
