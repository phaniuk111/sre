"""Alertmanager routing, grouping timers, inhibition and time intervals, plus Prometheus' `for` state
machine and a rule linter in the spirit of Pint. Behaviour follows the Alertmanager source, which
differs from two tables in the book (see the tests and README).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, time
from zoneinfo import ZoneInfo

# ───────────────────────────────────────────── matchers
MATCHER = re.compile(r'^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*(=~|!~|!=|=)\s*(.*?)\s*$')


def parse_matcher(s):
    name, op, val = MATCHER.match(s).groups()
    if len(val) >= 2 and val[0] == val[-1] == '"':
        val = val[1:-1]  # double quotes are optional; single quotes are kept literally
    return name, op, val


def matches(matchers, labels):
    for m in matchers:
        name, op, val = parse_matcher(m) if isinstance(m, str) else m
        have = labels.get(name, "")  # a missing label behaves like an empty one
        ok = {"=": have == val, "!=": have != val,
              "=~": re.fullmatch(val, have) is not None, "!~": re.fullmatch(val, have) is None}[op]
        if not ok:
            return False
    return True


# ───────────────────────────────────────────── routing
@dataclass
class Route:
    receiver: str = None
    matchers: list = field(default_factory=list)
    routes: list = field(default_factory=list)
    cont: bool = False
    group_by: list = None
    active_time_intervals: list = field(default_factory=list)
    mute_time_intervals: list = field(default_factory=list)

    @staticmethod
    def from_dict(d, parent=None):
        r = Route(receiver=d.get("receiver") or (parent.receiver if parent else None), matchers=d.get("matchers", []),
                  cont=d.get("continue", False), group_by=d.get("group_by") or (parent.group_by if parent else None),
                  active_time_intervals=d.get("active_time_intervals", []), mute_time_intervals=d.get("mute_time_intervals", []))
        r.routes = [Route.from_dict(c, r) for c in d.get("routes", [])]
        return r

    def match(self, labels):
        """Alertmanager's Route.Match: depth first; the first matching child wins unless it has
        continue: true; if no child matches, this route itself is the answer."""
        if not matches(self.matchers, labels):
            return []
        found = []
        for child in self.routes:
            got = child.match(labels)
            found += got
            if got and not child.cont:
                break
        return found or [self]


def receivers_for(config, labels):
    return [r.receiver for r in Route.from_dict(config["route"]).match(labels)]


# ───────────────────────────────────────────── grouping timers
def notification_times(arrivals, group_wait=30, group_interval=300, repeat_interval=4 * 3600, until=None):
    """Seconds at which one aggregation group notifies, given when alerts join it (all still firing).
    The first flush is group_wait after the first alert; the timer then restarts at every flush, so
    later flushes are group_interval apart and only happen when the group changed, or when
    repeat_interval has passed since the last notification."""
    arrivals = sorted(arrivals)
    until = until if until is not None else arrivals[-1] + 2 * group_interval
    t = arrivals[0] + group_wait
    sent, last_sent, seen = [], None, 0
    while t <= until:
        now = sum(1 for a in arrivals if a <= t)
        if now > seen or (last_sent is not None and t - last_sent >= repeat_interval):
            sent.append(t)
            last_sent, seen = t, now
        t += group_interval
    return sent


# ───────────────────────────────────────────── inhibition
def inhibited(alert, firing, rules):
    """An incoming (target) alert is muted if another firing (source) alert matches the source side
    and has equal values for every label in `equal`. An alert never inhibits itself."""
    for rule in rules:
        if not matches(rule["target_matchers"], alert):
            continue
        for src in firing:
            if src is alert or src == alert:
                continue
            if matches(rule["source_matchers"], src) and all(src.get(k, "") == alert.get(k, "") for k in rule.get("equal", [])):
                return True
    return False


# ───────────────────────────────────────────── time intervals
DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def _in_range(value, spec, names=None):
    for part in spec:
        lo, _, hi = str(part).lower().partition(":")
        hi = hi or lo
        conv = (lambda x: names.index(x)) if names else int
        if conv(lo) <= value <= conv(hi):
            return True
    return False


def in_interval(interval, when: datetime):
    """One time_intervals entry: every field present must match. Times are [start, end)."""
    local = when.astimezone(ZoneInfo(interval.get("location", "UTC")))
    if "weekdays" in interval and not _in_range(local.weekday(), interval["weekdays"], DAYS):
        return False
    if "times" in interval:
        t = local.time()
        if not any(time.fromisoformat(r["start_time"]) <= t < time.fromisoformat(r["end_time"]) for r in interval["times"]):
            return False
    return True


def should_notify(route: Route, intervals: dict, when: datetime):
    """Routing still happens outside active intervals; only the notification is suppressed.
    That includes the 'resolved' message, which surprises people after business hours."""
    if route.mute_time_intervals and any(in_interval(i, when) for n in route.mute_time_intervals for i in intervals[n]):
        return False
    if route.active_time_intervals:
        return any(in_interval(i, when) for n in route.active_time_intervals for i in intervals[n])
    return True


# ───────────────────────────────────────────── Prometheus `for` state machine
def alert_states(truth, for_steps):
    """truth: per evaluation, True/False/None (None = the query returned nothing, e.g. a failed
    scrape). Returns the state after each evaluation: inactive, pending or firing.
    Any evaluation without a result resets a pending alert."""
    states, run = [], 0
    for v in truth:
        run = run + 1 if v else 0
        states.append("inactive" if run == 0 else "firing" if run > for_steps else "pending")
    return states


def last_over_time(values, steps):
    """last_over_time(x[steps]): the newest non-missing value in the window, so one failed scrape
    doesn't make the expression vanish."""
    out = []
    for i in range(len(values)):
        win = [v for v in values[max(0, i - steps + 1): i + 1] if v is not None]
        out.append(win[-1] if win else None)
    return out


# ───────────────────────────────────────────── rule lint (Pint-style)
SUMMARY = re.compile(r"^[A-Z][^{.!?]+[^.!?]\.$")
DESCRIPTION = re.compile(r"^[A-Z{].*\{\{.*\}\}.*\.$", re.S)
DURATION = re.compile(r"^(\d+)([smhd])$")


def seconds(d):
    n, u = DURATION.match(d).groups()
    return int(n) * {"s": 1, "m": 60, "h": 3600, "d": 86400}[u]


def lint_rules(doc, evaluation_interval="1m"):
    """Checks the books recommend: severity label, one-sentence summary with no templates, a templated
    description, a runbook link, a comparison in the expression, `for` longer than the evaluation
    interval, warnings slow (>=15m) and criticals fast (<=15m), and _over_time for probe-style alerts."""
    problems = []
    for g in doc["groups"]:
        for r in g["rules"]:
            if "alert" not in r:
                if r["record"].count(":") < 2:
                    problems.append(f"{r['record']}: recording rule names should be level:metric:operations")
                continue
            a, lab, ann = r["alert"], r.get("labels", {}), r.get("annotations", {})
            sev = lab.get("severity")
            if sev not in ("critical", "warning", "info"):
                problems.append(f"{a}: severity must be critical, warning or info")
            if not SUMMARY.match(ann.get("summary", "")):
                problems.append(f"{a}: summary must be one sentence, capitalised, ending in a period, without templates")
            if not DESCRIPTION.match(ann.get("description", "")):
                problems.append(f"{a}: description must use at least one template and end in a period")
            if "runbook_url" not in ann:
                problems.append(f"{a}: add a runbook_url")
            if not re.search(r"(==|!=|>=|<=|[<>])\s*[-\d.(]|\bunless\b|\babsent", r["expr"]):
                problems.append(f"{a}: alert expression has no comparison")
            f = seconds(r.get("for", "0s"))
            if f and f < seconds(evaluation_interval):
                problems.append(f"{a}: for is shorter than the evaluation interval")
            if sev == "warning" and f < 900:
                problems.append(f"{a}: warnings should wait at least 15m")
            if sev == "critical" and f > 900:
                problems.append(f"{a}: criticals should fire within 15m")
            if "probe_success" in r["expr"] and "_over_time" not in r["expr"]:
                problems.append(f"{a}: wrap probe_success in last_over_time so a missed scrape doesn't reset `for`")
    return problems
