"""A nightly revenue pipeline you can break, and the read-only checks that judge it.

The source is an orders database owned by another team: we may read it, never write to it.
Every night at 02:00 the job copies yesterday's orders into the warehouse (pence -> pounds)
and publishes the partition. Finance reads it at 08:00, so the deadline is 07:00.

The SLO is about what finance sees, not about the job's exit code:
  freshness     yesterday's partition was published by 07:00
  completeness  the warehouse has the same number of rows as the source (within 0.1%)
  correctness   the totals match, and a handful of real orders traced end to end match
A day is good only if all three hold.
"""
import os
import random
import sqlite3
from datetime import datetime, timedelta

BASE = datetime(2026, 11, 1)          # day 1 of the lab's calendar
JOB_HOUR, DEADLINE_HOUR = 2, 7
ROW_TOLERANCE = 0.001                 # 0.1%
SLO_TARGET = 29 / 30                  # one bad day a month


def day_start(day):
    return BASE + timedelta(days=day - 1)


def date_of(day):
    return day_start(day).date().isoformat()


def deadline(day):
    """When day's partition must be published: 07:00 the next morning."""
    return day_start(day + 1) + timedelta(hours=DEADLINE_HOUR)


def connect(folder):
    os.makedirs(folder, exist_ok=True)
    src = sqlite3.connect(os.path.join(folder, "source.db"))
    wh = sqlite3.connect(os.path.join(folder, "warehouse.db"))
    src.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, amount_pence INTEGER, order_date TEXT, updated_at TEXT)")
    wh.execute("CREATE TABLE IF NOT EXISTS fact_orders (order_id INTEGER, amount_gbp REAL, order_date TEXT, source_updated_at TEXT, loaded_at TEXT)")
    wh.execute("CREATE TABLE IF NOT EXISTS published (order_date TEXT PRIMARY KEY, published_at TEXT)")
    return src, wh


# ------------------------------------------------------------------ the source system (not ours)
def source_takes_orders(src, day, n=400, seed=None):
    """The shop takes n orders during the day. This is the other team's system writing its own table."""
    rng = random.Random(seed if seed is not None else day)
    rows = []
    for _ in range(n):
        at = day_start(day) + timedelta(seconds=rng.randrange(8 * 3600, 23 * 3600))
        rows.append((rng.randrange(500, 20000), date_of(day), at.isoformat(sep=" ")))
    src.executemany("INSERT INTO orders (amount_pence, order_date, updated_at) VALUES (?, ?, ?)", sorted(rows, key=lambda r: r[2]))
    src.commit()
    return n


# ------------------------------------------------------------------ the pipeline (ours)
def run_job(src, wh, day, at, drop=0.0, corrupt=False, duplicate=False, fail=False, seed=0):
    """Extract day's orders, transform, load, publish. `at` is when the job finishes.

    The load is idempotent: it replaces the partition, so a rerun is always safe.
    Faults: fail (crash before loading), drop (lose a share of rows), corrupt (forget to
    divide by 100), duplicate (append instead of replace, twice).
    Returns the job's exit status, which is "ok" for every fault except fail.
    """
    if fail:
        return "failed"
    rng = random.Random(seed + day)
    rows = src.execute("SELECT id, amount_pence, order_date, updated_at FROM orders WHERE order_date = ?", (date_of(day),)).fetchall()
    rows = [r for r in rows if rng.random() >= drop]
    out = [(i, pence if corrupt else pence / 100, d, u, at.isoformat(sep=" ")) for i, pence, d, u in rows]
    if not duplicate:
        wh.execute("DELETE FROM fact_orders WHERE order_date = ?", (date_of(day),))
    for _ in range(2 if duplicate else 1):
        wh.executemany("INSERT INTO fact_orders VALUES (?, ?, ?, ?, ?)", out)
    # published_at is when the partition's current contents were written, so a late correction counts as late
    wh.execute("INSERT INTO published VALUES (?, ?) ON CONFLICT(order_date) DO UPDATE SET published_at = excluded.published_at",
               (date_of(day), at.isoformat(sep=" ")))
    wh.commit()
    return "ok"


# ------------------------------------------------------------------ the checks (read-only on both sides)
def _ts(s):
    return datetime.fromisoformat(s) if s else None


def high_water(src, wh):
    """Newest timestamp on each side. The gap is the freshness lag, and it stays small when the
    source is quiet, unlike "now minus the newest row in the warehouse"."""
    s = _ts(src.execute("SELECT max(updated_at) FROM orders").fetchone()[0])
    o = _ts(wh.execute("SELECT max(source_updated_at) FROM fact_orders").fetchone()[0])
    return s, o


def reconcile(src, wh, day):
    d = (date_of(day),)
    s_rows, s_pence = src.execute("SELECT count(*), coalesce(sum(amount_pence), 0) FROM orders WHERE order_date = ?", d).fetchone()
    o_rows, o_gbp = wh.execute("SELECT count(*), coalesce(sum(amount_gbp), 0) FROM fact_orders WHERE order_date = ?", d).fetchone()
    ratio = (o_rows / s_rows) if s_rows else (1.0 if o_rows == 0 else float("inf"))
    return {"source_rows": s_rows, "warehouse_rows": o_rows, "rows_ratio": round(ratio, 4),
            "source_total": round(s_pence / 100, 2), "warehouse_total": round(o_gbp, 2), "total_diff": round(o_gbp - s_pence / 100, 2)}


def trace_records(src, wh, day, n=5):
    """Follow n real orders from the source into the warehouse. No test rows are written anywhere."""
    picked = src.execute("SELECT id, amount_pence FROM orders WHERE order_date = ? ORDER BY (id * 7919) % 1000 LIMIT ?", (date_of(day), n)).fetchall()
    bad = []
    for oid, pence in picked:
        got = wh.execute("SELECT amount_gbp FROM fact_orders WHERE order_id = ?", (oid,)).fetchall()
        if len(got) != 1:
            bad.append(f"order {oid}: found {len(got)} times")
        elif abs(got[0][0] - pence / 100) > 0.005:
            bad.append(f"order {oid}: {got[0][0]} in the warehouse, {pence / 100} at source")
    return {"traced": len(picked), "problems": bad}


def check(src, wh, day):
    """Was day a good day for finance? Judged at the deadline, from data only."""
    pub = _ts((wh.execute("SELECT published_at FROM published WHERE order_date = ?", (date_of(day),)).fetchone() or [None])[0])
    rec, traced = reconcile(src, wh, day), trace_records(src, wh, day)
    fresh = pub is not None and pub <= deadline(day)
    complete = abs(rec["rows_ratio"] - 1) <= ROW_TOLERANCE
    correct = abs(rec["total_diff"]) <= 0.01 and not traced["problems"]
    return {"day": day, "date": date_of(day), "published_at": pub.isoformat(sep=" ") if pub else None, "deadline": deadline(day).isoformat(sep=" "),
            "fresh": fresh, "complete": complete, "correct": correct, "good": fresh and complete and correct,
            "reconcile": rec, "traced": traced}


def month(history, target=SLO_TARGET):
    """Compliance and budget from a list of per-day verdicts (True = good day)."""
    days, good = len(history), sum(history)
    allowed = round(30 * (1 - target))            # bad days allowed in a 30-day window: 1
    return {"days": days, "good_days": good, "bad_days": days - good, "compliance": round(good / days, 4) if days else None,
            "target": round(target, 4), "bad_days_allowed_per_30": allowed, "budget_left": allowed - (days - good)}


def metrics(src, wh, day, now):
    """Prometheus text exposition for the checker. Push it, or write it for the node_exporter textfile collector."""
    s, o = high_water(src, wh)
    rec = reconcile(src, wh, day)
    pub = _ts((wh.execute("SELECT max(published_at) FROM published").fetchone() or [None])[0])
    epoch = lambda t: int((t - datetime(1970, 1, 1)).total_seconds()) if t else 0
    lines = [f'etl_source_high_water_seconds{{pipeline="revenue"}} {epoch(s)}',
             f'etl_output_high_water_seconds{{pipeline="revenue"}} {epoch(o)}',
             f'etl_last_publish_timestamp_seconds{{pipeline="revenue"}} {epoch(pub)}',
             f'etl_partition_rows_ratio{{pipeline="revenue"}} {rec["rows_ratio"]}',
             f'etl_partition_total_diff{{pipeline="revenue"}} {rec["total_diff"]}',
             f'etl_check_timestamp_seconds{{pipeline="revenue"}} {epoch(now)}']
    return "\n".join(lines) + "\n"
