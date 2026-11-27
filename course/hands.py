# Hands-on tasks: one per lesson, each run against a POC in this repository.
# verify_hands.py runs every command and stores what it printed in hands_out.json;
# build.py shows that real output under "What you should see".
REPO = 'https://github.com/phaniuk111/sre/tree/main/'


def py(d, code):
    return f"cd {d}\npython - <<'EOF'\n{code.strip()}\nEOF"


T = {}


def task(key, d, title, mins, cmd, change, change_cmd, story, see=None, change_see=None, setup=None):
    """see / change_see: output typed in by hand, for commands that need the live lab running
    (verify_hands.py skips those; every other output is captured from a real run)."""
    T[key] = dict(key=key, dir=d, title=title, mins=mins, cmd=cmd.strip(), change=change, change_cmd=change_cmd.strip(), story=story,
                  see=see, change_see=change_see, setup=setup)


# ───────────────────────────────────────────────────────────── book 1: SRE
D = 'poc-01-slo-error-budget'
task('01', D, 'Derive every SLO number yourself', 10, py(D, '''
from slo.budget import ErrorBudget, burn_rate, burn_rate_for_consumption, time_to_exhaustion_hours
from slo.stats import min_failures_to_alert
from slo.composition import serial_availability
print("budget, 99.9% over 30 days (minutes):", round(ErrorBudget(0.999).allowed_downtime_minutes, 1))
print("burn rate that spends 2% in 1 h:", round(burn_rate_for_consumption(0.02, 1), 2))
print("burn rate that spends 5% in 6 h:", round(burn_rate_for_consumption(0.05, 6), 2))
print("burn rate at 0.8% errors, 99.9% SLO:", round(burn_rate(0.008, 0.999), 1))
print("hours until the budget is gone at 14.4x:", time_to_exhaustion_hours(14.4))
print("failures needed in 100 requests, 99% SLO:", min_failures_to_alert(100, 0.144))
print("five hard dependencies at 99.9% each:", round(serial_availability([0.999] * 5), 4))
'''),
     'Your SLO is 99.95% over a 28-day window. Before you run this, write down the fast-burn rate and the error rate that pages.',
     py(D, '''
from slo.budget import burn_rate_for_consumption
rate = burn_rate_for_consumption(0.02, 1, 28)
print("fast-burn rate over 28 days:", round(rate, 2))
print("error rate that pages at 99.95%:", f"{rate * 0.0005:.3%}")
'''),
     'I don’t quote 14.4, I derive it: 2% of a 30-day budget in one hour is 0.02 × 720. I’ve run the same sum for a 28-day window (13.44) and turned it into the error rate that pages for our SLO.')

D = 'poc-02-observability-otel'
task('02', D, 'Find the cohort that is failing', 10, py(D, '''
import random
from detectors.cohort_latency import build_baselines, outlier_fraction, is_regression
from detectors.failure_concentration import rank_cohorts
random.seed(7)
def synth(method, p50, n, slow=1.0):
    return [(method, random.lognormvariate(0, 0.3) * p50 * slow) for _ in range(n)]
base = build_baselines(synth("Login", 80, 5000) + synth("Report", 6000, 5000))
f = outlier_fraction(synth("Login", 80, 2000, slow=1.8) + synth("Report", 6000, 2000), base)
print("Login 1.8x slower -> outliers:", round(f, 3), "regression:", is_regression(f))
events = []
for _ in range(5000):
    lb = {"browser": random.choice(["chrome", "safari", "firefox"]), "user_type": random.choice(["consumer", "enterprise"])}
    bad = lb["browser"] == "firefox" and lb["user_type"] == "enterprise"
    events.append((lb, random.random() < (0.95 if bad else 0.001)))
name, gain, rate, size = rank_cohorts(events)[0]
print("failures concentrate in:", name, "| failure rate", round(rate, 2), "| requests", size)
'''),
     'A 144 ms login is still “fast”. Would one global p99 threshold of 2 seconds have caught the slowdown? Predict the share of requests over 2 s before and after.',
     py(D, '''
import random
random.seed(7)
def synth(method, p50, n, slow=1.0):
    return [(method, random.lognormvariate(0, 0.3) * p50 * slow) for _ in range(n)]
for label, slow in (("before", 1.0), ("after ", 1.8)):
    xs = synth("Login", 80, 2000, slow) + synth("Report", 6000, 2000)
    print(label, "share of requests over 2 s:", round(sum(v > 2000 for _, v in xs) / len(xs), 3))
'''),
     'A single latency threshold missed a login that got 1.8× slower, because reports dominate the tail. I compare each request type with its own baseline, and I rank label combinations by how much they explain the failures, which found “Firefox and enterprise” in one step.')

D = 'poc-03-incident-management'
task('03a', D, 'Measure your incident response', 10, f'cd {D}\npython incident_metrics.py examples/incidents.json',
     'Median time to mitigate is 15 minutes and to resolve is 146. Which one would you put on a dashboard for leadership, and what happens to both if one incident’s fix takes a day longer? Add a day to INC-101’s resolved time and rerun.',
     py(D, '''
import json
from incident_metrics import Incident, summarise
data = json.load(open("examples/incidents.json"))
data[0]["resolved"] = "2026-11-03T12:30:00Z"
s = summarise([Incident.from_dict(d) for d in data])
print("median minutes to mitigate:", s["median_ttm_min"], "| to resolve:", s["median_ttr_min"])
'''),
     'I track time to detect, mitigate and resolve separately, as medians. Mitigation is what customers feel, so that’s the headline. I also track the share of incidents found by a person and the share with no incident commander, because those show where the process is weak.')
task('03b', D, 'Write a blameless postmortem in 20 minutes', 20, f'cd {D}\ncat templates/postmortem-cast.md | head -40\npython incident_metrics.py examples/incidents.json | grep -E "manually|without_ic"',
     'Fill the template for INC-101 from examples/incidents.json. Keep every sentence about a person neutral: what they knew and saw, never “should have”. Then check which of your action items change the system and which only ask people to be careful.',
     f'cd {D}\ngrep -c "" templates/postmortem-cast.md\ngrep -n "^## " templates/postmortem-cast.md',
     'My postmortems follow the control structure: what each person or system knew, what feedback it had, and why the action made sense at the time. Action items change the system. “Be more careful” isn’t one.')
task('03c', D, 'Run STPA on a design before it ships', 20, f'cd {D}\ngrep -n "^## \\|^### " templates/stpa-worksheet.md\ncat playbooks/slo-burn.md | head -30',
     'Take a deploy pipeline: controller = the pipeline, controlled process = production. List four unsafe control actions, one of each kind: not given, given wrongly, too early or late, stopped too soon. The worksheet has the columns.',
     f'cd {D}\ngrep -n -i "unsafe control" -A 6 templates/stpa-worksheet.md | head -14',
     'For a risky design I list the control actions and ask four questions of each: what if it isn’t given, is given wrongly, at the wrong time, or stops too soon? That finds hazards with no component failure at all, like a rollback that is never triggered because the feedback is missing.')

D = 'poc-04-resilience-patterns'
task('04', D, 'Watch a retry storm, then stop it', 10, f'cd {D}\npython simulate_cascade.py',
     'The spike lasts 20 ticks, yet the naive service never recovers and does 7,950 units of wasted work. What is wasted work, and where does the extra load come from once the spike is over? Find the three protections in the code.',
     f'cd {D}\ngrep -n "shed now\\|RetryBudget(\\|AdaptiveThrottler(\\|trigger client retries" simulate_cascade.py',
     'I simulated a spike to 150% of capacity. Without protection, goodput fell to zero and stayed there after the spike, because the queue was full of requests whose callers had given up. With deadlines, load shedding and a 10% retry budget, the service kept serving at capacity and recovered on its own.')

D = 'poc-05-progressive-delivery'
task('05', D, 'Judge a canary with statistics', 10, py(D, '''
import random
from canary_analysis import ArmStats, judge
rng = random.Random(3)
def arm(n, err, p50, slow=1.0):
    return ArmStats(n, sum(rng.random() < err for _ in range(n)), [rng.lognormvariate(0, 0.4) * p50 * slow for _ in range(n)])
control = arm(50000, 0.001, 50)
print("healthy canary      :", judge(arm(5000, 0.001, 50), control))
print("2% errors           :", judge(arm(5000, 0.02, 50), control))
print("50% slower          :", judge(arm(5000, 0.001, 50, slow=1.5), control))
print("only 20 requests    :", judge(arm(20, 0.0, 50), control))
'''),
     'The canary took 20 requests with zero errors. Is that a pass? Predict the verdict for 20, 200 and 2,000 requests, all healthy.',
     py(D, '''
import random
from canary_analysis import ArmStats, judge
rng = random.Random(3)
def arm(n, err, p50):
    return ArmStats(n, sum(rng.random() < err for _ in range(n)), [rng.lognormvariate(0, 0.4) * p50 for _ in range(n)])
control = arm(50000, 0.001, 50)
for n in (20, 200, 2000):
    print(n, "requests:", judge(arm(n, 0.0, 50), control))
'''),
     'My canary gate compares the canary with a control running at the same time, with a significance test for errors and for latency. Too little traffic is “inconclusive”, never a pass, so a quiet canary can’t promote itself.')

D = 'poc-06-chaos-fis'
task('06', D, 'Prove an AZ-loss test actually tested something', 10, py(D, '''
from verify_experiment import verify_az_loss
def series(before, during, after): return [before] * 10 + [during] * 10 + [after] * 5
runs = {
  "fault worked, load moved": ({"a": series(100, 0, 100), "b": series(100, 150, 100), "c": series(100, 150, 100)}, [0] * 25),
  "fault never took effect": ({"a": series(100, 100, 100), "b": series(100, 100, 100), "c": series(100, 100, 100)}, [0] * 25),
  "users were hurt":         ({"a": series(100, 0, 100), "b": series(100, 100, 100), "c": series(100, 100, 100)}, [0] * 10 + [20] * 10 + [0] * 5),
}
for name, (per_az, errors) in runs.items():
    r = verify_az_loss(per_az, errors=errors, fault_az="a", fault_start=10, fault_end=20)
    print(f"{name:26}", r["verdict"], "| fault took effect:", r["fault_took_effect"], "| load absorbed:", r["load_absorbed"])
'''),
     'An experiment finished with zero errors. Why is that not enough to call it a pass? Check the second run above, then read the first three entries of the test catalogue.',
     f'cd {D}\ngrep -n "x:\\|y:\\|z:" dirt-catalog.yaml | head -9',
     'A chaos test with no errors proves nothing unless the fault really happened. Mine checks three things: traffic to the failed zone dropped to zero, the other zones absorbed it, and the SLI stayed inside the SLO. Each test is written as “X is resilient to Y, measured by Z”.')

D = 'poc-07-capacity-planning'
task('07', D, 'Size a service for N+1 across zones', 10, py(D, '''
from capacity import plan_supply, redundancy_overhead, sum_of_peaks, peak_of_sums
plan = plan_supply(peak_demand_qps=9000, qps_per_instance=100, failure_domains=3, target_utilisation=0.7)
print(plan)
print("capacity left after losing one zone:", plan.per_domain * (plan.domains - 1) * 100, "qps")
print("extra capacity for N+1 with 3 zones:", redundancy_overhead(3), "| with 6:", redundancy_overhead(6))
s = {"eu": [10, 80, 30, 10], "us": [10, 20, 80, 30], "ap": [80, 30, 10, 10]}
print("sum of peaks:", sum_of_peaks(s), "| peak of sums:", peak_of_sums(s))
'''),
     'Peak is 9,000 qps and one instance serves 100. A colleague says “90 instances”. Predict the real number for 3 zones at 70% target utilisation, and for 2 zones.',
     py(D, '''
from capacity import plan_supply
for domains in (3, 2):
    p = plan_supply(9000, 100, domains, 0.7)
    print(domains, "zones ->", p.total, "instances,", p.per_domain, "per zone, running at", f"{p.utilisation_at_peak:.0%}", "at peak")
'''),
     'I size for the peak at target utilisation with one failure domain lost: 9,000 qps needs 195 instances across three zones, not 90, and each runs at 46% on a normal day. More zones make redundancy cheaper: 50% extra with three, 20% with six.')

D = 'poc-08-data-resilience'
task('08', D, 'Check backups against RPO, and whether restores are tested', 10, f'cd {D}\npython backup_slo.py',
     'Two of three data sources meet the RPO objective, and the catalogue database has backups but appears under “untested or slow restores”. Which is the bigger risk, and what would you tell the team that owns it?',
     py(D, '''
import backup_slo as B
for s in B.load_sample("examples/recovery_points.json"):
    rpo, rto, _ = B.TIER_OBJECTIVES[s.tier]
    tests = [int(d.total_seconds() / 60) for d in s.restore_durations]
    print(s.arn.split(":")[-1], "|", s.tier, "| RPO", rpo, "| RTO", rto, "| recovery points:", len(s.recovery_points), "| restore tests (minutes):", tests)
'''),
     'I report backups as an SLO: the share of hours in which the newest recovery point was inside the RPO, per data source. And a backup only counts once a restore has been tested inside the RTO. In my sample fleet one database had perfect backups and no tested restore, which is the one I’d fix first.')

D = 'poc-09-toil-automation'
task('09', D, 'Rank toil by the hours it costs', 10, f'cd {D}\npython toil_report.py examples/tickets.csv > /tmp/toil.txt\nhead -22 /tmp/toil.txt',
     'The noisiest ticket class (120 tickets) isn’t the most expensive one. Which class would you automate first, and why? Then find the share of tickets that needed no action at all.',
     f'cd {D}\npython toil_report.py examples/tickets.csv | grep -E "unactionable|ops_load"\nhead -3 examples/tickets.csv\ngrep -c "false" examples/tickets.csv',
     'I rank toil by hours, not ticket count: restarting a stuck worker cost 25 hours across 60 tickets, more than a flappy alert with twice as many. More than half the tickets needed no action, so the first fix was deleting alerts, before automating anything.')

D = 'poc-10-platform-policy'
task('10', D, 'Run production-readiness as code', 10, f'cd {D}\npython policy_check.py examples/catalog.yaml examples/exemptions.yaml; echo "exit code: $?"',
     'legacy-billing has an exemption for single-AZ, but it is still blocked on progressive release. Why? Look at the exemptions file for the answer.',
     f'cd {D}\ncat examples/exemptions.yaml',
     'Our readiness rules are checks against a service catalogue: an SLO exists, alerts route to a team that exists, releases are progressive. Exemptions are allowed, but they carry an owner, a reason and an expiry date, and an expired one blocks again.')

D = 'poc-11-ai-ops-guardrails'
task('11', D, 'Let an agent act, within limits it has earned', 10, py(D, '''
from agent_guardrails import Guardrails, IrreversibleDelete, Level, Proposal, RollbackLambdaAlias, TrackRecord, ZonalShift, earned_level
for rec in (TrackRecord(), TrackRecord(19, 1), TrackRecord(995, 5)):
    print(rec.total, "past runs ->", earned_level(rec, Level.L4_FULL).name)
ev = ["5xx up 30x since deploy 42", "only version 7 errors"]
g = Guardrails(records={"bad-deploy": TrackRecord(30, 1), "az": TrackRecord(500, 0), "x": TrackRecord(5000, 0)}, ceilings={"x": Level.L4_FULL})
p = Proposal("bad-deploy", RollbackLambdaAlias("checkout", "live", "6", "7"), "rollback", ev, 0.9)
print("30 runs, no human  :", g.execute(p, validate=lambda: True))
print("30 runs, approved  :", g.execute(p, validate=lambda: True, human_approves=lambda *_: True))
print("500 runs, bad fix  :", g.execute(Proposal("az", ZonalShift("alb-arn", "euw2-az1"), "AZ errors", ev, 0.95), validate=lambda: False))
print("irreversible action:", g.execute(Proposal("x", IrreversibleDelete(), "free space", ev, 0.99), lambda: True))
'''),
     'Something is going wrong and you want every agent action stopped now. Predict what the kill switch does to an agent with 5,000 clean runs, and whether the refusal is recorded.',
     py(D, '''
from agent_guardrails import Guardrails, Level, Proposal, TrackRecord, ZonalShift
g = Guardrails(records={"x": TrackRecord(5000, 0)}, ceilings={"x": Level.L4_FULL})
g.kill_switch = True
print(g.execute(Proposal("x", ZonalShift("a", "b"), "r", ["evidence"], 0.99), lambda: True))
print("audit entries:", len(g.audit))
'''),
     'My rule for AI in operations: autonomy is earned per scenario from a track record and capped by policy. Every action needs evidence, a dry run, a validation step and an undo. Irreversible actions are refused at any level, there’s a kill switch, and everything is audited.')

# ───────────────────────────────────────────────────────────── book 2: platform engineering
D = 'poc-12-coupling-discovery'
task('12', D, 'Find hidden coupling from evidence', 10, py(D, '''
import json
from coupling_discovery import analyse
report = analyse(json.load(open("examples/evidence.json")))
for finding, detail in report.items():
    print(f"{finding:26}", json.dumps(detail)[:150])
'''),
     'Two services write the same orders table. Predict their independent release rate (how often one deploys without the other), then check it.',
     py(D, '''
import json
from coupling_discovery import co_deployed, independent_release_rate
deploys = json.load(open("examples/evidence.json"))["deploys"]
print("independent release rate:", independent_release_rate(deploys))
print("deployed together:", co_deployed(deploys))
'''),
     'I look for coupling in evidence, not diagrams: two writers on one table, services that always deploy together, a queue with no schema, call cycles in traces. The number I track is the independent release rate. If it’s low, the “microservices” are one system.')

D = 'poc-13-safe-coding'
task('13', D, 'Make SQL injection impossible, then prove it', 10, f'cd {D}\npython conformance.py examples; echo "exit code: $?"\npython conformance.py examples/safe.py safedb; echo "exit code: $?"',
     'sneaky.py uses the safe database wrapper but builds SQL with an f-string. Does the checker catch it? Read the three lines it flagged.',
     f'cd {D}\nsed -n 4,15p examples/sneaky.py',
     'Rather than train every developer to avoid injection, the platform owns a safe API where queries must be string literals and values are parameters. A conformance check in CI fails the build if anyone imports the raw driver or builds SQL from a variable. The bug class can’t be written.')

D = 'poc-14-supply-chain-gate'
task('14', D, 'Gate a deploy on signed evidence', 10, py(D, '''
from datetime import datetime, timezone
from gate import attest, evaluate
NOW = datetime(2026, 11, 21, 12, 0, tzinfo=timezone.utc)
KEYS = {"codebuild-prod": b"k-build", "review-system": b"k-review", "inspector": b"k-scan", "laptop": b"k-laptop"}
TRUST = {k: v for k, v in KEYS.items() if k != "laptop"}
POLICY = {"trusted_builders": ["codebuild-prod"], "source_repo": "github.com/acme/orders", "min_slsa_build_level": 3,
          "min_approvals": 1, "max_scan_age_hours": 24, "bad_changes": ["c0ffee1"]}
D = "sha256:1111"
def atts(builder="codebuild-prod", approvers=("bea",), critical=0, commits=("abc1234",)):
    return [attest("provenance", D, {"source_repo": "github.com/acme/orders", "commits": list(commits), "slsa_build_level": 3}, builder, KEYS[builder]),
            attest("review", D, {"author": "amir", "approvers": list(approvers)}, "review-system", KEYS["review-system"]),
            attest("scan", D, {"critical": critical, "scanned_at": "2026-11-21T06:00:00+00:00"}, "inspector", KEYS["inspector"])]
cases = {"all evidence present": atts(), "built on a laptop": atts(builder="laptop"), "author approved own change": atts(approvers=("amir",)),
         "2 critical findings": atts(critical=2), "contains a known-bad commit": atts(commits=("abc1234", "c0ffee1"))}
for name, a in cases.items():
    r = evaluate(D, a, POLICY, TRUST, NOW)
    print(f"{name:28}", r["decision"], r["reasons"])
'''),
     'It is 3 a.m., production is down, and the fix can’t get a second reviewer. Should the gate let it through? Predict what break-glass needs, then run it with and without an incident number.',
     py(D, '''
from datetime import datetime, timezone
from gate import attest, evaluate
NOW = datetime(2026, 11, 21, 12, 0, tzinfo=timezone.utc)
K = {"codebuild-prod": b"k-build", "review-system": b"k-review", "inspector": b"k-scan"}
P = {"trusted_builders": ["codebuild-prod"], "source_repo": "github.com/acme/orders", "min_slsa_build_level": 3, "min_approvals": 1, "max_scan_age_hours": 24, "bad_changes": []}
D = "sha256:1111"
a = [attest("provenance", D, {"source_repo": "github.com/acme/orders", "commits": ["abc"], "slsa_build_level": 3}, "codebuild-prod", K["codebuild-prod"]),
     attest("review", D, {"author": "amir", "approvers": []}, "review-system", K["review-system"]),
     attest("scan", D, {"critical": 0, "scanned_at": "2026-11-21T06:00:00+00:00"}, "inspector", K["inspector"])]
for bg in ({"who": "amir"}, {"who": "amir", "incident": "INC-204", "reason": "checkout down, fix reviewed verbally"}):
    r = evaluate(D, a, P, K, NOW, break_glass=bg)
    print(r["decision"], "|", r["reasons"], "| audit:", bool(r.get("audit")))
'''),
     'My deploy gate trusts signed attestations, not people’s word: provenance from the trusted builder, a review by someone other than the author, a recent scan. Break-glass exists for emergencies, but it needs a name, an incident and a reason, it is logged loudly, and it can’t override a known-bad change.')

D = 'poc-15-safe-deployment'
task('15', D, 'Give teams a blueprint they can’t weaken', 10, py(D, '''
from blueprints import render, conformance, latest
cfg = render("external-web-service", 3, {"runtime.memory_limit": "1Gi"})
print("rendered:", cfg["tls"], cfg["runtime"])
for bad in ({"runtime.run_as_root": True}, {"placement.zones": 1}):
    try:
        render("external-web-service", 3, bad)
    except ValueError as e:
        print("refused :", e)
cfg["network"]["public_ingress"] = "open"
cfg["observability"]["tracing"] = False
for f in conformance("orders", cfg):
    print("drift   :", f[0], "-", f[2])
'''),
     'A team is still on version 2 of the blueprint. Is that a block or a warning? Decide, then check.',
     py(D, '''
from blueprints import render, conformance, latest
print("latest version:", latest("external-web-service"))
print(conformance("legacy", render("external-web-service", 2)))
'''),
     'Teams get a versioned blueprint with a few parameters. Security invariants like TLS 1.3 and no root are locked, so they can’t be set wrong. A conformance check compares what’s running with the blueprint, which catches hand edits after deploy and services left on old versions.')

D = 'poc-16-risk-profile-rollouts'
task('16', D, 'Let the error budget set the rollout speed', 10, f'cd {D}\npython risk_profile.py | cut -c1-200',
     'A tier-1 service has 10% of its budget left. Predict how the rollout plan changes compared with 90% left, and what happens when the budget is overspent.',
     py(D, '''
from risk_profile import rollout_plan
for left in (0.9, 0.1, -0.2):
    p = rollout_plan(1, left)
    print(f"budget left {left:+.0%}: bake {p['bake_minutes']} min, minimum {p['minimum_minutes']} min, allowed: {p['allowed']}", p["notes"])
'''),
     'Rollout policy comes from the service’s tier and its remaining error budget. A tier-1 service always gets staged rollout with canary analysis. With little budget left the bake time doubles, and once the budget is spent only fixes ship. The platform applies this, so teams don’t negotiate it per release.')

D = 'poc-17-efficiency-apm'
task('17', D, 'Tell growth from a regression', 10, f'cd {D}\npython apm.py examples/fleet.json',
     'Two services both use 20% more CPU this month. One is fine and one is a regression. What single extra number tells them apart?',
     py(D, '''
from apm import productivity, classify
before = {"cpu_seconds": 1000, "work": 5000}
print("same work, 20% more CPU:", classify(before, {"cpu_seconds": 1200, "work": 5000}))
print("20% more work and CPU  :", classify(before, {"cpu_seconds": 1200, "work": 6000}))
'''),
     'CPU going up says nothing by itself. I divide useful work by CPU seconds: if work grew 20% too, that’s growth; if work is flat, it’s a regression. The work metric has to track real output, so I check it correlates with CPU before trusting it.')

D = 'poc-18-platform-scorecard'
task('18a', D, 'Score a platform from the user’s side', 10, f'cd {D}\npython scorecard.py examples/platform.json',
     'Adoption is 60% and the platform’s SLO is met, so is it healthy? Find the headline the scorecard gives and the two numbers behind it.',
     f'cd {D}\npython scorecard.py examples/platform.json | grep -E "ttfhw|first_attempt|headline|lead_time_ratio"',
     'I measure a platform three ways: users (adoption, retention, time to first hello-world), the system (SLO, cost per service) and the business (delivery metrics on and off the platform). In my example the SLO was met but only two-thirds of teams succeeded first time, so the roadmap item was onboarding.')
task('18b', D, 'Retire a service without surprising anyone', 10, py(D, '''
from datetime import date
from scorecard import brownout_plan
callers = {"billing": "2026-11-18", "reports": "2026-11-02", "old-cron": "2026-06-30"}
plan = brownout_plan(callers, today=date(2026, 11, 21), off_date=date(2027, 3, 1))
print("contact now  :", plan["contact_now"])
print("probably gone:", plan["probably_gone"])
for b in plan["brownouts"]:
    print("brownout     :", b["date"], b["duration"])
print("switch off   :", plan["off"])
'''),
     'Every caller in the logs was last seen five months ago. Can you skip the brownouts and switch off today? Predict what the plan says.',
     py(D, '''
from datetime import date
from scorecard import brownout_plan
plan = brownout_plan({"old-cron": "2026-06-30", "legacy-report": "2026-05-12"}, today=date(2026, 11, 21), off_date=date(2027, 3, 1))
print("contact now:", plan["contact_now"], "| probably gone:", plan["probably_gone"])
print("brownouts still planned:", [b["duration"] for b in plan["brownouts"]])
'''),
     'To retire a service I find the real callers in access logs, contact the recent ones, then run brownouts of increasing length before the date: five minutes, an hour, eight hours, a day. A short planned outage finds the callers who ignored the emails while it’s still cheap.')

D = 'poc-19-ai-platform-signals'
task('19', D, 'Page on a model that is up but wrong', 10, py(D, '''
from ai_signals import psi, drift_status, confidence_gate, model_slo
EDGES = [50, 100, 250, 500]
TRAIN = [20] * 20 + [80] * 30 + [180] * 30 + [400] * 20
for name, live in (("similar traffic", [25] * 22 + [75] * 28 + [200] * 31 + [450] * 19), ("wave of $5,000 payments", [80] * 20 + [180] * 20 + [400] * 10 + [5000] * 50)):
    s = psi(TRAIN, live, EDGES)
    print(f"{name:24} PSI {s:.2f} -> {drift_status(s)}")
ok = {"available": True, "latency_ok": True, "fresh": True, "drift": "stable", "quality_ok": True}
print("all green        :", model_slo(ok))
print("API up, drifted  :", model_slo({**ok, "drift": "drifted"}))
print("API down         :", model_slo({**ok, "available": False}))
'''),
     'A fraud model answers every request in 40 ms with HTTP 200. 12% of its answers are wrong. Predict the error rate if it only answers when its confidence is at least 0.7, and what that costs.',
     py(D, '''
from ai_signals import confidence_gate
preds = ([{"confidence": 0.95, "correct": True}] * 80 + [{"confidence": 0.9, "correct": False}] * 2
         + [{"confidence": 0.5, "correct": True}] * 8 + [{"confidence": 0.4, "correct": False}] * 10)
print(confidence_gate(preds, threshold=0.7))
'''),
     'For an ML service, availability and latency aren’t enough: it can be up and wrong. I add freshness, input drift and a quality signal to the SLO, and treat “up but drifted” as a page. A confidence gate trades a little availability for correctness: answering 82% of requests cut errors from 12% to 2.4%.')

# ───────────────────────────────────────────────────────────── book 3: Prometheus
D = 'poc-20-promql-semantics'
task('20a', D, 'rate, increase and irate on the same samples', 10, py(D, '''
import promql as P
samples = [(15, 100), (30, 110), (45, 170), (60, 180)]      # (seconds, counter value), scraped every 15 s
print("increase[1m]:", round(P.increase(samples, 60, 60), 2))
print("rate[1m]    :", round(P.rate(samples, 60, 60), 3), "per second")
print("irate[1m]   :", round(P.irate(samples, 60, 60), 3), "per second")
restart = [(0, 0), (15, 15), (30, 30), (45, 45), (60, 5), (75, 20)]   # the pod restarted after t=45
print("increase[2m] across a restart:", P.increase(restart, 75, 120), "= 45 before the restart + 20 after")
'''),
     'The counter rose by 80 between the first and last sample, yet increase says 106.67. Work out why on paper (80 × 60 ÷ 45), then predict irate 15 seconds earlier, at t = 45.',
     py(D, '''
import promql as P
samples = [(15, 100), (30, 110), (45, 170), (60, 180)]
print("irate at t=45:", round(P.irate(samples[:3], 45, 60), 3), "per second  <- the spike")
print("irate at t=60:", round(P.irate(samples, 60, 60), 3), "per second  <- already gone")
print("rate  at t=60:", round(P.rate(samples, 60, 60), 3), "per second  <- spike averaged in")
'''),
     'rate is the per-second average over the window and handles counter resets; increase is the same number times the window, so it can be fractional; irate uses only the last two samples. I use rate in alerts and recording rules and keep irate for zoomed-in graphs, because it forgets a spike 15 seconds later.')
task('20b', D, 'Histogram quantiles and vector matching', 10, py(D, '''
import promql as P
buckets = [(0.1, 600), (0.5, 900), (1.0, 980), (2.0, 995), (float("inf"), 1000)]   # (le, cumulative count)
for q in (0.5, 0.95, 0.99):
    print(f"p{int(q * 100)} =", round(P.histogram_quantile(q, buckets), 3), "s")
errs = [({"job": "api", "code": "500"}, 5.0), ({"job": "web", "code": "500"}, 1.0)]
total = [({"job": "api"}, 100.0), ({"job": "web"}, 50.0)]
for labels, v in P.binop("/", errs, total, on=["job"]):
    print("error ratio", labels, round(v, 3))
'''),
     'The p99 comes out as 1.67 s, but no request was measured at 1.67 s. Where does that number come from, and what would p99 be if the 2-second bucket did not exist?',
     py(D, '''
import promql as P
print("with a 2 s bucket   :", round(P.histogram_quantile(0.99, [(0.1, 600), (0.5, 900), (1.0, 980), (2.0, 995), (float("inf"), 1000)]), 3))
print("without a 2 s bucket:", round(P.histogram_quantile(0.99, [(0.1, 600), (0.5, 900), (1.0, 980), (float("inf"), 1000)]), 3))
'''),
     'histogram_quantile interpolates inside a bucket, so the answer is only as good as the bucket boundaries. If the quantile lands in the +Inf bucket it returns the highest finite boundary. So I put a boundary exactly at the SLO threshold and measure the SLO as a ratio of bucket counts, not as a percentile.')

D = 'poc-21-tsdb-internals'
task('21a', D, 'See what makes a sample cheap or expensive to store', 10, py(D, '''
import random, tsdb as T
N = 120                                   # one 30-minute chunk at 15 s
clean = [i * 15000 for i in range(N)]
vals = [float(i // 10) for i in range(N)]
print("bits for 120 regular timestamps:", T.timestamp_bits(clean))
print("bits for 120 constant values   :", T.value_bits([1.0] * N))
print("bytes per sample, regular scrapes:", round(T.bytes_per_sample(clean, vals), 2))
rnd = random.Random(7)
jittery = [t + rnd.randint(-30, 30) for t in clean]
print("bytes per sample, 30 ms jitter   :", round(T.bytes_per_sample(jittery, vals), 2))
print("compaction block ranges for 15 days:", T.compaction_ranges(15))
'''),
     'Scrape timestamps that wobble by ±30 ms more than double the disk used. Predict what happens if Prometheus snaps timestamps to the interval with a 60 ms tolerance.',
     py(D, '''
import random, tsdb as T
N = 120; clean = [i * 15000 for i in range(N)]; vals = [float(i // 10) for i in range(N)]
rnd = random.Random(7); jittery = [t + rnd.randint(-30, 30) for t in clean]
fixed = T.snap_timestamps(jittery, 15000, tolerance_ms=60)
print("jittery:", round(T.bytes_per_sample(jittery, vals), 2), "| snapped:", round(T.bytes_per_sample(fixed, vals), 2), "| aligned:", T.jitter_report(fixed, 15000)["aligned"])
'''),
     'Prometheus stores the change in the gap between timestamps and the XOR of each value with the last one. Regular scrapes and slow-moving values cost about a bit each, which is how it averages 1–2 bytes a sample in production. That’s also why jittery scrape timing costs disk: in my test it took a sample from 0.5 to 2.3 bytes.')
task('21b', D, 'Find the label that is blowing up cardinality', 10, py(D, '''
import tsdb as T
expo = "\\n".join(f'http_requests_total{{env="production",path="/user/{u}",code="200"}} 1' for u in range(50)) + '\\nup{env="production",job="api"} 1\\n'
r = T.cardinality_report(T.parse_exposition(expo))
print("series:", r["series"])
print("values per label:", r["label_value_counts"])
print("series per metric:", r["series_by_metric"])
print("same on every series:", r["everywhere"])
'''),
     'One endpoint puts the user ID in the path label. Predict how many series a sample_limit of 20 would let this scrape keep.',
     py(D, '''
import tsdb as T
expo = "\\n".join(f'http_requests_total{{path="/user/{u}"}} 1' for u in range(50)) + "\\n"
print(T.apply_limits(T.parse_exposition(expo), sample_limit=20))
'''),
     'Cardinality is the bill: every label value combination is a series. I look for the label with the most values, usually an ID in a path, and fix it at the source or drop it with relabeling. A sample_limit fails the whole scrape, not just the extra series, which is the point: it makes the problem loud.')

D = 'poc-22-relabel-discovery-sharding'
task('22a', D, 'Turn discovered EC2 instances into scrape targets', 10, py(D, '''
import relabel as R
fleet = [
 {"id": "i-1", "private_ip": "10.0.1.10", "az": "eu-west-2a", "state": "running", "type": "m7g.large", "tags": {"Name": "web1", "Service": "web", "Monitoring": "true", "Team": "checkout"}},
 {"id": "i-3", "private_ip": "10.0.3.12", "az": "eu-west-2c", "state": "stopped", "type": "t4g.small", "tags": {"Name": "old", "Service": "web", "Monitoring": "true"}},
 {"id": "i-4", "private_ip": "10.0.1.13", "az": "eu-west-2a", "state": "running", "type": "t4g.small", "tags": {"Name": "bastion", "Service": "ops"}},
]
print("before relabeling:", sorted(R.ec2_discovery(fleet[:1], 9100)[0])[:6], "...")
for t in R.discover(fleet):
    print("target:", t["address"], t["labels"])
print("anchored regex, 'running-ish' kept?", R.relabel({"x": "running-ish"}, [{"source_labels": ["x"], "regex": "running", "action": "keep"}]))
'''),
     'Three instances were discovered and one became a target. Say why each of the other two was dropped before you look at the relabel rules.',
     f'cd {D}\ngrep -n "source_labels" -A 2 prometheus-ec2.yml | head -12',
     'Service discovery gives every target a pile of __meta labels; relabel rules decide which targets to keep and which labels to copy. I keep running instances tagged for monitoring, connect by private IP and label by name. Regexes are anchored, so “running” doesn’t match “running-ish”.')
task('22b', D, 'Shard scrapes across Prometheus servers', 10, py(D, '''
import relabel as R
few = [f"10.0.0.{i}:9100" for i in range(24)]
many = [f"10.0.{i // 250}.{i % 250}:9100" for i in range(2000)]
print("24 targets on 2 shards  :", dict(R.balance(few, 2)))
print("2000 targets on 2 shards:", dict(R.balance(many, 2)))
print("share of targets that move going from 2 to 3 shards:", round(R.moved_when_resharding(many, 2, 3), 2))
print("relabel rule for shard 0 of 2:", R.shard_config(2, 0))
'''),
     'You add a third shard. Predict the share of targets that move to a different server, and what that does to rate() on those targets for the next few minutes.',
     py(D, '''
import relabel as R
many = [f"10.0.{i // 250}.{i % 250}:9100" for i in range(2000)]
for a, b in ((2, 3), (2, 4), (3, 4)):
    print(f"{a} -> {b} shards: {R.moved_when_resharding(many, a, b):.0%} of targets move")
'''),
     'I shard with hashmod on the target address: each server keeps the targets whose hash matches its index. It balances well with many targets and poorly with few. Changing the shard count moves most targets, so I plan it, and I keep a global view with Thanos or remote write.')

D = 'poc-23-alert-routing-and-rule-ci'
task('23a', D, 'Trace an alert through the routing tree', 10, py(D, '''
import yaml, alerting as A
cfg = yaml.safe_load(open("config/alertmanager.yml"))
for labels in ({"environment": "production", "team": "devops"}, {"environment": "testing", "team": "devops"}, {"environment": "production", "team": "sre"}):
    print(labels, "->", A.receivers_for(cfg, labels))
print("alerts arriving at 0 s, 17 s and 35 s are sent at:", A.notification_times([0, 17, 35], until=900), "seconds")
'''),
     'Three alerts for one group arrive at 0, 17 and 35 seconds with group_wait 30 s and group_interval 5 m. Predict when notifications go out. Then say what a second identical alert at 400 s would do.',
     py(D, '''
import alerting as A
print("0, 17, 35       ->", A.notification_times([0, 17, 35], until=900))
print("0, 17, 35, 400  ->", A.notification_times([0, 17, 35, 400], until=900))
print("single quotes are literal:", A.matches(["environment = 'production'"], {"environment": "production"}))
'''),
     'An alert walks the routing tree and stops at the first matching child unless continue is set. group_wait batches the first notification, group_interval spaces updates to a group, repeat_interval re-sends unchanged alerts. I test routes with amtool before deploying, because a wrong matcher fails silently.')
task('23b', D, 'Test alert rules in CI before they page anyone', 10, f'cd {D}\nsed -n 1,30p config/unit-test.yml\npython -m pytest -q 2>&1 | tail -1',
     'Break a rule on purpose: change the for: duration in config/rules.yml from the tested value and predict which check fails, promtool check or promtool test.',
     f'cd {D}\ngrep -n "for:\\|alert:" config/rules.yml | head -8\nls ci',
     'Alert rules are code, so they go through CI: promtool check for syntax, a linter for missing severity labels and runbooks, and promtool unit tests that feed in a series and assert when the alert fires and with which labels. Alertmanager routes get the same treatment with amtool.')

D = 'poc-24-slo-burn-rate-rules'
task('24', D, 'Generate burn-rate rules and replay an outage', 10, py(D, '''
import generate as G
print("budget minutes at 99.9%:", round(G.downtime_minutes(99.9), 1), "| page pairs:", G.PAGE, "| ticket pairs:", G.TICKET)
tot = [600.0] * 600; err = [0.0] * 600
for i in range(300, 330): err[i] = tot[i]                # a 30-minute total outage starting at minute 300
fired = G.simulate(err, tot, 99.9, G.PAGE)
after_fix = lambda f: len(f) - 1 - f[::-1].index(True) - 329
print("the page fires in minute", fired.index(True) - 300 + 1, "of the outage")
print("14.4x rule (1 h and 5 m) clears", after_fix(G.simulate(err, tot, 99.9, G.PAGE[:1])), "minutes after the fix; 6x rule (6 h and 30 m) clears after", after_fix(fired))
slow = [t * 0.004 for t in tot * 10]                      # 0.4% errors for 100 hours: a 4x burn
print("4x burn pages:", any(G.simulate(slow, tot * 10, 99.9, G.PAGE)), "| tickets:", any(G.simulate(slow, tot * 10, 99.9, G.TICKET)))
'''),
     'Remove the short window: page on the 1-hour window alone. Predict how long the page keeps firing after the outage is fixed.',
     py(D, '''
import generate as G
tot = [600.0] * 600; err = [0.0] * 600
for i in range(300, 330): err[i] = tot[i]
b = G.budget(99.9)
long_only = [G.error_ratio(err, tot, i, 60) > 14.4 * b for i in range(600)]
both = G.simulate(err, tot, 99.9, G.PAGE[:1])
last = lambda f: len(f) - 1 - f[::-1].index(True) - 329
print("1 h window alone: still firing", last(long_only), "minutes after the fix")
print("1 h and 5 m     : clears", last(both), "minutes after the fix")
'''),
     'I generate the recording and alerting rules from one SLO file, so every service gets the same windows. I replayed a 30-minute outage against them: the page fired in the first minute, and the 14.4× rule cleared four minutes after the fix because of its 5-minute window. With the 1-hour window alone it kept firing for 59 minutes.')

D = 'poc-25-remote-write-and-thanos'
task('25a', D, 'Size remote write for your ingestion rate', 10, py(D, '''
import longterm as L
for rate in (10_000, 250_000, 1_000_000):
    p = L.remote_write_plan(rate)
    print(f"{rate:>9,} samples/s -> min shards {p['min_shards']}, rides out {p['tolerated_outage_hours']} h, warnings: {p['warnings']}")
print("retry backoff (s):", L.backoff_schedule()[:6], "... max", L.backoff_schedule()[-1])
'''),
     'The remote store is down for three hours. Predict what Prometheus has lost when it comes back, given the default settings above.',
     py(D, '''
import longterm as L
for hours in (2.0, 4.0):
    ok = L.remote_write_plan(250_000, wal_hours=hours)["tolerated_outage_hours"]
    print("WAL kept for", hours, "h -> a 3-hour outage loses about", max(0.0, 3 - ok), "h of samples")
'''),
     'Remote write reads from the write-ahead log, so it survives a remote outage for as long as the WAL is kept, about two hours by default. After that, data is lost. I size shards from the ingestion rate, and I alert on the remote-write lag, not just on failures.')
task('25b', D, 'Deduplicate two Prometheus replicas', 10, py(D, '''
import longterm as L
a = [(t, 1.0) for t in range(0, 600, 15) if not 120 <= t < 300]      # replica A restarts for 3 minutes
b = [(t, 1.0) for t in range(0, 600, 15) if t not in (45, 60)]       # replica B misses two scrapes
out = L.dedup_thanos({"a": a, "b": b})
print("Thanos query-time dedup: samples", len(out), "of 40 | gaps:", sorted(set(range(0, 600, 15)) - {t for t, _, _ in out}))
got = L.dedup_mimir({"a": {t for t, _ in a}, "b": {t for t, _ in b}}, "a", failover_after=30, now_series=list(range(0, 600, 15)))
print("Mimir HA tracker       : samples", len(got), "of 40 (waits 30 s before switching replica)")
print("downsampling kept at 50 days:", L.downsample_plan(24 * 50), "| write quorum with 3 replicas:", L.write_quorum(3))
'''),
     'You add a fourth store node. Predict the share of series that move with plain hashmod and with a consistent-hash ring.',
     py(D, '''
import longterm as L
series = [f"series-{i}" for i in range(5000)]
three, four = ["n1", "n2", "n3"], ["n1", "n2", "n3", "n4"]
print("hashmod:", f"{L.moved(L.hashmod_ring(series, three), L.hashmod_ring(series, four)):.0%}", "of series move")
print("ketama :", f"{L.moved(L.ketama_ring(series, three), L.ketama_ring(series, four)):.0%}", "of series move")
print("pick for a global view without central ingest:", L.recommend({"global-view-without-central-ingest"}))
'''),
     'For HA I run two identical Prometheus servers and deduplicate. Thanos does it at query time and fills one replica’s gaps from the other. Mimir picks one replica on the write path and switches after a timeout, which loses a few samples on failover but stores the data once.')

# ───────────────────────────────────────────────────────────── book 4: Grafana stack
D = 'poc-26-logql-and-log-labels'
task('26', D, 'Run a LogQL pipeline stage by stage', 10, py(D, '''
import json, logql as Q
from logql import NS
T0 = 1_700_000_000 * NS
def line(i, **kw):
    return json.dumps({"level": "info", "method": "GET", "path": f"/api/cart/{i}", "status": 200, "latency": "120ms", **kw})
streams = [
 ({"app": "checkout", "namespace": "shop"}, [(T0 + i * NS, line(i, status=500 if i % 10 == 0 else 200, latency="900ms" if i % 10 == 0 else "120ms")) for i in range(100)]),
 ({"app": "web", "namespace": "edge"}, [(T0 + i * NS, f'10.0.{i % 3}.7 - - [x] "GET /index.html HTTP/1.1" {404 if i % 5 == 0 else 200} 512') for i in range(50)]),
 ({"app": "legacy", "namespace": "shop"}, [(T0, "not json at all")]),
]
sel = [("app", "=", "checkout")]
print('{app="checkout"}                               lines:', len(Q.run(streams, sel, [])))
print('  |= "500"                                     lines:', len(Q.run(streams, sel, [Q.line_filter("|=", "500")])))
print('  | json | latency > 500ms                     lines:', len(Q.run(streams, sel, [Q.json_parser, Q.label_filter("latency", ">", "500ms")])))
pat = Q.pattern_parser('<ip> - - [<_>] "<method> <uri> <_>" <status> <size>')
print('{app="web"} | pattern ... | status >= 400      lines:', len(Q.run(streams, [("app", "=", "web")], [pat, Q.label_filter("status", ">=", 400)])))
print('{app="legacy"} | json   error label:', Q.run(streams, [("app", "=", "legacy")], [Q.json_parser])[0][0].get("__error__"))
'''),
     'A colleague wants user_id as a Loki label “to make searches fast”. Predict what the selector {app=~".*"} does, and say what you would use for user_id instead.',
     py(D, '''
import logql as Q
try:
    Q.select([({"app": "x"}, [])], [("app", "=~", ".*")])
except ValueError as e:
    print("refused:", e)
print("2h30m =", Q.parse_duration("2h30m"), "s | 2.4KiB =", Q.parse_bytes("2.4KiB"), "bytes")
'''),
     'Loki indexes labels, not log content. Labels pick streams, so I keep them few and low-cardinality: app, namespace, environment. Everything else is found at query time with line filters first, because they’re cheapest, then a parser and label filters. A user ID belongs in the line or in structured metadata, never in a label.')

D = 'poc-27-trace-context-and-traceql'
task('27a', D, 'Propagate a trace across services', 10, py(D, '''
import tracing as T
tid, sid = "4bf92f3577b34da6a3ce929d0e0e4736", "00f067aa0ba902b7"
h = T.traceparent(tid, sid, True)
print("W3C traceparent:", h)
print("parsed         :", T.parse_traceparent(h))
print("uppercase id   :", T.parse_traceparent(h.upper()), "(invalid: must be lowercase)")
ctx = {"trace_id": "5759e988bd862e3fe1be46a994272793", "parent_id": "53995c3f42cd8ad8", "sampled": True}
print("X-Ray header   :", T.to_xray(ctx))
services = ["frontend", "checkout", "cart", "payment"]
print("complete traces, children follow the parent:", T.propagate(services, 2000, 0.1, parent_based=True))
print("complete traces, each service samples alone:", T.propagate(services, 2000, 0.1, parent_based=False))
'''),
     'Four services each sample 10% of traces independently. Predict the share of traces that arrive complete, then say which sampler setting fixes it.',
     py(D, '''
import tracing as T
for n in (2, 4, 8):
    print(n, "services, independent 10% sampling ->", T.propagate([f"s{i}" for i in range(n)], 4000, 0.1, parent_based=False), "complete")
'''),
     'A trace survives only if every hop passes the traceparent header on and respects its sampled flag. If each service samples on its own, most traces arrive with holes. I use parent-based sampling so the first service decides, and I check propagation across queues and async code, where it usually breaks.')
task('27b', D, 'Keep the traces worth keeping', 10, py(D, '''
import tracing as T
from tracing import Span
def traces(n, end, status="ok"):
    return [[Span(T.new_id(f"{status}{end}{i}", 16), "x", None, "web", "GET /checkout", 0, end, status)] for i in range(n)]
print("error traces kept       :", sum(map(T.tail_keep, traces(1000, 40, "error"))), "of 1000")
print("slow traces kept (>0.5s):", sum(map(T.tail_keep, traces(1000, 900))), "of 1000")
print("fast healthy traces kept:", sum(map(T.tail_keep, traces(1000, 10))), "of 1000")
print("head sampling keeps 10% of ids:", sum(T.ratio_decision(T.new_id(f"r{i}", 16), 0.1) for i in range(5000)), "of 5000")
'''),
     'Head sampling at 1% is cheap. Predict how many of 200 error traces it keeps, and how many tail sampling keeps.',
     py(D, '''
import tracing as T
ids = [T.new_id(f"err{i}", 16) for i in range(200)]
print("head sampling at 1% keeps", sum(T.ratio_decision(i, 0.01) for i in ids), "of 200 error traces")
print("tail sampling keeps all 200, because it decides after it has seen the whole trace")
'''),
     'Head sampling decides at the first span, so it’s cheap but blind: at 1% it throws away 99% of the errors too. Tail sampling waits for the whole trace and keeps every error, half the slow ones and 1% of the rest. The cost is a collector tier that buffers traces, with all spans of a trace sent to the same instance.')

D = 'poc-28-adot-collector-eks'
task('28a', D, 'Lint collector configs before they reach a cluster', 10, py(D, '''
import copy, collector as C
agent, cluster, gateway = (C.load(f"config/{n}.yaml") for n in ("node-agent", "cluster-agent", "gateway"))
for name, cfg in (("node-agent", agent), ("cluster-agent", cluster), ("gateway", gateway)):
    errors, warnings = C.validate(cfg)
    print(f"{name:14} mode={cfg.get('mode')}: {len(errors)} errors")
two = copy.deepcopy(cluster); two["replicas"] = 2
print("cluster agent with 2 replicas:", C.validate(two)[0])
bad = copy.deepcopy(agent); bad["mode"] = "deployment"
print("node agent as a Deployment   :", C.validate(bad)[0][:1])
'''),
     'Someone moves memory_limiter to the end of the processor list “so batching happens first”. Predict what the linter says and why the order matters.',
     py(D, '''
import copy, collector as C
agent = C.load("config/node-agent.yaml")
bad = copy.deepcopy(agent)
for p in bad["service"]["pipelines"].values():
    if "memory_limiter" in p.get("processors", []):
        p["processors"] = [x for x in p["processors"] if x != "memory_limiter"] + ["memory_limiter"]
for e in C.validate(bad)[0][:2]:
    print(e)
'''),
     'On EKS I run the collector three ways: a DaemonSet for per-node data like logs and kubelet stats, a single-replica Deployment for cluster-wide data so it isn’t collected twice, and a gateway for tail sampling and export. memory_limiter goes first in every pipeline so the collector sheds load before it runs out of memory.')
task('28b', D, 'Size the buffer and route traces for tail sampling', 10, py(D, '''
import copy, collector as C
print("buffer for a 30-minute backend outage at 5,000 lines/s of 400 bytes:", C.buffer_size_mb(30, 5000, 400), "MB")
agent, gateway = C.load("config/node-agent.yaml"), C.load("config/gateway.yaml")
print("trace-ID routing to the gateway in place:", C.tail_sampling_needs_trace_routing(agent, gateway))
naive = copy.deepcopy(agent); naive["service"]["pipelines"]["traces"]["exporters"] = ["otlp/gateway"]
print("with a plain OTLP exporter              :", C.tail_sampling_needs_trace_routing(naive, gateway))
'''),
     'The gateway has three replicas behind a normal load balancer and does tail sampling. Predict what goes wrong, then find the exporter that fixes it in the agent config.',
     f'cd {D}\ngrep -n "loadbalancing" -A 6 config/node-agent.yaml | head -12',
     'I size the collector’s queue from the outage I want to ride out: 30 minutes at 5,000 lines a second of 400 bytes is 3.6 GB. Tail sampling across several gateway replicas only works if every span of a trace reaches the same replica, so agents use the load-balancing exporter keyed on trace ID.')

D = 'poc-29-grafana-as-code-amg'
task('29', D, 'Generate a dashboard and lint it', 10, py(D, '''
import copy, dashboards_as_code as D
d = D.golden_signals_dashboard("checkout")
print("top row :", [p["title"] for p in d["panels"] if p["gridPos"]["y"] == 0])
print("problems:", D.lint_dashboard(d))
bad = copy.deepcopy(d)
bad["panels"][0]["title"] = ""
bad["panels"][0].pop("description", None)
print("after removing a title and description:")
for p in D.lint_dashboard(bad):
    print("  -", p)
print("mixin override:", D.merge({"stack": ["prometheus"], "interval": "1m"}, {"interval": "30s"}))
'''),
     'A dashboard has 60 panels and nobody can find anything. Predict what the linter says about it, then say which four panels you would put in the top row.',
     py(D, '''
import copy, dashboards_as_code as D
d = D.golden_signals_dashboard("checkout")
big = copy.deepcopy(d); big["panels"] = big["panels"] * 12
print([p for p in D.lint_dashboard(big) if "panel" in p][:2])
'''),
     'Dashboards are generated from code and reviewed like code: the four golden signals on the top row, detail in collapsed rows, every panel with a title, a unit and a description. A linter in CI enforces it, and the JSON in Git is the source of truth, so nobody’s hand edit survives the next deploy.')

D = 'poc-30-performance-feedback-loop'
task('30a', D, 'Turn the SLO into a load-test gate', 10, py(D, '''
import perf as P
th = P.thresholds_from_slo(99.9, 300)
print("k6 thresholds from a 99.9% / 300 ms SLO:", th)
ok = {"metrics": {"http_req_failed": {"value": 0.0004}, "http_req_duration": {"p(95)": 240.0}}}
bad = {"metrics": {"http_req_failed": {"value": 0.004}, "http_req_duration": {"p(95)": 410.0}}}
print("good run:", P.gate(ok, th))
print("bad run :", P.gate(bad, th))
for kind in ("smoke", "average", "stress", "spike", "soak"):
    print(f"{kind:8}", P.profile(kind)[:2])
'''),
     'Open the generated k6 script. Find where the thresholds are set, and say what happens to the CI job when one of them fails.',
     f'cd {D}\nhead -24 k6/checkout-average.js',
     'Load-test thresholds come straight from the SLO, so the test fails for the same reason a page would. Smoke runs on every merge, average load nightly, stress and spike before a launch, soak before a big release. The gate reads the summary and fails the pipeline.')
task('30b', D, 'Verify a deploy and roll back automatically', 10, py(D, '''
import perf as P
def healthy(expr, step): return 0.002 if "error" in expr else (5.0 if "login" in expr else 0.1)
def broken_logins(expr, step): return 0.0 if "login" in expr and step >= 2 else healthy(expr, step)
def one_blip(expr, step): return 0.0 if "login" in expr and step == 2 else healthy(expr, step)
for name, q in (("healthy", healthy), ("logins stop at step 2", broken_logins), ("one bad reading", one_blip)):
    r = P.verify_deployment(q, P.DEPLOY_CHECKS)
    print(f"{name:22}", r["decision"], r.get("reason", ""))
print("web vital, LCP samples:", P.rate_vital("LCP", [1800, 2100, 2300, 2600, 4200]))
'''),
     'Error rate is fine after a deploy, but logins have silently stopped. Which check catches that, and why does a single bad reading not trigger a rollback?',
     py(D, '''
import perf as P
for c in P.DEPLOY_CHECKS:
    print(c["name"], "| needs", ("min " + str(c["min"])) if "min" in c else ("max " + str(c["max"])))
'''),
     'After each deploy the pipeline queries a few signals for several steps: error ratio from logs, a success counter with a minimum, and downstream errors. Two bad readings in a row roll back; one is treated as noise. The “minimum” check matters most, because a broken login page produces no errors at all.')

# ───────────────────────────────────────────────────────────── interview drills
D = 'poc-01-slo-error-budget'
task('k1', D, 'Turn any SLO into its paging thresholds', 10, py(D, """
from slo.budget import burn_rate_for_consumption
fast, slow = burn_rate_for_consumption(0.02, 1), burn_rate_for_consumption(0.05, 6)
print(f"fast burn = 0.02 x 720 h / 1 h = {fast:.1f}    slow burn = 0.05 x 720 h / 6 h = {slow:.1f}")
print(f"{'SLO':>7} {'budget':>8} {'pages at (1h and 5m)':>21} {'pages at (6h and 30m)':>22} {'max burn':>9} {'full outage pages after':>24}")
for slo in (0.99, 0.995, 0.999, 0.9999):
    b = 1 - slo
    print(f"{slo:>7.2%} {b:>8.2%} {fast * b:>20.3%} {slow * b:>21.3%} {1 / b:>9.0f}x {3600 * fast * b:>20.0f} s")
"""),
     'Your SLO is 95%. Predict the error rate the 14.4× rule needs, then the lowest SLO at which that rule can fire at all (the error rate can’t pass 100%).',
     py(D, """
from slo.budget import burn_rate_for_consumption
fast = burn_rate_for_consumption(0.02, 1)
for slo in (0.95, 0.93, 0.90):
    b = 1 - slo
    print(f"SLO {slo:.0%}: highest possible burn rate {1 / b:.1f}x, the 14.4x rule needs {fast * b:.0%} errors ->", "can fire" if fast * b < 1 else "can never fire")
print("for a 7-day window the same 2%-in-an-hour rule is", round(burn_rate_for_consumption(0.02, 1, 7), 2), "x")
"""),
     'I derive the threshold on the spot: 2% of a 30-day budget in an hour is 0.02 × 720 = 14.4. Times the budget gives the error rate: 1.44% for three nines. I also know where it breaks: below about a 93% SLO the rule can’t fire, and a different window changes the number.')
task('k3', D, 'Decide when a few failures are enough to page', 10, py(D, """
from slo.stats import wilson_interval, min_failures_to_alert
for k in (15, 23, 24):
    lo, hi = wilson_interval(k, 100)
    print(f"{k} failures in 100: observed {k}%, 99% interval {lo:.1%} to {hi:.1%} ->", "page" if lo > 0.144 else "not sure yet")
for n in (100, 200, 1000):
    print(f"{n:>5} requests: page at {min_failures_to_alert(n, 0.144)} failures")
"""),
     'The same page for a 99.9% SLO means an error rate of 1.44%. Predict how many failures in 200 requests you need to be sure, and how that changes at 95% confidence.',
     py(D, """
from slo.stats import min_failures_to_alert
print("99.9% SLO, 200 requests, 99% confidence:", min_failures_to_alert(200, 0.0144), "failures")
print("99.9% SLO, 200 requests, 95% confidence:", min_failures_to_alert(200, 0.0144, z=1.96), "failures")
print("99.9% SLO, 20 requests, 99% confidence :", min_failures_to_alert(20, 0.0144), "failures")
"""),
     'At low traffic I don’t page on the raw ratio. I page when the lower bound of a Wilson interval is above the threshold: with a 99% SLO that’s 24 failures in 100 requests, not 15. Below a few dozen requests an hour I add synthetic probes, or judge by bad minutes.')

D = 'poc-20-promql-semantics'
task('k2', D, 'Check your answers against real Prometheus', 10,
     f'cd {D}/promtool\nhead -26 rate.test.yml\n../../poc-31-checkout-journey-slo-lab/bin/promtool test rules rate.test.yml',
     'Open rate.test.yml and change the third sample from 170 to 110, so the spike moves to the last step. Predict increase, rate and irate, edit the expected values, and run promtool again. It prints “got” for anything you got wrong.',
     py(D, """
import promql as P
late = [(15, 100), (30, 110), (45, 110), (60, 180)]
print("increase[1m]:", round(P.increase(late, 60, 60), 2), "| rate[1m]:", round(P.rate(late, 60, 60), 3), "| irate[1m]:", round(P.irate(late, 60, 60), 3))
"""),
     'I checked my understanding against Prometheus itself with promtool unit tests: four samples, and the expected values for increase, rate and irate written by hand before running. Extrapolation, counter resets and irate forgetting a spike are all in that one file.',
     setup='promtool ships with Prometheus. Get it once with <code>make prometheus</code> in poc-31-checkout-journey-slo-lab, which puts it in that folder’s <code>bin</code>.')

D = 'poc-32-etl-pipeline-slo-lab'
task('32a', D, 'Break a nightly pipeline four ways', 15,
     f'cd {D}\npython lab.py reset\npython lab.py day\npython lab.py day --fail\npython lab.py rerun --at 03:30\npython lab.py day --drop 0.02',
     'The 2%-drop job exited “ok” and the five traced orders all matched. Predict what the checks say for a job that forgets to divide pence by 100, and for a load that appends twice.',
     f'cd {D}\npython lab.py day --corrupt\npython lab.py day --duplicate',
     'I built a pipeline lab where the job can exit 0 and still fail finance. A crash that was rerun before the 07:00 deadline was a good day. A run that silently lost 2% of rows was a bad one, and only reconciliation against the source caught it; tracing five real orders didn’t.')
task('32b', D, 'Freshness when the source is quiet, and the month’s budget', 10,
     f'cd {D}\npython lab.py day --quiet\npython lab.py lag\npython lab.py day --late 09:15\npython lab.py month',
     'Read rules/etl-slo.yml. Predict the time of night ETLDeadlineAtRisk can first fire, and why there is no burn-rate alert. Then run the rule tests.',
     f'cd {D}/rules\ngrep -n "alert:\\|for:" etl-slo.yml\n../../poc-31-checkout-journey-slo-lab/bin/promtool test rules etl-slo.test.yml',
     'For freshness I compare the newest timestamp at the source with the newest in the warehouse, so a quiet source isn’t mistaken for a stale pipeline. With one run a day there’s no traffic for burn rates: I page at 05:00 if the 07:00 partition isn’t published, which leaves time to rerun.')

D = 'poc-31-checkout-journey-slo-lab'
task('probe', D, 'Run three probes against the shop and break things', 20,
     f"cd {D}\nmake prometheus          # once\npython lab.py up         # the shop, customer traffic, Prometheus and three probes\npython lab.py probe\npython lab.py promql 'sum by (route) (rate(edge_request_duration_seconds_count[1m]))'",
     'Give one probe location a broken network. Predict: page, ticket or nothing? Then break payment for everyone and predict how long the page takes.',
     f"cd {D}\npython lab.py probe-fault dublin on      # wait 2 minutes\npython lab.py promql 'probe:checkout_success:ratio_2m'\npython lab.py promql 'ALERTS{{alertname=~\"CheckoutProbe.*\"}}'\npython lab.py probe-fault dublin off\npython lab.py chaos payment --error-rate 1   # wait 3 minutes\npython lab.py promql 'ALERTS{{alertname=\"CheckoutProbeFailing\"}}'\npython lab.py chaos payment --reset && python lab.py down",
     'I added synthetic probes to my checkout lab: three locations placing a tagged test order every five seconds. The edge records them under their own route, so they stay out of the customer SLI. One location failing raised a ticket; all three failing paged in about two and a half minutes.',
     see="""  ok  place a test order: HTTP 200, confirmed, 0.01 s
  ok  declined card is refused politely: HTTP 200, declined, 0.00 s
probe succeeded in 0.02 s
{'route': 'POST /checkout (synthetic)'} 1.2
{'route': 'POST /checkout'} 10.0""",
     change_see="""one location broken, after 2 minutes:
{'location': 'frankfurt'} 1
{'location': 'dublin'} 0.1
{'location': 'london'} 1
{'alertname': 'CheckoutProbeOneLocation', 'alertstate': 'pending', 'severity': 'ticket'} 1

payment broken for everyone, after about 2.5 minutes:
{'alertname': 'CheckoutProbeFailing', 'alertstate': 'firing', 'severity': 'page'} 1""",
     setup='This one runs the live lab from the hands-on SLO track, so it needs <code>pip install prometheus_client</code> and about ten minutes.')

# lesson id -> task keys
FOR = {
    'ch-8': ['01'], 'ch-9': ['02'], 'ch-10': ['03a'], 'ch-11': ['03b'], 'ch-12': ['03c'], 'ch-13': ['09'], 'ch-14': ['05', '06'],
    'ch-15': ['07'], 'ch-16': ['08'], 'ch-17': ['04'], 'ch-18': ['10'], 'ch-20': ['19'], 'ch-21': ['11'],
    'pe-1': ['12'], 'pe-2': ['15'], 'pe-3': ['14'], 'pe-4': ['17'], 'pe-5': ['13'], 'pe-6': ['16'], 'pe-7': ['18a'], 'pe-8': ['18b'], 'pe-9': ['19'],
    'm-1': ['22b'], 'm-3': ['21a'], 'm-3q': ['20a'], 'm-4': ['22a'], 'm-5': ['23a'], 'm-6': ['22b', '25b'], 'm-7': ['21b'], 'm-8': ['21b'],
    'm-9': ['25a'], 'm-10': ['25b'], 'm-11': ['29'], 'm-12': ['23b'], 'm-13': ['24'], 'm-14': ['27a', '28a'],
    'g-2': ['27a'], 'g-4': ['26'], 'g-5': ['20b'], 'g-6': ['27b'], 'g-7': ['28a'], 'g-8': ['29'], 'g-9': ['23a', '24'],
    'g-10': ['29'], 'g-11': ['28b'], 'g-12': ['30a'], 'g-14': ['30b'],
    'k-1': ['k1', '24'], 'k-2': ['20a', 'k2'], 'k-3': ['k3'], 'k-4': ['32a', '32b'], 'k-5': ['probe'],
}
