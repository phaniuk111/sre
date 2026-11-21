# POC 16: Risk-profile rollouts, operation invariants and platform SLOs

**Book:** *Platform Engineering at Google* (early release), chapter "Deep Dive: Reliability" (chapter 16 of the final book)

The chapter's thesis: SRE provides the blueprint for reliability, and the platform is the machinery that gives it to every team by default. This POC implements three of its concrete mechanisms.

| Mechanism | In `risk_profile.py` | On AWS |
|---|---|---|
| **Risk profiles**: a service's tier and remaining error budget set its deployment policy | `rollout_plan(tier, budget_remaining, change_kind)` returns stages, bake time, canary requirement, regions at once. Low budget tightens the plan; a spent budget pauses feature rollouts for tiers 1 and 2 | CodeDeploy deployment configurations or AppConfig strategies chosen by tier (`terraform/`), alarms for rollback |
| **Preventing unsafe operations**: invariants enforced in code | `guard_drain()` rejects a drain of more than one region, or one that leaves too little capacity to survive a further loss. Break-glass overrides with an audit record | Route 53 ARC safety rules, Service Control Policies, CloudTrail and EventBridge for the alert |
| **Reliability of the platform itself** | `platform_slo()` counts only system-caused failures, as the chapter says Google's build service does | CloudWatch SLOs on pipeline success, deploy latency, telemetry lag |
| The nines | `allowed_downtime_minutes(slo)` | |

```bash
python risk_profile.py
python -m pytest -q
```

| Target | Downtime a year | What it takes (from the chapter) |
|---|---|---|
| 99% | 87.6 h | |
| 99.9% | 8.77 h | hygiene: error budgets, standard pipelines, basic telemetry, backups, static multi-zone |
| 99.99% | 52.6 min | active-active, global load balancing, N+1 by region, automated failover, canary analysis and rollback, chaos testing |
| 99.999% | 5.26 min | sharded serving, hedging, staggered change propagation, autonomous response |

## What to shift down
The chapter's three tests: **blast radius** (can one team's mistake hurt others?), **complexity** (does it need rare expertise?), and **the cost of a mistake** (minor: leave teams free; catastrophic: the platform owns it and blocks it).

## Interview talking points
* Reliability is a global cost that local teams underfund. A platform internalises it: build canary analysis once, and no team writes its own.
* The platform owns the *how* of deployment; the developer owns the *what*.
* Capacity changes should roll out through the same staged pipeline as software.
* Break-glass is a feature with accountability: permitted, logged, alerted, reviewed.
* The platform is a single point of failure for everyone, so it needs stricter SLOs than its tenants and a rollback path with almost no dependencies.
* If several teams have the same outage, change the platform default. Don't retrain the teams.
