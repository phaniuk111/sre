# Playbook: Checkout SLO fast burn

> Fires when **2% of the 30-day error budget burns in 1 hour** (burn rate ≥ 14.4) and the last 5 minutes are still bad.
> Goal: **mitigate first, diagnose later.** Speed of accurate classification and escalation counts more than finding the root cause.

## 0. First 5 minutes (IMAG roles)
| Role | Who | Does |
|---|---|---|
| Incident Commander (IC) | first responder until handed over | owns all roles until delegated, decides, assigns work by name |
| Communications Lead | delegate when stakeholders start asking | status page/AWS Health-style updates every 30 min, single doc of truth |
| Operations Lead | delegate when >1 workstream | runs investigation & mitigation under IC direction |

- [ ] Declare the incident (Incident Manager opens automatically from the alarm). Over-escalating is fine; you can downgrade later.
- [ ] Post in the incident channel: *"I'm IC. Current impact: X. Next update in 15 min."*

## 1. Triage: how bad, how wide?
- How many users? Which CUJs (search / cart / checkout)? Check the `checkout-cuj` Synthetics canary and the SLO dashboard.
- One AZ/Region or global? CloudWatch: split `RequestCount`/5xx by `AvailabilityZone`.
- Did anything change? Check **CodeDeploy** deployments, **AppConfig** deployments, Terraform/CloudFormation stacks, feature flags. Most outages follow a change.

## 2. Generic mitigations (safe, don't need root cause)
| Mitigation | AWS action | When |
|---|---|---|
| **Roll back** | `aws deploy stop-deployment --auto-rollback-enabled` / revert Lambda alias / AppConfig `stop-deployment` | a change landed shortly before impact |
| **Drain** | Route 53 ARC zonal shift / weighted record to 0 / ALB target-group deregistration | impact limited to one AZ or region |
| **Upsize** | raise ASG desired / ECS service desired count / Lambda reserved concurrency | saturation (CPU, connections, throttles) |
| **Degrade** | AppConfig flag `recommendations_enabled=false` | expensive non-critical feature |
| **Block** | AWS WAF rule / API Gateway usage-plan throttle | one client or "query of death" |

Run mitigations as experiments: **one at a time**, announce it, watch the SLI for 5 minutes, record it in the timeline.

## 3. Investigate (multiple hypotheses)
Write hypotheses in the doc, assign each one to a named person, and try to **disprove** it. The first mitigation that works wins.

## 4. Resolve
Move to *Resolved* only when: cause identified OR the breaking change is rolled back **and blocked from redeploy**, and no organised response is needed. Use a "wait and see" period for complex incidents. The IC announces closure on every channel.

## 5. Learn
Open the post-incident analysis from `templates/postmortem-cast.md` within 24h. Assign an author who **was not** part of the response.
