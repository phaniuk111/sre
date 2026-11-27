#!/usr/bin/env python3
"""Run the pipeline one day at a time and see what finance would have seen.

  python lab.py reset
  python lab.py day                      a normal day: orders arrive, the 02:00 job runs, the day is judged
  python lab.py day --fail               the job crashes; nothing is published
  python lab.py rerun --at 03:30         rerun the last day's job (idempotent). Before 07:00 it still counts
  python lab.py day --drop 0.02          the job exits 0 but loses 2% of rows
  python lab.py day --corrupt            the job exits 0 but forgets to divide pence by 100
  python lab.py day --duplicate          a non-idempotent load appends the rows twice
  python lab.py day --quiet              the shop is closed: no orders at all
  python lab.py day --late 09:15         the job finishes after the deadline
  python lab.py check                    the three checks for the last day, read-only
  python lab.py lag                      freshness two ways: high-water gap against "now minus newest row"
  python lab.py month                    good days, compliance against the SLO, budget left
  python lab.py metrics                  what the checker exports to Prometheus
"""
import argparse
import json
import os
import shutil
from datetime import timedelta

import etl

HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.environ.get("ETL_LAB_DIR", os.path.join(HERE, ".lab"))
STATE = os.path.join(LAB, "state.json")


def load():
    return json.load(open(STATE)) if os.path.exists(STATE) else {"day": 0, "history": []}


def save(state):
    os.makedirs(LAB, exist_ok=True)
    json.dump(state, open(STATE, "w"), indent=1)


def at_time(day, hhmm):
    h, m = (int(x) for x in hhmm.split(":"))
    return etl.day_start(day + 1) + timedelta(hours=h, minutes=m)


def verdict_line(v, status=None):
    mark = lambda ok: "ok " if ok else "BAD"
    r = v["reconcile"]
    out = [f"day {v['day']} ({v['date']})" + (f"   job exit status: {status}" if status else ""),
           f"  freshness    {mark(v['fresh'])}  published {v['published_at'] or 'never'}  (deadline {v['deadline']})",
           f"  completeness {mark(v['complete'])}  {r['warehouse_rows']} of {r['source_rows']} rows  (ratio {r['rows_ratio']})",
           f"  correctness  {mark(v['correct'])}  totals differ by £{r['total_diff']}; traced {v['traced']['traced']} real orders, {len(v['traced']['problems'])} wrong",
           f"  => {'GOOD' if v['good'] else 'BAD'} day for finance"]
    for p in v["traced"]["problems"][:2]:
        out.insert(-1, f"                    {p}")
    return "\n".join(out)


def record(state, v):
    state["history"] = [h for h in state["history"] if h["day"] != v["day"]] + [{"day": v["day"], "good": v["good"]}]
    save(state)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("reset")
    d = sub.add_parser("day")
    d.add_argument("--fail", action="store_true"); d.add_argument("--corrupt", action="store_true")
    d.add_argument("--duplicate", action="store_true"); d.add_argument("--quiet", action="store_true")
    d.add_argument("--drop", type=float, default=0.0); d.add_argument("--late", default=None, metavar="HH:MM")
    d.add_argument("--orders", type=int, default=400)
    r = sub.add_parser("rerun"); r.add_argument("--at", default="03:30", metavar="HH:MM")
    for name in ("check", "lag", "month", "metrics"):
        sub.add_parser(name)
    a = ap.parse_args()

    if a.cmd == "reset":
        shutil.rmtree(LAB, ignore_errors=True)
        etl.connect(LAB); save({"day": 0, "history": []})
        print("fresh lab: empty source and warehouse, calendar at day 0"); return
    state = load()
    src, wh = etl.connect(LAB)
    day = state["day"]

    if a.cmd == "day":
        day += 1
        if not a.quiet:
            etl.source_takes_orders(src, day, a.orders)
        finished = at_time(day, a.late or "02:10")
        status = etl.run_job(src, wh, day, finished, drop=a.drop, corrupt=a.corrupt, duplicate=a.duplicate, fail=a.fail)
        state["day"] = day
        v = etl.check(src, wh, day)
        record(state, v)
        print(verdict_line(v, status))
    elif a.cmd == "rerun":
        if not day:
            raise SystemExit("run a day first")
        status = etl.run_job(src, wh, day, at_time(day, a.at))
        v = etl.check(src, wh, day)
        record(state, v)
        print(f"rerun finished at {a.at}\n" + verdict_line(v, status))
    elif a.cmd == "check":
        print(verdict_line(etl.check(src, wh, day)))
    elif a.cmd == "lag":
        s, o = etl.high_water(src, wh)
        now = etl.deadline(day)
        gap = (s - o) if s and o else None
        print(f"judged at the deadline, {now}")
        print(f"  newest order at source   {s}\n  newest order in warehouse {o}")
        print(f"  high-water gap           {gap}   <- is the pipeline behind the source?")
        print(f"  now minus newest row     {now - o if o else None}   <- also grows when the source is simply quiet")
    elif a.cmd == "month":
        m = etl.month([h["good"] for h in state["history"]])
        print("days: " + " ".join(("." if h["good"] else "X") for h in sorted(state["history"], key=lambda h: h["day"])))
        print(json.dumps(m, indent=1))
    elif a.cmd == "metrics":
        print(etl.metrics(src, wh, day, etl.deadline(day)), end="")


if __name__ == "__main__":
    main()
