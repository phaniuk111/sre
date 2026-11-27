#!/usr/bin/env python3
"""A synthetic probe: a scripted customer that walks the checkout journey on a schedule.

    python probe.py --once                                  one run, printed
    python probe.py --location london --port 9201           run every 5 s and serve /metrics

Each run places a test order and a declined-card order through the edge, exactly as a browser would,
and checks the answers and the time taken. Test orders carry "synthetic": true, which the edge uses to
record them under their own route label, so they never count in the customer SLI or in revenue.

Why run one when you already measure real traffic: it keeps producing events at 3 a.m. when nobody is
buying, it covers the path from outside, and it finds a broken journey before the first customer does.
--fail-rate simulates this probe's own network being bad, to show why one location must not page.
"""
import argparse
import json
import os
import random
import time
import urllib.error
import urllib.request

from prometheus_client import Counter, Gauge, start_http_server

EDGE = os.environ.get("SHOP_EDGE_URL", "http://127.0.0.1:8080").rstrip("/")
LIMIT_S = 2.0                                        # the SLO's latency threshold
TEST_CARD, DECLINED_CARD = "4000000000000077", "4000000000000002"


def _order(edge, card, timeout):
    body = json.dumps({"items": ["probe-sku"], "card": card, "synthetic": True}).encode()
    req = urllib.request.Request(edge + "/checkout", data=body, method="POST", headers={"Content-Type": "application/json"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read() or b"{}"), time.time() - t0
    except urllib.error.HTTPError as e:
        return e.code, {}, time.time() - t0
    except (urllib.error.URLError, OSError, ValueError):
        return 0, {}, time.time() - t0


def run_once(edge=EDGE, timeout=5.0, fail_rate=0.0, rnd=random.random):
    """Walk the journey. Returns {"ok", "seconds", "steps": [(name, ok, detail)]}."""
    if rnd() < fail_rate:
        return {"ok": False, "seconds": 0.0, "steps": [("reach the shop", False, "this probe's own network failed")]}
    steps, total = [], 0.0
    status, body, took = _order(edge, TEST_CARD, timeout)
    total += took
    ok = status == 200 and body.get("status") == "confirmed" and bool(body.get("order_id")) and took < LIMIT_S
    steps.append(("place a test order", ok, f"HTTP {status}, {body.get('status', 'no answer')}, {took:.2f} s"))
    status, body, took = _order(edge, DECLINED_CARD, timeout)
    total += took
    ok2 = status == 200 and body.get("status") == "declined" and took < LIMIT_S
    steps.append(("declined card is refused politely", ok2, f"HTTP {status}, {body.get('status', 'no answer')}, {took:.2f} s"))
    return {"ok": ok and ok2, "seconds": total, "steps": steps}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--edge", default=EDGE); ap.add_argument("--location", default="local")
    ap.add_argument("--port", type=int, default=9201); ap.add_argument("--interval", type=float, default=5.0)
    ap.add_argument("--fail-rate", type=float, default=0.0); ap.add_argument("--once", action="store_true")
    a = ap.parse_args()
    if a.once:
        r = run_once(a.edge, fail_rate=a.fail_rate)
        for name, ok, detail in r["steps"]:
            print(f"  {'ok ' if ok else 'BAD'} {name}: {detail}")
        print(f"probe {'succeeded' if r['ok'] else 'FAILED'} in {r['seconds']:.2f} s")
        raise SystemExit(0 if r["ok"] else 1)
    labels = {"journey": "checkout", "location": a.location}
    success = Gauge("probe_success", "1 if the last run of the journey passed every step", list(labels))
    duration = Gauge("probe_duration_seconds", "How long the last run took", list(labels))
    last = Gauge("probe_last_run_timestamp_seconds", "When the probe last ran: alert if this stops moving", list(labels))
    runs = Counter("probe_runs_total", "Probe runs by result", list(labels) + ["result"])
    start_http_server(a.port)
    print(f"probe {a.location}: {a.edge} every {a.interval}s, metrics on :{a.port}", flush=True)
    while True:
        r = run_once(a.edge, fail_rate=a.fail_rate)
        success.labels(**labels).set(1 if r["ok"] else 0)
        duration.labels(**labels).set(r["seconds"])
        last.labels(**labels).set(time.time())
        runs.labels(result="ok" if r["ok"] else "fail", **labels).inc()
        time.sleep(a.interval)


if __name__ == "__main__":
    main()
