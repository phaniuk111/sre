# Extracted requirements

*What the two books say a team or platform should have in place, as a checklist. Use it to assess a system, or to structure a "how would you improve this?" answer. S = SRE book chapter, P = platform book chapter (final numbering).*

## Targets

| | Requirement | Source | Code |
|---|---|---|---|
| R1 | Every critical user journey has an SLI and an SLO chosen from user need | S8, S9 | POC 01 |
| R2 | A written error budget policy with three zones, agreed by product and engineering | S8 | POC 01 |
| R3 | Paging alerts fire on burn rate, confirmed by a short window | S8 | POC 01 |
| R4 | Low-traffic services alert on a confidence interval, not a raw ratio | S8, S9 | POC 01 |
| R5 | Each service has a tier that the delivery pipeline reads | P16 | POC 16 |

## Observability

| | Requirement | Source | Code |
|---|---|---|---|
| R6 | New services get the four golden signals, logs and traces without doing anything | S9, P16 | POC 02 |
| R7 | Metric names and dashboards are the same across services | P16 | POC 02 |
| R8 | User journeys are measured from the client side as well as the server | S9 | POC 02 |
| R9 | Monitoring does not depend on the systems it monitors | S9 |  |
| R10 | Each service reports useful work so productivity per unit of resource is known | P14 | POC 17 |

## Incidents and learning

| | Requirement | Source | Code |
|---|---|---|---|
| R11 | Anyone can declare an incident; roles are defined and practised | S10 | POC 03 |
| R12 | Generic mitigations exist and can be run without diagnosis | S10, S13 | POC 03, 09 |
| R13 | Emergency access, communication and documentation work when normal tools are down | S17 | POC 04 |
| R14 | Postmortems are blameless, list several contributing factors and track actions to completion | S11 | POC 03 |
| R15 | Repeated incidents lead to a changed platform default | P16 |  |

## Change

| | Requirement | Source | Code |
|---|---|---|---|
| R16 | Every production change, including configuration, goes through one pipeline | S14, P15, P16 | POC 05, 15 |
| R17 | Rollouts are staged, with bake time set by the service’s risk profile | S17, P16 | POC 16 |
| R18 | A canary is compared with a control automatically, and regressions roll back | S14, P16 | POC 05 |
| R19 | Artifacts are built by a hosted builder, signed, and verified before deploy | P15 | POC 14 |
| R20 | A change can be marked bad and is then blocked everywhere | P16 | POC 14 |
| R21 | Break-glass exists, needs an incident reference, and alerts security | P16 | POC 14, 16 |

## Resilience and capacity

| | Requirement | Source | Code |
|---|---|---|---|
| R22 | Critical services run across failure domains by default, sized to lose one | S17, P16 | POC 04, 07 |
| R23 | The client library enforces backoff and a retry budget | S17, P16 | POC 04 |
| R24 | Requests carry criticality and deadlines; overload sheds the least important first | S15, P14 | POC 04 |
| R25 | The platform rejects operations that break an invariant | P16 | POC 16 |
| R26 | Capacity is forecast with stated uncertainty and scaled automatically | S15, P16 | POC 07 |
| R27 | Fault injection is run regularly, with SLO-based stop conditions | S14, P9 | POC 06 |

## Data

| | Requirement | Source | Code |
|---|---|---|---|
| R28 | Each data set has an RPO, RTO and retention window set by the business | S16 | POC 08 |
| R29 | Backups are separate copies; writers to live data can’t delete them | S16 | POC 08 |
| R30 | Restores are tested automatically and the restored data is validated | S16 | POC 08 |
| R31 | Each service owns its data store behind an API | P9 | POC 12 |

## Security

| | Requirement | Source | Code |
|---|---|---|---|
| R32 | New code is written in a memory-safe language | P15 |  |
| R33 | Injection-prone operations are reachable only through typed safe APIs, checked in CI | P15 | POC 13 |
| R34 | Dependencies come from a curated repository with automated updates | P12, P15 | POC 14 |
| R35 | Workloads have their own identities; service calls are authenticated and authorised by the framework | P15 |  |
| R36 | Web security headers and TLS are set once, centrally | P15 |  |
| R37 | Infrastructure comes from reviewed blueprints, and drift is detected | P15 | POC 15 |
| R38 | Adoption of each guarantee is measured across the fleet | P15 | POC 13, 15 |

## The platform as a product

| | Requirement | Source | Code |
|---|---|---|---|
| R39 | Customer segments are named, and their jobs to be done are written down | P19 | POC 18 |
| R40 | Time to a first production deploy is measured and short | P18, P19 | POC 18 |
| R41 | Console, command line, infrastructure as code and agents share one API | P18 |  |
| R42 | The golden path has documented escape hatches; exemptions have an owner and an expiry | S18, P18 | POC 10 |
| R43 | The contract between platform and teams is published as resources, rights and responsibilities | P12 | docs |
| R44 | A scorecard reports user, system and business views | P19 | POC 18 |
| R45 | The platform has its own SLOs, stricter than its tenants’ | P16 | POC 16 |
| R46 | Old platforms are retired with a plan, brownouts and an off date | P19 | POC 18 |

## People

| | Requirement | Source | Code |
|---|---|---|---|
| R47 | Engineering work is at least half of an SRE team’s time | S1, S6, S13 | POC 09 |
| R48 | On-call load is capped and rotations are large enough to be sustainable | S6, S10 |  |
| R49 | Onboarding and training build confidence through practice | S5 |  |
| R50 | Platform teams have people with time allocated to support, writing and teaching | P24 |  |
| R51 | Internal documentation has owners and review dates | S4, P24 |  |

## AI

| | Requirement | Source | Code |
|---|---|---|---|
| R52 | Model endpoints have a quality objective alongside latency and availability | S20, P22 | POC 19 |
| R53 | Freshness, input drift and confidence are monitored and can page | P22 | POC 19 |
| R54 | Models are signed, registered with lineage, evaluated and canaried before serving | S20, P22 | POC 19 |
| R55 | Input and output guardrails run outside the model | P22 |  |
| R56 | Agents have least privilege, act only reversibly, and earn autonomy per class of action | S21, P22 | POC 11 |
| R57 | Generated code passes the same safe APIs and deploy gate as human code | P12, P15 | POC 13, 14 |
