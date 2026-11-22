#!/usr/bin/env python3
"""Steady customer traffic for the lab: real orders, a few declined cards, a few malformed requests.

    python loadgen.py --rps 10

About 3% of orders use a card that the bank declines (a correct answer, so a good event) and about
2% are malformed (HTTP 400, which the SLI leaves out of valid events).
"""
import argparse
import json
import os
import random
import threading
import time
import urllib.error
import urllib.request
from collections import Counter

EDGE = os.environ.get("SHOP_EDGE_URL", "http://127.0.0.1:8080").rstrip("/")


def one_order(edge=EDGE, timeout=10):
    r = random.random()
    if r < 0.02:
        body = b'{"items": []}'                      # malformed: no items, no card
    else:
        card = "4000000000000002" if r < 0.05 else "4000000000000077"
        body = json.dumps({"items": ["sku-123"], "card": card}).encode()
    req = urllib.request.Request(edge + "/checkout", data=body, method="POST",
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        return e.code
    except (urllib.error.URLError, OSError):
        return "no-answer"


def run(rps, seconds=None, edge=EDGE, report_every=10):
    stop = time.time() + seconds if seconds else None
    counts, lock = Counter(), threading.Lock()

    def worker():
        code = one_order(edge)
        with lock:
            counts[code] += 1

    last = time.time()
    while stop is None or time.time() < stop:
        threading.Thread(target=worker, daemon=True).start()
        time.sleep(random.expovariate(rps))
        if time.time() - last >= report_every:
            with lock:
                print(time.strftime("%H:%M:%S"), dict(sorted(counts.items(), key=str)), flush=True)
                counts.clear()
            last = time.time()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rps", type=float, default=float(os.environ.get("RPS", 10)))
    ap.add_argument("--seconds", type=float)
    a = ap.parse_args()
    print(f"sending about {a.rps} orders a second to {EDGE}", flush=True)
    run(a.rps, a.seconds)
