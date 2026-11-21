# Knowledge map

*Twelve themes across both books. Each row is a concept, a one-line definition, where it is taught, and the POC that implements it. S = SRE book chapter, P = platform book chapter (final numbering).*

## Targets and budgets

How reliable is reliable enough, and how the answer drives decisions.

| Concept | In one line | Chapters | Code |
|---|---|---|---|
| **SLI, SLO, SLA** | Indicator (good events over valid events), objective (the target), agreement (what happens if it is missed) | S8 | POC 01 |
| **Error budget** | One minus the SLO: the failure you are allowed, to be spent on change | S2, S8 | POC 01 |
| **Burn rate** | How fast the budget is being spent. Page on a fast burn confirmed by a short window | S8 | POC 01 |
| **Error budget policy** | What changes as the budget shrinks: business as usual, growing trade-offs, freeze | S8 | POC 01 |
| **Critical user journey** | A user goal and its tasks; SLOs are defined from it downward | S8, S9 | POC 02 |
| **Low-traffic alerting** | Page only when a confidence interval’s lower bound exceeds the threshold | S8, S9 | POC 01 |
| **Risk profile** | A service’s tier and remaining budget set its rollout policy automatically | S8, P16 | POC 16 |
| **The nines** | Each extra nine cuts allowed downtime tenfold and costs far more than the last | S2, S8, P16 | POC 16 |

## Seeing the system

What you have to be able to observe, and who provides it.

| Concept | In one line | Chapters | Code |
|---|---|---|---|
| **Observability** | Someone without tribal knowledge can test and reject hypotheses quickly | S9 | POC 02 |
| **Four golden signals** | Latency, traffic, errors, saturation, with the same names everywhere | S9, P16 | POC 02 |
| **Client-side telemetry** | What servers can’t see: DNS, certificates, crashes, retries hiding errors | S9 | POC 02 |
| **Customer-centric invariant** | A check from the user’s side, such as “sees non-zero valid results” | S9 | POC 02 |
| **Application productivity metric** | Useful work divided by resources used; separates busier from slower | P14 | POC 17 |
| **Security signals** | Frameworks report per request which protections ran; absence raises an alert | P15 |  |
| **Model signals** | Freshness, drift, confidence; for agents, tokens, latency, tool calls | S20, P16, P22 | POC 19 |
| **Joint cognitive system** | People and tools share a working memory in an incident; consistency gives fluency | P16 |  |

## Changing production safely

Changes are the main cause of outages in both books.

| Concept | In one line | Chapters | Code |
|---|---|---|---|
| **Progressive rollout** | Small exposure first, growing in stages with bake time | S14, S17, P16 | POC 05, 16 |
| **Canary analysis** | Compare the new version with a control serving the same traffic at the same time | S14, P16 | POC 05 |
| **Automatic rollback** | A regression halts and reverts the rollout without a human | S17, P16 | POC 05 |
| **Configuration as code** | Versioned, reviewed, tested and rolled out like a binary | S14, P15 | POC 10, 15 |
| **Blueprint** | A pre-validated template with locked invariants and a few parameters | P15 | POC 15 |
| **Conformance verification** | Continuously compare what is deployed with the approved baseline | P15 | POC 15, 10 |
| **Attestation and deploy gate** | Signed statements about an artifact, verified before it may run | P15 | POC 14 |
| **Bad-change marker** | Flag one change and the deploy system refuses every build containing it | P9, P16 | POC 14 |

## Failure, response and learning

What to do when it breaks, and how to stop it breaking the same way.

| Concept | In one line | Chapters | Code |
|---|---|---|---|
| **Incident roles** | Commander directs, operations acts, communications informs | S10 | POC 03 |
| **Generic mitigations** | Roll back, drain, add capacity, degrade, block: safe before diagnosis | S10, S13 | POC 03, 09 |
| **Emergency modes** | Normal, emergency, disaster; each needs tooling with fewer dependencies | S17 | POC 04 |
| **Break-glass** | A bypass that is permitted, logged, alerted on and reviewed | P16 | POC 14, 16 |
| **Blameless postmortem** | Why the action made sense at the time; several contributing factors | S4, S11 | POC 03 |
| **STPA** | Forward-looking: hazards, control structure, unsafe control actions, scenarios | S12 | POC 03 |
| **CAST** | Backward-looking: the same model applied to an incident, down to systemic factors | S12 | POC 03 |
| **Rasmussen’s boundaries** | Cost and workload pressure push a system towards the accident boundary | S11 |  |
| **Institutional memory** | If teams repeat an outage, change the platform default, not the training | P16 |  |

## Resilience by design

Properties built in before the incident.

| Concept | In one line | Chapters | Code |
|---|---|---|---|
| **Failure domains and N+1** | Survive the loss of a zone or region; say which domain you mean | S15, S17, P16 | POC 04, 07 |
| **Graceful degradation** | Serve something useful when a dependency is gone | S1, S17 | POC 04 |
| **Load shedding by criticality** | Drop the least important work first; tag requests | S15, S17, P14 | POC 04 |
| **Retry budgets and adaptive throttling** | Bound retries in the client library so one service can’t start a cascade | S17, P16 | POC 04 |
| **Deadline propagation** | Stop work whose caller has already given up | P14 | POC 17 |
| **Fail open or fail closed** | Degrade for optional features; refuse for security or correctness checks | P9, P22 | POC 12, 19 |
| **Operation invariants** | The platform rejects unsafe actions, such as draining several regions | P16 | POC 16 |

## Capacity and efficiency

Having enough, and not paying for more.

| Concept | In one line | Chapters | Code |
|---|---|---|---|
| **Forecast with uncertainty** | Plan to a chosen risk, not to every edge case | S15 | POC 07 |
| **Pooling** | Peaks rarely coincide, so a shared pool needs less than the sum of its parts | S15, P14 | POC 07 |
| **Stockout** | Pooled services must survive not getting capacity | S15 | POC 07 |
| **Autoscaling** | Predictive for the long term, reactive within minutes, horizontal and vertical | P16 | POC 07 |
| **Fleet-wide profiling** | One profiler everywhere shows which shared component costs the most | P14 | POC 17 |
| **On by default** | Ship optimisations to everyone; absorb small regressions; opt-outs are information | P14 | POC 17 |
| **Idle accelerators** | Power stays high at low utilisation, so run fewer machines hotter | S20 |  |

## Data

Losing data is worse than being down.

| Concept | In one line | Chapters | Code |
|---|---|---|---|
| **RPO, RTO, RWO** | How much you may lose, how long until you are back (detect, act, restore), how far back you can go | S16 | POC 08 |
| **3-2-1** | Three copies, two media, one elsewhere; replication is not a backup | S16 | POC 08 |
| **Restore testing** | A backup you have not restored is a hope | S16 | POC 08 |
| **Integrity first** | Recover as much as possible, never at the cost of integrity | S16 |  |
| **Shared database** | Several services on one schema; the classic coupling antipattern | P9 | POC 12 |

## Platforms and shifting down

Where both books converge.

| Concept | In one line | Chapters | Code |
|---|---|---|---|
| **Shift down** | Move responsibility into the platform so teams inherit the result | S18, S23, P15, P16 | POC 10, 13–16 |
| **Ecosystem types 0 to 4** | YOLO, ad hoc, guided, engineered, assured | S18, P12 | POC 10 |
| **Golden path** | The supported, documented, easiest way to do a common task | S18, P18, P19 | POC 18 |
| **Resource or guardrail** | A resource helps; a guardrail makes the safe choice the only one | P12 | POC 14 |
| **Effectiveness zone** | Match the strength of a control to the severity of the outcome | S18 | POC 10 |
| **Shared fate and the three Rs** | Resources, rights, responsibilities: the contract between platform and teams | P12 | docs |
| **Large-scale change** | One team changes thousands of projects at once; needs a uniform toolchain | P12, P14 |  |
| **Pace layers** | Six layers from experiments to law, each changing at its own speed | P10 |  |
| **Platform SLOs** | The platform is everyone’s single point of failure and needs stricter objectives | P16 | POC 16 |

## Coupling and architecture

What depends on what, and whether anyone decided it.

| Concept | In one line | Chapters | Code |
|---|---|---|---|
| **Explicit and implicit** | A direct call, or an unstated assumption such as a message format | P9 | POC 12 |
| **Retargetability** | Being able to reuse a part elsewhere; what coupling trades away | P9 |  |
| **Loose patterns** | Layers, pipe and filter, publish-subscribe, federation, fail open | P9 | POC 12 |
| **Antipatterns** | Shared database, distributed monolith, megamorphic artifact, control coupling | P9 | POC 12 |
| **Hyrum’s law** | With enough users, every observable behaviour is depended on by someone | S8, P9, P14 |  |
| **Discovering coupling** | Static analysis, tracing, log correlation, chaos engineering | P9 | POC 12, 06 |

## Security by construction

Prevent classes of bug instead of hunting instances.

| Concept | In one line | Chapters | Code |
|---|---|---|---|
| **Assurance** | Confidence that a property holds for every behaviour; testing can’t give it | P15 | POC 13 |
| **Archetype and invariant** | A recurring application shape, and the properties a platform can own for it | P15 |  |
| **Risky operation** | Safe only if a condition holds that nothing guarantees | P15 | POC 13 |
| **Safe abstraction** | No safety condition on callers; the module owns the risk; reviewable alone | P15 | POC 13 |
| **SLSA build levels** | L1 provenance exists, L2 signed by a hosted builder, L3 hardened builds | P15 | POC 14 |
| **Identity and authorisation** | Workload identity, mutual TLS, a central relationship-based authorisation service | P15 |  |
| **Insider risk** | Multi-party approval, no direct production access, audited proxies | P15 |  |
| **Prompt injection** | No separate channel for data in a model, so it can’t be prevented by construction yet | P15, P22 |  |

## People, teams and product

The sociotechnical half.

| Concept | In one line | Chapters | Code |
|---|---|---|---|
| **Psychological safety** | Safe to be wrong, to not know, to make an honest novel mistake | S4, P24 |  |
| **Toil** | Manual, repetitive, automatable, no lasting value; keep engineering above half | S1, S13, P16 | POC 09 |
| **Sustainable on-call** | Limits on on-call share, rotation size and incidents per shift | S6, S10 |  |
| **Engagement model** | The contract of work between SRE and a product team | S7 |  |
| **Developer experience** | Feedback loops, cognitive load, flow | P18 | POC 18 |
| **Platform as a product** | Customers, a value proposition, a lifecycle; jobs to be done | P19 | POC 18 |
| **Deprecation** | A launch in reverse, with brownouts and a real off switch | P19 | POC 18 |
| **Education** | Belongs to the platform team; next task to the most junior who can do it with guidance | S5, P24 |  |

## AI

Running AI, and running with AI.

| Concept | In one line | Chapters | Code |
|---|---|---|---|
| **Quality as a reliability signal** | A fast success with a wrong answer is a failure | S20, P22 | POC 19 |
| **Qualification** | Hardware, models and prompts are tested and canaried before serving | S20 | POC 19 |
| **Feature store and model registry** | One source of feature values; one source of truth for versions | P22 | POC 19 |
| **Autonomy levels** | From manual to full; earned per class of action, never assumed | S21 | POC 11 |
| **Reversible atomic actions** | An agent may only do what it knows how to undo | S21 | POC 11 |
| **Guardrails as containment** | Generated code must compile against safe APIs and pass the deploy gate | P12, P15 | POC 13, 14 |
| **Agentic platform** | Agent-friendly interfaces, with the platform as the controls that always hold | P19, P22 |  |
| **Amplifier** | AI magnifies an organisation’s existing strengths and dysfunctions | P24 |  |
