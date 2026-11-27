#!/usr/bin/env python3
"""Drive the checkout lab from your terminal.

  python lab.py up                       start the shop, the load generator and Prometheus (if found)
  python lab.py status                   journey SLI, burn rates, budget, each dependency, firing alerts
  python lab.py chaos payment --error-rate 0.02 --mode random
  python lab.py chaos payment --error-rate 0.02 --mode outage --period-s 300
  python lab.py chaos payment --latency-ms 1800
  python lab.py chaos payment --slow-rate 0.02 --slow-ms 1500
  python lab.py chaos payment --reset
  python lab.py config --recommendations hard
  python lab.py config --retries payment=1
  python lab.py stop checkout            kill one service (the edge keeps answering, with 502s)
  python lab.py start checkout
  python lab.py promql 'journey:checkout_error_ratio:rate5m'
  python lab.py probe                    run the synthetic probe once and print each step
  python lab.py probe-fault dublin on    give one probe location a broken network (off to mend it)
  python lab.py down                     stop everything

Works the same against `docker compose up` (ports are mapped to the same numbers); there, use
`docker compose stop checkout` / `start checkout` instead of lab.py stop/start.
Prometheus: put the binary in ./bin (make prometheus) or pass --prometheus /path/to/prometheus.
"""
import argparse
import json
import os
import signal
import subprocess
import sys
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, ".lab")
PROBES = {"london": 9201, "dublin": 9202, "frankfurt": 9203}   # three synthetic probe locations
PROM = os.environ.get("PROM_URL", "http://127.0.0.1:9090").rstrip("/")
sys.path.insert(0, HERE)
from shop import DEFAULT_PORTS, ROLES, default_url  # noqa: E402


def _pidfile(name):
    return os.path.join(STATE, f"{name}.pid")


def _spawn(name, argv):
    os.makedirs(os.path.join(STATE, "logs"), exist_ok=True)
    log = open(os.path.join(STATE, "logs", f"{name}.log"), "ab")
    p = subprocess.Popen(argv, cwd=HERE, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    with open(_pidfile(name), "w") as f:
        f.write(str(p.pid))
    return p.pid


def _kill(name):
    try:
        pid = int(open(_pidfile(name)).read())
        os.killpg(pid, signal.SIGTERM)
    except (FileNotFoundError, ProcessLookupError, ValueError):
        return False
    finally:
        if os.path.exists(_pidfile(name)):
            os.remove(_pidfile(name))
    return True


def _post(url, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), method="POST",
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=5) as r:
        return json.loads(r.read())


def _wait_up(role, seconds=10):
    end = time.time() + seconds
    while time.time() < end:
        try:
            urllib.request.urlopen(default_url(role) + "/healthz", timeout=1)
            return True
        except OSError:
            time.sleep(0.2)
    return False


def find_prometheus(explicit=None):
    for p in [explicit, os.environ.get("PROMETHEUS_BIN"), os.path.join(HERE, "bin", "prometheus")]:
        if p and os.path.exists(p):
            return p
    return None


def up(a):
    py = sys.executable
    for role in ROLES:
        if not os.path.exists(_pidfile(role)):
            _spawn(role, [py, "shop.py", role])
    for role in ROLES:
        if not _wait_up(role):
            sys.exit(f"{role} did not start; see .lab/logs/{role}.log")
    if not os.path.exists(_pidfile("loadgen")):
        _spawn("loadgen", [py, "loadgen.py", "--rps", str(a.rps)])
    for loc, port in PROBES.items():
        if not os.path.exists(_pidfile(f"probe-{loc}")):
            _spawn(f"probe-{loc}", [py, "probe.py", "--location", loc, "--port", str(port)])
    prom = find_prometheus(a.prometheus)
    if prom and not os.path.exists(_pidfile("prometheus")):
        _spawn("prometheus", [prom, "--config.file=prometheus/prometheus.local.yml",
                              f"--storage.tsdb.path={os.path.join(STATE, 'prom-data')}",
                              "--web.listen-address=127.0.0.1:9090", "--web.enable-lifecycle"])
        print("Prometheus: http://127.0.0.1:9090  (alerts tab: /alerts)")
    elif not prom:
        print("No Prometheus binary found: run `make prometheus`, or use `docker compose up`.")
    print("Shop is up. Edge (the load balancer): http://127.0.0.1:8080  ·  load: ~%s orders/s" % a.rps)
    print("Give it 2-3 minutes of healthy traffic, then run: python lab.py status")


def down(_):
    for name in ROLES + ["loadgen", "prometheus"] + [f"probe-{loc}" for loc in PROBES]:
        if _kill(name):
            print("stopped", name)


def stop(a):
    print("stopped" if _kill(a.role) else "was not running", a.role)


def start(a):
    _spawn(a.role, [sys.executable, "shop.py", a.role])
    print("started" if _wait_up(a.role) else "failed to start", a.role)


def probe(_):
    import probe as P
    r = P.run_once(default_url("edge"))
    for name, ok, detail in r["steps"]:
        print(f"  {'ok ' if ok else 'BAD'} {name}: {detail}")
    print(f"probe {'succeeded' if r['ok'] else 'FAILED'} in {r['seconds']:.2f} s")


def probe_fault(a):
    name = f"probe-{a.location}"
    _kill(name)
    argv = [sys.executable, "probe.py", "--location", a.location, "--port", str(PROBES[a.location])]
    _spawn(name, argv + (["--fail-rate", "1"] if a.state == "on" else []))
    print(f"{name}: network {'broken' if a.state == 'on' else 'mended'}")


def chaos(a):
    if a.role not in DEFAULT_PORTS or a.role in ("edge", "checkout"):
        sys.exit("chaos works on dependencies: cart, inventory, payment, orders, recommendations")
    changes = {"reset": True} if a.reset else {
        k: v for k, v in {"error_rate": a.error_rate, "mode": a.mode, "period_s": a.period_s,
                          "latency_ms": a.latency_ms, "jitter_ms": a.jitter_ms,
                          "slow_rate": a.slow_rate, "slow_ms": a.slow_ms}.items() if v is not None}
    print(a.role, _post(default_url(a.role) + "/chaos", changes))


def config(a):
    changes = {}
    if a.recommendations:
        changes["recommendations"] = a.recommendations
    if a.retries is not None:
        changes["retries"] = dict(kv.split("=") for kv in a.retries if kv)
    print("checkout", _post(default_url("checkout") + "/config", changes))


def query(expr):
    url = PROM + "/api/v1/query?" + urllib.parse.urlencode({"query": expr})
    with urllib.request.urlopen(url, timeout=10) as r:
        data = json.loads(r.read())
    if data.get("status") != "success":
        raise RuntimeError(data)
    return data["data"]["result"]


def value(expr):
    res = query(expr)
    return float(res[0]["value"][1]) if res else None


def _pct(v, digits=3):
    return "—" if v is None else f"{v * 100:.{digits}f}%"


def status(_):
    try:
        e5, e1h = value("journey:checkout_error_ratio:rate5m"), value("journey:checkout_error_ratio:rate1h")
    except OSError:
        sys.exit(f"Can't reach Prometheus at {PROM}. Is it running? (python lab.py up, or docker compose up)")
    rows = [
        ("Journey SLI, last 5 min (at the edge)", _pct(None if e5 is None else 1 - e5)),
        ("Journey SLI, last hour", _pct(None if e1h is None else 1 - e1h)),
        ("Checkout's own success rate, 5 min", _pct(value("service:checkout_own_success:ratio_rate5m"))),
        ("Burn rate, 5 min", "—" if e5 is None else f"{e5 / 0.001:.1f}x"),
        ("Burn rate, 1 hour", "—" if e1h is None else f"{e1h / 0.001:.1f}x"),
        ("Error budget left (30 days so far)", _pct(value("journey:checkout_error_budget_remaining:ratio"), 1)),
        ("Journey p99 at the edge, 5 min",
         _sec(value('histogram_quantile(0.99, sum by (le) (rate(edge_request_duration_seconds_bucket{route="POST /checkout"}[5m])))'))),
    ]
    width = max(len(r[0]) for r in rows)
    print("\nCHECKOUT JOURNEY (SLO 99.9% confirmed in under 2 s · page at 14.4x)")
    for k, v in rows:
        print(f"  {k:<{width}}  {v}")
    print("\nDEPENDENCIES as checkout sees them (every attempt, 5 min)")
    deps = {r["metric"]["dep"]: float(r["value"][1]) for r in query("dep:checkout_dependency_success:ratio_rate5m")}
    p99 = {r["metric"]["dep"]: float(r["value"][1]) for r in query(
        "histogram_quantile(0.99, sum by (dep, le) (rate(checkout_dependency_duration_seconds_bucket[5m])))")}
    for d in sorted(deps):
        print(f"  {d:<16} success {_pct(deps[d]):>9}   p99 {_sec(p99.get(d))}")
    alerts = [r["metric"] for r in query('ALERTS{alertstate="firing"}')]
    pending = [r["metric"] for r in query('ALERTS{alertstate="pending"}')]
    print("\nALERTS")
    for m in alerts:
        print(f"  FIRING   {m['alertname']}  ({m.get('severity', '')})")
    for m in pending:
        print(f"  pending  {m['alertname']}  ({m.get('severity', '')})")
    if not alerts and not pending:
        print("  none")
    print()


def _sec(v):
    return "—" if v is None or v != v else f"{v:.2f} s"


def promql(a):
    for r in query(a.expr):
        print(r["metric"], r["value"][1])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("up"); p.add_argument("--rps", type=float, default=10); p.add_argument("--prometheus")
    p.set_defaults(fn=up)
    sub.add_parser("down").set_defaults(fn=down)
    sub.add_parser("status").set_defaults(fn=status)
    for name, fn in (("stop", stop), ("start", start)):
        p = sub.add_parser(name); p.add_argument("role", choices=ROLES); p.set_defaults(fn=fn)
    p = sub.add_parser("chaos"); p.add_argument("role")
    p.add_argument("--error-rate", type=float); p.add_argument("--mode", choices=["random", "outage"])
    p.add_argument("--period-s", type=float); p.add_argument("--latency-ms", type=float)
    p.add_argument("--jitter-ms", type=float); p.add_argument("--slow-rate", type=float)
    p.add_argument("--slow-ms", type=float); p.add_argument("--reset", action="store_true")
    p.set_defaults(fn=chaos)
    p = sub.add_parser("config"); p.add_argument("--recommendations", choices=["hard", "soft"])
    p.add_argument("--retries", nargs="*", metavar="DEP=N"); p.set_defaults(fn=config)
    p = sub.add_parser("promql"); p.add_argument("expr"); p.set_defaults(fn=promql)
    sub.add_parser("probe").set_defaults(fn=probe)
    p = sub.add_parser("probe-fault"); p.add_argument("location", choices=list(PROBES)); p.add_argument("state", choices=["on", "off"])
    p.set_defaults(fn=probe_fault)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
