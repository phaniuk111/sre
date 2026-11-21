# Extracted requirements

*What the four books say a team or platform should have in place, as a checklist. Use it to assess a system, or to structure a "how would you improve this?" answer. S = SRE book chapter, P = platform book chapter (final numbering), M = Mastering Prometheus, G = Observability with Grafana.*

## Targets

| | Requirement | Source | Code |
|---|---|---|---|
| R1 | Every critical user journey has an SLI and an SLO chosen from user need | S8, S9 | POC 01 |
| R2 | A written error budget policy with three zones, agreed by product and engineering | S8 | POC 01 |
| R3 | Paging alerts fire on burn rate, confirmed by a short window | S8, M13 | POC 01 |
| R4 | Low-traffic services alert on a confidence interval, not a raw ratio | S8, S9 | POC 01 |
| R5 | Each service has a tier that the delivery pipeline reads | P16 | POC 16 |

## Observability

| | Requirement | Source | Code |
|---|---|---|---|
| R6 | New services get the four golden signals, logs and traces without doing anything | S9, P16 | POC 02 |
| R7 | Metric names and dashboards are the same across services | P16 | POC 02 |
| R8 | User journeys are measured from the client side as well as the server | S9, G12 | POC 02 |
| R9 | Monitoring does not depend on the systems it monitors | S9, M5, M6 |  |
| R10 | Each service reports useful work so productivity per unit of resource is known | P14 | POC 17 |

## Metrics, logs and traces

| | Requirement | Source | Code |
|---|---|---|---|
| R11 | Every scrape job has sample and label limits, and new metrics are reviewed for cardinality | M7, G15 | POC 21 |
| R12 | Prometheus runs as an HA pair sending to every Alertmanager in a cluster, with a dead man’s switch | M5, M6 | POC 23, 25 |
| R13 | Alert and recording rules have unit tests and are linted in pull requests | M12 | POC 23 |
| R14 | SLO burn-rate rules are generated from a spec, not written by hand | M13, S8 | POC 24 |
| R15 | Loki labels are few and low-cardinality; IDs live in the log line | G4 | POC 26 |
| R16 | W3C trace context is propagated everywhere, with conversion at AWS or B3 boundaries | G6, M14 | POC 27 |
| R17 | Collectors run as node agents, one cluster agent and a gateway, with buffers sized for a backend outage | G11 | POC 28 |
| R18 | Dashboards and alert rules live in Git, in team folders, applied with Terraform | G8, G10, M11 | POC 29 |
| R19 | Every deployment is annotated and verified automatically against telemetry | G14 | POC 30 |
| R20 | Load tests run with SLO thresholds, and their telemetry is kept out of production | G13 | POC 30 |
| R21 | The observability platform has its own SLOs, cost dashboards and a tested disaster plan | G15 |  |

## Incidents and learning

| | Requirement | Source | Code |
|---|---|---|---|
| R22 | Anyone can declare an incident; roles are defined and practised | S10, G9 | POC 03 |
| R23 | Generic mitigations exist and can be run without diagnosis | S10, S13 | POC 03, 09 |
| R24 | Emergency access, communication and documentation work when normal tools are down | S17 | POC 04 |
| R25 | Postmortems are blameless, list several contributing factors and track actions to completion | S11 | POC 03 |
| R26 | Repeated incidents lead to a changed platform default | P16 |  |

## Change

| | Requirement | Source | Code |
|---|---|---|---|
| R27 | Every production change, including configuration, goes through one pipeline | S14, P15, P16 | POC 05, 15 |
| R28 | Rollouts are staged, with bake time set by the service’s risk profile | S17, P16 | POC 16 |
| R29 | A canary is compared with a control automatically, and regressions roll back | S14, P16 | POC 05 |
| R30 | Artifacts are built by a hosted builder, signed, and verified before deploy | P15 | POC 14 |
| R31 | A change can be marked bad and is then blocked everywhere | P16 | POC 14 |
| R32 | Break-glass exists, needs an incident reference, and alerts security | P16 | POC 14, 16 |

## Resilience and capacity

| | Requirement | Source | Code |
|---|---|---|---|
| R33 | Critical services run across failure domains by default, sized to lose one | S17, P16 | POC 04, 07 |
| R34 | The client library enforces backoff and a retry budget | S17, P16 | POC 04 |
| R35 | Requests carry criticality and deadlines; overload sheds the least important first | S15, P14 | POC 04 |
| R36 | The platform rejects operations that break an invariant | P16 | POC 16 |
| R37 | Capacity is forecast with stated uncertainty and scaled automatically | S15, P16 | POC 07 |
| R38 | Fault injection is run regularly, with SLO-based stop conditions | S14, P9 | POC 06 |

## Data

| | Requirement | Source | Code |
|---|---|---|---|
| R39 | Each data set has an RPO, RTO and retention window set by the business | S16 | POC 08 |
| R40 | Backups are separate copies; writers to live data can’t delete them | S16 | POC 08 |
| R41 | Restores are tested automatically and the restored data is validated | S16 | POC 08 |
| R42 | Each service owns its data store behind an API | P9 | POC 12 |

## Security

| | Requirement | Source | Code |
|---|---|---|---|
| R43 | New code is written in a memory-safe language | P15 |  |
| R44 | Injection-prone operations are reachable only through typed safe APIs, checked in CI | P15 | POC 13 |
| R45 | Dependencies come from a curated repository with automated updates | P12, P15 | POC 14 |
| R46 | Workloads have their own identities; service calls are authenticated and authorised by the framework | P15 |  |
| R47 | Web security headers and TLS are set once, centrally | P15 |  |
| R48 | Infrastructure comes from reviewed blueprints, and drift is detected | P15 | POC 15 |
| R49 | Adoption of each guarantee is measured across the fleet | P15 | POC 13, 15 |

## The platform as a product

| | Requirement | Source | Code |
|---|---|---|---|
| R50 | Customer segments are named, and their jobs to be done are written down | P19 | POC 18 |
| R51 | Time to a first production deploy is measured and short | P18, P19 | POC 18 |
| R52 | Console, command line, infrastructure as code and agents share one API | P18 |  |
| R53 | The golden path has documented escape hatches; exemptions have an owner and an expiry | S18, P18 | POC 10 |
| R54 | The contract between platform and teams is published as resources, rights and responsibilities | P12 | docs |
| R55 | A scorecard reports user, system and business views | P19 | POC 18 |
| R56 | The platform has its own SLOs, stricter than its tenants’ | P16 | POC 16 |
| R57 | Old platforms are retired with a plan, brownouts and an off date | P19 | POC 18 |

## People

| | Requirement | Source | Code |
|---|---|---|---|
| R58 | Engineering work is at least half of an SRE team’s time | S1, S6, S13 | POC 09 |
| R59 | On-call load is capped and rotations are large enough to be sustainable | S6, S10 |  |
| R60 | Onboarding and training build confidence through practice | S5 |  |
| R61 | Platform teams have people with time allocated to support, writing and teaching | P24 |  |
| R62 | Internal documentation has owners and review dates | S4, P24 |  |

## AI

| | Requirement | Source | Code |
|---|---|---|---|
| R63 | Model endpoints have a quality objective alongside latency and availability | S20, P22 | POC 19 |
| R64 | Freshness, input drift and confidence are monitored and can page | P22 | POC 19 |
| R65 | Models are signed, registered with lineage, evaluated and canaried before serving | S20, P22 | POC 19 |
| R66 | Input and output guardrails run outside the model | P22 |  |
| R67 | Agents have least privilege, act only reversibly, and earn autonomy per class of action | S21, P22 | POC 11 |
| R68 | Generated code passes the same safe APIs and deploy gate as human code | P12, P15 | POC 13, 14 |
