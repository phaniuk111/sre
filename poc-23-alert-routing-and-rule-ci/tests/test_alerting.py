import os
import sys
from datetime import datetime, timezone

import yaml

HERE = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, HERE)
import alerting as A  # noqa: E402

CFG = yaml.safe_load(open(os.path.join(HERE, "config", "alertmanager.yml")))
RULES = yaml.safe_load(open(os.path.join(HERE, "config", "rules.yml")))


def test_most_specific_route_wins_and_parent_is_the_fallback():
    simple = {"route": {"receiver": "fallthrough", "routes": [
        {"receiver": "slack-devops", "matchers": ["team = devops"], "routes": [{"receiver": "pagerduty-devops", "matchers": ["environment = production"]}]}]}}
    assert A.receivers_for(simple, {"environment": "production", "team": "devops"}) == ["pagerduty-devops"]
    assert A.receivers_for(simple, {"environment": "testing", "team": "devops"}) == ["slack-devops"]
    assert A.receivers_for(simple, {"environment": "production", "team": "sre"}) == ["fallthrough"]


def test_continue_sends_to_siblings_too():
    assert A.receivers_for(CFG, {"environment": "production", "team": "devops"}) == ["pagerduty-devops", "default"]
    assert A.receivers_for(CFG, {"environment": "testing", "team": "devops"}) == ["slack-devops"]


def test_the_books_second_table_is_wrong_for_production_sre():
    # The book lists 'fallthrough', but every matcher on the default route holds for this alert:
    # missing namespace is "" (!= default), team matches (devops|sre), missing service doesn't match ^(api.+)
    assert A.receivers_for(CFG, {"environment": "production", "team": "sre"}) == ["default"]


def test_single_quotes_are_literal_in_matchers():
    assert A.matches(['environment = "production"'], {"environment": "production"})
    assert not A.matches(["environment = 'production'"], {"environment": "production"})
    assert A.matches(["environment = 'production'"], {"environment": "'production'"})


def test_grouping_timeline():
    # alerts at 10:00:00, 10:00:17, 10:00:35 (seconds from 10:00)
    sent = A.notification_times([0, 17, 35], until=900)
    assert sent[0] == 30          # group_wait: first two go out together
    assert sent[1] == 330         # 10:05:30, not 10:05:00 as the book's table says: the timer restarts at each flush
    assert len(sent) == 2         # nothing changed afterwards, and repeat_interval (4h) hasn't passed


def test_repeat_interval_resends_an_unchanged_group():
    sent = A.notification_times([0], group_interval=300, repeat_interval=3600, until=7300)
    assert sent == [30, 3630, 7230]


def test_inhibition_mutes_the_warning_only_with_equal_labels():
    crit = {"alertname": "DiskFull", "namespace": "shop", "severity": "critical"}
    warn = {"alertname": "DiskFull", "namespace": "shop", "severity": "warning"}
    other_ns = {**warn, "namespace": "billing"}
    rules = CFG["inhibit_rules"]
    assert A.inhibited(warn, [crit, warn], rules)
    assert not A.inhibited(other_ns, [crit, other_ns], rules)
    assert not A.inhibited(crit, [crit], rules)


def test_business_hours_suppress_notifications_including_resolved():
    route = A.Route.from_dict(CFG["route"]).routes[2]
    intervals = {i["name"]: i["time_intervals"] for i in CFG["time_intervals"]}
    tue_noon = datetime(2024, 3, 5, 12, 0, tzinfo=timezone.utc)
    tue_night = datetime(2024, 3, 5, 22, 0, tzinfo=timezone.utc)
    saturday = datetime(2024, 3, 9, 12, 0, tzinfo=timezone.utc)
    assert A.should_notify(route, intervals, tue_noon)
    assert not A.should_notify(route, intervals, tue_night)
    assert not A.should_notify(route, intervals, saturday)


def test_a_missed_scrape_resets_for_unless_last_over_time_is_used():
    probe = [0, 0, 0, None, 0, 0, 0, 0]          # 0 = failing, None = scrape failed, no sample
    raw_truth = [None if v is None else v != 1 for v in probe]
    assert "firing" not in A.alert_states(raw_truth, for_steps=5)
    smoothed = A.last_over_time(probe, steps=5)
    assert A.alert_states([v != 1 for v in smoothed], for_steps=5)[-1] == "firing"


def test_shipped_rules_pass_the_linter_and_bad_rules_dont():
    assert A.lint_rules(RULES) == []
    bad = {"groups": [{"rules": [{"alert": "X", "expr": "probe_success", "for": "30s", "labels": {"severity": "page"},
                                  "annotations": {"summary": "x is {{ $labels.instance }}"}}, {"record": "foo", "expr": "up"}]}]}
    problems = A.lint_rules(bad)
    for needle in ("severity", "summary", "description", "runbook", "no comparison", "evaluation interval", "last_over_time", "level:metric"):
        assert any(needle in p for p in problems), needle


def test_ci_files_parse():
    wf = yaml.safe_load(open(os.path.join(HERE, "ci", "observability-ci.yml")))
    steps = [s.get("run", "") for j in wf["jobs"].values() for s in j["steps"]]
    assert any("promtool test rules" in s for s in steps) and any("amtool config routes test" in s for s in steps)
    ut = yaml.safe_load(open(os.path.join(HERE, "config", "unit-test.yml")))
    assert ut["rule_files"] == ["rules.yml"]
