import os
import sys
from datetime import timedelta

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, ".."))

from backup_slo import fleet_report, load_sample  # noqa: E402


def test_fleet_report_finds_gaps():
    srcs = load_sample(os.path.join(HERE, "..", "examples", "recovery_points.json"))
    end = max(max(s.recovery_points) for s in srcs)
    r = fleet_report(srcs, end - timedelta(days=7), end)
    per = r["per_source_rpo_compliance"]
    assert per["arn:aws:dynamodb:eu-west-2:111122223333:table/orders"] == 1.0
    assert per["arn:aws:dynamodb:eu-west-2:111122223333:table/payments"] < 0.99  # 12h gap in hourly backups
    assert r["slo_met"] is False
    assert r["untested_or_slow_restores"] == ["arn:aws:rds:eu-west-2:111122223333:db:catalog"]
    assert r["rwo_gaps"] == []  # 36 days of hourly points covers the 35-day RWO
