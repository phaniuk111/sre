# Knowledge map

*14 themes across all four books. Each row is a concept, a one-line definition, where it is taught, and the POC that implements it. S = SRE book chapter, P = platform book chapter (final numbering), M = Mastering Prometheus, G = Observability with Grafana.*

## Targets and budgets

How reliable is reliable enough, and how the answer drives decisions.

| Concept | In one line | Chapters | Code |
|---|---|---|---|
| **SLI, SLO, SLA** | Indicator (good events over valid events), objective (the target), agreement (what happens if it is missed) | S8, M13, G9 | POC 01, 24 |
| **Error budget** | One minus the SLO: the failure you are allowed, to be spent on change | S2, S8, M13 | POC 01, 24 |
| **Burn rate** | How fast the budget is being spent. Page on a fast burn confirmed by a short window | S8, M13 | POC 01, 24 |
| **Error budget policy** | What changes as the budget shrinks: business as usual, growing trade-offs, freeze | S8 | POC 01 |
| **Critical user journey** | A user goal and its tasks; SLOs are defined from it downward | S8, S9 | POC 02 |
| **Low-traffic alerting** | Page only when a confidence interval’s lower bound exceeds the threshold | S8, S9, M13 | POC 01, 24 |
| **Risk profile** | A service’s tier and remaining budget set its rollout policy automatically | S8, P16 | POC 16 |
| **The nines** | Each extra nine cuts allowed downtime tenfold and costs far more than the last | S2, S8, P16 | POC 16 |

## Seeing the system

What you have to be able to observe, and who provides it.

| Concept | In one line | Chapters | Code |
|---|---|---|---|
| **Observability** | Someone without tribal knowledge can test and reject hypotheses quickly | S9, M1, G1 | POC 02 |
| **Four golden signals** | Latency, traffic, errors, saturation, with the same names everywhere | S9, P16, G8, G9 | POC 02, 29 |
| **Client-side telemetry** | What servers can’t see: DNS, certificates, crashes, retries hiding errors | S9, G12 | POC 02, 30 |
| **Customer-centric invariant** | A check from the user’s side, such as “sees non-zero valid results” | S9 | POC 02 |
| **Application productivity metric** | Useful work divided by resources used; separates busier from slower | P14 | POC 17 |
| **Security signals** | Frameworks report per request which protections ran; absence raises an alert | P15 |  |
| **Model signals** | Freshness, drift, confidence; for agents, tokens, latency, tool calls | S20, P16, P22 | POC 19 |
| **Joint cognitive system** | People and tools share a working memory in an incident; consistency gives fluency | P16 |  |

## Changing production safely

Changes are the main cause of outages in both books.

| Concept | In one line | Chapters | Code |
|---|---|---|---|
| **Progressive rollout** | Small exposure first, growing in stages with bake time | S14, S17, P16, G14 | POC 05, 16 |
| **Canary analysis** | Compare the new version with a control serving the same traffic at the same time | S14, P16 | POC 05 |
| **Automatic rollback** | A regression halts and reverts the rollout without a human | S17, P16, G14 | POC 05, 30 |
| **Configuration as code** | Versioned, reviewed, tested and rolled out like a binary | S14, P15, M12, G10 | POC 10, 15, 23, 29 |
| **Blueprint** | A pre-validated template with locked invariants and a few parameters | P15 | POC 15 |
| **Conformance verification** | Continuously compare what is deployed with the approved baseline | P15 | POC 15, 10 |
| **Attestation and deploy gate** | Signed statements about an artifact, verified before it may run | P15 | POC 14 |
| **Bad-change marker** | Flag one change and the deploy system refuses every build containing it | P9, P16 | POC 14 |

## Failure, response and learning

What to do when it breaks, and how to stop it breaking the same way.

| Concept | In one line | Chapters | Code |
|---|---|---|---|
| **Incident roles** | Commander directs, operations acts, communications informs | S10, G9 | POC 03 |
| **Generic mitigations** | Roll back, drain, add capacity, degrade, block: safe before diagnosis | S10, S13 | POC 03, 09 |
| **Emergency modes** | Normal, emergency, disaster; each needs tooling with fewer dependencies | S17 | POC 04 |
| **Break-glass** | A bypass that is permitted, logged, alerted on and reviewed | P16 | POC 14, 16 |
| **Blameless postmortem** | Why the action made sense at the time; several contributing factors | S4, S11, G9 | POC 03 |
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
| **Fleet-wide profiling** | One profiler everywhere shows which shared component costs the most | P14, G13 | POC 17, 30 |
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
| **Golden path** | The supported, documented, easiest way to do a common task | S18, P18, P19, G10 | POC 18 |
| **Resource or guardrail** | A resource helps; a guardrail makes the safe choice the only one | P12 | POC 14 |
| **Effectiveness zone** | Match the strength of a control to the severity of the outcome | S18 | POC 10 |
| **Shared fate and the three Rs** | Resources, rights, responsibilities: the contract between platform and teams | P12 | docs |
| **Large-scale change** | One team changes thousands of projects at once; needs a uniform toolchain | P12, P14 |  |
| **Pace layers** | Six layers from experiments to law, each changing at its own speed | P10 |  |
| **Platform SLOs** | The platform is everyone’s single point of failure and needs stricter objectives | P16, G15 | POC 16 |

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
| **Sustainable on-call** | Limits on on-call share, rotation size and incidents per shift | S6, S10, G9 |  |
| **Engagement model** | The contract of work between SRE and a product team | S7 |  |
| **Developer experience** | Feedback loops, cognitive load, flow | P18 | POC 18 |
| **Platform as a product** | Customers, a value proposition, a lifecycle; jobs to be done | P19, G15 | POC 18 |
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

## Metrics with Prometheus

How Prometheus stores, queries, alerts and scales.

| Concept | In one line | Chapters | Code |
|---|---|---|---|
| **Series and cardinality** | A metric name plus one label set; every new value is a new series in memory and index | M3, M7, G5 | POC 21 |
| **Head block, WAL and blocks** | Two hours in memory with a write-ahead log, then immutable blocks compacted up to 31 days | M3, G5 | POC 21 |
| **Inverted index** | Sorted postings lists per label pair, intersected shortest first | M3 | POC 21 |
| **rate, increase and irate** | Reset-aware, extrapolated over the window; irate uses the last two samples | M3, G5 | POC 20 |
| **Vector matching** | on, ignoring, group_left and group_right; and, or, unless for alert logic | M3 | POC 20 |
| **Relabeling** | Rewrite targets before the scrape, series after it, and series before remote write | M4 | POC 22 |
| **Service discovery** | Kubernetes, EC2, file and HTTP discovery turn inventory into targets | M4 | POC 22 |
| **Alertmanager routing** | A tree of matchers with grouping, inhibition, silences and timers | M5, G9 | POC 23 |
| **High availability** | Identical pairs differing by a replica label; deduplicate at query or write | M6, M9, M10 | POC 25 |
| **Sharding and federation** | hashmod splits targets; federation only for small aggregates | M6 | POC 22 |
| **Scrape limits** | sample_limit and label limits fail a scrape that would explode cardinality | M7, G15 | POC 21 |
| **Remote write** | Sharded queues with backoff to long-term storage | M9, G5 | POC 25 |
| **Thanos, Mimir, VictoriaMetrics** | Object-storage blocks with a global query layer, central multi-tenant ingestion, or efficient local disks | M9, M10, G5 | POC 25 |
| **Monitoring mixins** | Jsonnet bundles of alerts, rules and dashboards, overridden through _config | M11 | POC 29 |
| **Rule CI** | promtool syntax and unit tests, Pint against live data, in pull requests | M12 | POC 23 |
| **Window-based SLO** | Count good and bad time windows instead of requests; suits low traffic | M13, S8 | POC 24 |

## Logs, traces and running observability

The rest of the Grafana stack, and observability as a platform.

| Concept | In one line | Chapters | Code |
|---|---|---|---|
| **Loki labels are the index** | Few low-cardinality labels; everything else is filtered or parsed at query time | G4 | POC 26 |
| **LogQL pipeline** | Stream selector, line filters, parsers, typed label filters, formatting, metric functions | G4 | POC 26 |
| **Trace context** | W3C traceparent and baggage carried across every hop; X-Ray and B3 at the edges | G6, M14 | POC 27 |
| **TraceQL** | Select spansets by attributes and structure: child, descendant, sibling | G6 | POC 27 |
| **Exemplars** | A trace ID attached to a metric sample, linking a spike to an example request | G5 |  |
| **Tail sampling** | Decide per whole trace in a gateway; keep errors and slow traces | G6, G11 | POC 28 |
| **Collector topology** | Node agents, a single cluster agent and a gateway, with buffers sized for outages | G10, G11, M14 | POC 28 |
| **Connectors** | spanmetrics and servicegraph derive RED metrics and service graphs from traces | G10 | POC 28 |
| **RED and USE** | Rate, errors, duration for requests; utilisation, saturation, errors for resources | G9, S9 |  |
| **Gold, silver, bronze** | Strategic, tactical and operational levels of incident command | G9, S10 |  |
| **Dashboard purpose** | Who is it for, what do they need, where will they view it | G8 | POC 29 |
| **Dashboards and rules as code** | Team folders, Terraform, linting in CI | G8, G10, M11 | POC 29 |
| **Real user monitoring** | Web Vitals at p75 and sessions linked to backend traces | G12 | POC 30 |
| **Continuous profiling** | Self time and total time; flame graph width is share of samples | G13, P14 | POC 30 |
| **Load test types** | Smoke, average, stress, spike, breakpoint, soak; thresholds from SLOs | G13, S15 | POC 30 |
| **Deployment verification** | Query telemetry after a deploy and roll back automatically | G14, S14, P16 | POC 30 |
| **Observability cost** | Plan what you need, drop at collection, isolate noisy environments | G15, M7 | POC 21 |
