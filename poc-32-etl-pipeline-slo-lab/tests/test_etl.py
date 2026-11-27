import os
import shutil
import subprocess
import sys
from datetime import timedelta

import pytest

HERE = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, HERE)
import etl  # noqa: E402


@pytest.fixture
def dbs(tmp_path):
    return etl.connect(str(tmp_path))


def run_day(dbs, day, at="02:10", **faults):
    src, wh = dbs
    etl.source_takes_orders(src, day)
    h, m = (int(x) for x in at.split(":"))
    status = etl.run_job(src, wh, day, etl.day_start(day + 1) + timedelta(hours=h, minutes=m), **faults)
    return status, etl.check(src, wh, day)


def test_a_normal_day_is_good(dbs):
    status, v = run_day(dbs, 1)
    assert status == "ok" and v["good"] and v["reconcile"]["rows_ratio"] == 1.0 and v["traced"]["traced"] == 5


def test_exit_status_ok_does_not_mean_the_data_is_ok(dbs):
    status, v = run_day(dbs, 1, drop=0.02)
    assert status == "ok" and v["fresh"] and not v["complete"] and not v["good"]
    status, v = run_day(dbs, 2, corrupt=True)
    assert status == "ok" and v["complete"] and not v["correct"] and v["traced"]["problems"]


def test_reconciliation_catches_what_a_sample_of_traced_records_can_miss(dbs):
    _, v = run_day(dbs, 1, drop=0.02)
    assert v["traced"]["problems"] == [] and v["reconcile"]["warehouse_rows"] < v["reconcile"]["source_rows"]


def test_a_failed_run_rerun_before_the_deadline_is_a_good_day(dbs):
    src, wh = dbs
    status, v = run_day(dbs, 1, fail=True)
    assert status == "failed" and not v["good"]
    etl.run_job(src, wh, 1, etl.day_start(2) + timedelta(hours=3, minutes=30))
    assert etl.check(src, wh, 1)["good"]


def test_a_rerun_after_the_deadline_is_still_a_bad_day(dbs):
    src, wh = dbs
    run_day(dbs, 1, drop=0.5)
    etl.run_job(src, wh, 1, etl.day_start(2) + timedelta(hours=9))
    v = etl.check(src, wh, 1)
    assert v["complete"] and v["correct"] and not v["fresh"] and not v["good"]


def test_the_load_is_idempotent_and_a_non_idempotent_one_is_caught(dbs):
    src, wh = dbs
    run_day(dbs, 1)
    etl.run_job(src, wh, 1, etl.day_start(2) + timedelta(hours=3))
    assert etl.reconcile(src, wh, 1)["rows_ratio"] == 1.0
    _, v = run_day(dbs, 2, duplicate=True)
    assert v["reconcile"]["rows_ratio"] == 2.0 and not v["good"]


def test_a_quiet_source_is_not_a_stale_pipeline(dbs):
    src, wh = dbs
    run_day(dbs, 1)
    status = etl.run_job(src, wh, 2, etl.day_start(3) + timedelta(hours=2))  # day 2: the shop was closed
    assert status == "ok" and etl.check(src, wh, 2)["good"]
    s, o = etl.high_water(src, wh)
    assert s == o                                     # high-water gap: zero
    assert etl.deadline(2) - o > timedelta(hours=24)  # "now minus newest row" would have paged


def test_month_budget_allows_one_bad_day():
    assert etl.month([True] * 29 + [False])["budget_left"] == 0
    m = etl.month([True] * 28 + [False] * 2)
    assert m["budget_left"] == -1 and m["compliance"] < m["target"]


def test_metrics_are_valid_exposition(dbs):
    src, wh = dbs
    run_day(dbs, 1)
    text = etl.metrics(src, wh, 1, etl.deadline(1))
    assert text.count("\n") == 6 and 'etl_partition_rows_ratio{pipeline="revenue"} 1.0' in text


def test_cli_walkthrough(tmp_path):
    env = {**os.environ, "ETL_LAB_DIR": str(tmp_path / "lab")}
    run = lambda *a: subprocess.run([sys.executable, os.path.join(HERE, "lab.py"), *a], env=env, capture_output=True, text=True, check=True).stdout
    run("reset")
    assert "GOOD day" in run("day")
    assert "BAD day" in run("day", "--fail")
    assert "GOOD day" in run("rerun", "--at", "03:30")
    assert "BAD day" in run("day", "--late", "09:15")
    assert '"bad_days": 1' in run("month")


@pytest.mark.skipif(not shutil.which("promtool"), reason="promtool not on PATH")
def test_alert_rules_with_promtool():
    r = subprocess.run(["promtool", "test", "rules", "etl-slo.test.yml"], cwd=os.path.join(HERE, "rules"), capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
