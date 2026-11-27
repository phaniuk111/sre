#!/usr/bin/env python3
"""Checkout journey lab: one small shop, several services, one file.

Run one role per process:

    python shop.py edge             # :8080  the load balancer / gateway; the journey SLI is measured here
    python shop.py checkout         # :8081  calls the dependencies below, in turn
    python shop.py cart             # :8082  hard dependency
    python shop.py inventory        # :8083  hard dependency
    python shop.py payment          # :8084  hard dependency (card ending 0002 is declined)
    python shop.py orders           # :8085  hard dependency
    python shop.py recommendations  # :8086  soft by default (checkout carries on without it)

Every role serves /metrics for Prometheus. Dependencies accept chaos settings on POST /chaos,
and checkout accepts design changes (hard/soft recommendations, retries) on POST /config.
Only the standard library and prometheus_client are needed.
"""
import argparse
import json
import os
import random
import threading
import time
import urllib.error
import urllib.request
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, Counter, Histogram, generate_latest

# A 2-second boundary is deliberate: the SLO says "confirmed in under 2 s", and a histogram can only
# answer that question if it has a bucket at exactly 2. (Exercise 9 shows what happens without one.)
BUCKETS = (0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 2.5, 5.0)
DEPENDENCIES = ["cart", "inventory", "recommendations", "payment", "orders"]
ROLES = ["edge", "checkout"] + DEPENDENCIES
DEFAULT_PORTS = {"edge": 8080, "checkout": 8081, "cart": 8082, "inventory": 8083,
                 "payment": 8084, "orders": 8085, "recommendations": 8086}


def default_url(role, ports=None):
    """Where a role listens. SHOP_<ROLE>_URL overrides it (docker-compose sets these)."""
    env = os.environ.get(f"SHOP_{role.upper()}_URL")
    if env:
        return env.rstrip("/")
    port = (ports or DEFAULT_PORTS)[role]
    return f"http://127.0.0.1:{port}"


# ----------------------------------------------------------------------------------- chaos
class Chaos:
    """Fault injection for a dependency.

    mode "random": each call fails with probability error_rate (independent failures).
    mode "outage": the service is completely down for the first error_rate share of every
                   period_s seconds (the same error rate, bunched into outages).
    latency_ms / jitter_ms: added to every call.
    slow_rate / slow_ms: a slow_rate share of calls, chosen at random, take slow_ms longer (a long tail).
    """
    KEYS = {"error_rate": float, "mode": str, "period_s": float, "latency_ms": float, "jitter_ms": float,
            "slow_rate": float, "slow_ms": float}

    def __init__(self):
        self._lock = threading.Lock()
        self.cfg = {"error_rate": 0.0, "mode": "random", "period_s": 300.0, "latency_ms": 0.0, "jitter_ms": 0.0,
                    "slow_rate": 0.0, "slow_ms": 0.0}

    def update(self, changes):
        with self._lock:
            if changes.get("reset"):
                self.__init__()
                return dict(self.cfg)
            for k, v in changes.items():
                if k not in self.KEYS:
                    raise ValueError(f"unknown chaos setting {k!r}; use {sorted(self.KEYS)} or reset")
                v = self.KEYS[k](v)
                if k == "mode" and v not in ("random", "outage"):
                    raise ValueError("mode must be random or outage")
                if k in ("error_rate", "slow_rate") and not 0 <= v <= 1:
                    raise ValueError(f"{k} must be between 0 and 1")
                self.cfg[k] = v
            return dict(self.cfg)

    def fails(self, now=None, rnd=random.random):
        c = self.cfg
        if c["error_rate"] <= 0:
            return False
        if c["mode"] == "random":
            return rnd() < c["error_rate"]
        now = time.time() if now is None else now
        return (now % c["period_s"]) / c["period_s"] < c["error_rate"]

    def delay_s(self, rnd=random.random):
        c = self.cfg
        ms = c["latency_ms"] + random.uniform(0, c["jitter_ms"])
        if c["slow_rate"] and rnd() < c["slow_rate"]:
            ms += c["slow_ms"]
        return max(0.0, ms) / 1000.0


# ----------------------------------------------------------------------------------- base server
class Role:
    def __init__(self, name):
        self.name = name
        self.registry = CollectorRegistry()

    def handle(self, method, path, body):  # -> (status, dict)
        return 404, {"error": "not found"}

    def serve(self, port, host="0.0.0.0"):
        role = self

        class Handler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def _reply(self, status, payload, ctype="application/json"):
                data = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
                self.send_response(status)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def _do(self, method):
                n = int(self.headers.get("Content-Length") or 0)
                body = self.rfile.read(n) if n else b""
                if method == "GET" and self.path == "/metrics":
                    return self._reply(200, generate_latest(role.registry), CONTENT_TYPE_LATEST)
                if method == "GET" and self.path == "/healthz":
                    return self._reply(200, {"ok": True, "role": role.name})
                status, payload = role.handle(method, self.path, body)
                self._reply(status, payload)

            def do_GET(self):
                self._do("GET")

            def do_POST(self):
                self._do("POST")

            def log_message(self, *args):
                pass

        server = ThreadingHTTPServer((host, port), Handler)
        server.daemon_threads = True
        return server


def post_json(url, payload, timeout):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), method="POST",
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, json.loads(r.read() or b"{}")


# ----------------------------------------------------------------------------------- dependencies
class Dependency(Role):
    def __init__(self, name):
        super().__init__(name)
        self.chaos = Chaos()
        self.requests = Counter("service_requests_total", "Requests this service answered, by status code",
                                ["service", "code"], registry=self.registry)
        self.duration = Histogram("service_request_duration_seconds", "Time this service spent per request",
                                  ["service"], buckets=BUCKETS, registry=self.registry)

    def handle(self, method, path, body):
        if path == "/chaos":
            if method == "GET":
                return 200, self.chaos.cfg
            try:
                return 200, self.chaos.update(json.loads(body or b"{}"))
            except (ValueError, TypeError) as e:
                return 400, {"error": str(e)}
        if method != "POST" or path != "/call":
            return 404, {"error": "not found"}
        t0 = time.time()
        time.sleep(self.chaos.delay_s())
        if self.chaos.fails():
            status, payload = 500, {"error": f"{self.name} failed"}
        else:
            status, payload = 200, self.answer(json.loads(body or b"{}"))
        self.requests.labels(self.name, str(status)).inc()
        self.duration.labels(self.name).observe(time.time() - t0)
        return status, payload

    def answer(self, req):
        if self.name == "payment" and str(req.get("card", "")).endswith("0002"):
            return {"result": "declined"}
        if self.name == "recommendations":
            return {"items": ["socks", "mug"]}
        return {"result": "ok"}


# ----------------------------------------------------------------------------------- checkout
class Checkout(Role):
    """Calls every dependency in turn. Recommendations are soft unless configured hard."""

    def __init__(self, urls=None, timeout_s=1.5):
        super().__init__("checkout")
        self.urls = urls or {d: default_url(d) for d in DEPENDENCIES}
        self.timeout_s = timeout_s
        self.config = {"recommendations": os.environ.get("RECOMMENDATIONS", "soft"),
                       "retries": json.loads(os.environ.get("RETRIES", "{}"))}
        self.requests = Counter("checkout_requests_total", "Checkout's own count of requests it answered",
                                ["code"], registry=self.registry)
        self.dep_attempts = Counter("checkout_dependency_attempts_total",
                                    "Every call checkout made to a dependency, including retries",
                                    ["dep", "outcome"], registry=self.registry)
        self.dep_duration = Histogram("checkout_dependency_duration_seconds",
                                      "How long each dependency call took, seen from checkout",
                                      ["dep"], buckets=BUCKETS, registry=self.registry)

    def call(self, dep, payload):
        """One logical call: the first attempt plus any configured retries."""
        attempts = 1 + int(self.config["retries"].get(dep, 0))
        for i in range(attempts):
            t0 = time.time()
            try:
                status, body = post_json(self.urls[dep] + "/call", payload, self.timeout_s)
                ok = status == 200
            except (urllib.error.URLError, OSError, ValueError):
                ok, body = False, {}
            self.dep_duration.labels(dep).observe(time.time() - t0)
            self.dep_attempts.labels(dep, "ok" if ok else "error").inc()
            if ok:
                return body
            if i + 1 < attempts:
                time.sleep(0.05 * (2 ** i))  # back off a little before retrying
        return None

    def handle(self, method, path, body):
        if path == "/config":
            if method == "POST":
                try:
                    changes = json.loads(body or b"{}")
                except ValueError:
                    return 400, {"error": "config must be JSON"}
                if "recommendations" in changes and changes["recommendations"] not in ("hard", "soft"):
                    return 400, {"error": "recommendations must be hard or soft"}
                if "retries" in changes:
                    self.config["retries"] = {k: int(v) for k, v in changes["retries"].items()}
                if "recommendations" in changes:
                    self.config["recommendations"] = changes["recommendations"]
            return 200, self.config
        if method != "POST" or path != "/checkout":
            return 404, {"error": "not found"}
        status, payload = self.place_order(body)
        self.requests.labels(str(status)).inc()
        return status, payload

    def place_order(self, body):
        try:
            order = json.loads(body or b"{}")
            assert isinstance(order.get("items"), list) and order["items"] and order.get("card")
        except (ValueError, AssertionError):
            return 400, {"error": "malformed order: send items and card"}
        for dep in DEPENDENCIES:
            result = self.call(dep, order)
            if result is None:
                if dep == "recommendations" and self.config["recommendations"] == "soft":
                    continue  # the page is shown without the panel
                return 503, {"error": f"{dep} unavailable"}
            if dep == "payment" and result.get("result") == "declined":
                return 200, {"status": "declined"}  # a correct answer, quickly: a good event
        return 200, {"status": "confirmed", "order_id": uuid.uuid4().hex[:12]}


# ----------------------------------------------------------------------------------- edge
class Edge(Role):
    """The load balancer. Every attempt passes here, including ones checkout never sees."""

    ROUTE = "POST /checkout"
    SYNTHETIC_ROUTE = "POST /checkout (synthetic)"   # probe.py's test orders: measured, but not customers

    def __init__(self, checkout_url=None, timeout_s=5.0):
        super().__init__("edge")
        self.checkout_url = checkout_url or default_url("checkout")
        self.timeout_s = timeout_s
        self.duration = Histogram("edge_request_duration_seconds",
                                  "Customer requests at the edge, by route and status code",
                                  ["route", "code"], buckets=BUCKETS, registry=self.registry)

    def handle(self, method, path, body):
        if method != "POST" or path != "/checkout":
            return 404, {"error": "not found"}
        t0 = time.time()
        route = self.ROUTE
        try:
            if json.loads(body or b"{}").get("synthetic") is True:
                route = self.SYNTHETIC_ROUTE   # keeps probe orders out of the customer SLI (route="POST /checkout")
        except (ValueError, AttributeError):
            pass
        try:
            req = urllib.request.Request(self.checkout_url + "/checkout", data=body, method="POST",
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=self.timeout_s) as r:
                status, payload = r.status, json.loads(r.read() or b"{}")
        except urllib.error.HTTPError as e:
            status, payload = e.code, {"error": "upstream error"}
        except TimeoutError:
            status, payload = 504, {"error": "gateway timeout"}
        except (urllib.error.URLError, OSError) as e:
            reason = getattr(e, "reason", e)
            status = 504 if isinstance(reason, TimeoutError) or "timed out" in str(reason) else 502
            payload = {"error": "bad gateway" if status == 502 else "gateway timeout"}
        self.duration.labels(route, str(status)).observe(time.time() - t0)
        return status, payload


def make_role(name, urls=None):
    if name == "edge":
        return Edge(checkout_url=(urls or {}).get("checkout"))
    if name == "checkout":
        return Checkout(urls={d: (urls or {}).get(d) or default_url(d) for d in DEPENDENCIES})
    if name in DEPENDENCIES:
        return Dependency(name)
    raise SystemExit(f"unknown role {name!r}; choose from {ROLES}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("role", choices=ROLES)
    ap.add_argument("--port", type=int)
    a = ap.parse_args()
    port = a.port or int(os.environ.get("PORT", DEFAULT_PORTS[a.role]))
    server = make_role(a.role).serve(port)
    print(f"{a.role} listening on :{port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
