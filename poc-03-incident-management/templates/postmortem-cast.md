# Post-incident analysis: <title>  (blameless + CAST)

*Author (independent, not a responder):* … *Status:* draft / reviewed (peer → team → org → exec)

## 1. Summary
Two or three sentences: what users experienced, for how long, how it was mitigated.

## 2. Impact
| Metric | Value |
|---|---|
| Error budget consumed | …% of 30-day budget |
| Users / customers affected | … (per-customer SLOs breached?) |
| CUJs affected | search / cart / checkout |
| TTD / TTM / TTR | … / … / … min |
| People & teams involved, pages sent | … |
| Customer comms: first update at | … (was it specific enough?) |

## 3. Timeline (UTC)
Facts only, no adjectives. Include *when we could first have detected it*.

## 4. CAST analysis (instead of a single "root cause")
### 4.1 Losses and hazards
- **Loss:** what unacceptable outcome happened (e.g. customers could not pay)?
- **Hazard:** what system state made it possible (e.g. "checkout serves errors above SLO while a rollout continues")?

### 4.2 Control structure at the time
Draw the controllers (humans and software) with control actions going down and feedback going up:
`Release engineer → CodeDeploy → Lambda alias → checkout` and `CloudWatch alarm → CodeDeploy (rollback) / on-call`.

### 4.3 Each controller: what it did, and why it made sense *at the time*
Write neutrally. Don't use "should have" or "failed to".
| Controller | Responsibilities | Contribution | Mental-model gaps | Contextual factors |
|---|---|---|---|---|
| On-call | mitigate impact | debugged for 20 min before rolling back | believed the release was unrelated because the canary passed | canary traffic 5% too small to see the bug in the EU-only code path |
| CodeDeploy alarm rollback | stop bad deploys | did not trigger | n/a (software) – designers assumed the alarm covered all routes | alarm watched only `/health` |

### 4.4 Systemic factors
- Safety culture: …
- Communication & coordination: …
- Management of change: …
- Safety information system (did people have the info they needed?): …
- Changes in the environment (gradual growth, new dependency, reorg): …

## 5. What went well / where we got lucky
Keep what went well (e.g. paging the comms lead early) and make it standard.

## 6. Action items (each traces to a factor above)
| # | Action | Addresses factor | Type (prevent / detect / mitigate / process) | Owner | Due |
|---|---|---|---|---|---|

## 7. Lessons for other teams (for the weekly outage digest)
