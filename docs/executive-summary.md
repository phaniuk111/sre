# Executive summary: four books

*Synthesis (pass 2) of the chapter summaries in `docs/chapters/`. S8 means SRE book chapter 8; P15 means platform book chapter 15 in the final numbering; M = Mastering Prometheus, G = Observability with Grafana.*

## The books in one paragraph each

**Site Reliability Engineering, 2nd Edition** describes how to run software so that it is as reliable as its users need and no more. It treats operations as an engineering problem, makes reliability measurable through service level objectives and error budgets, and organises everything else as a pyramid, the hierarchy of production health: culture at the base, then awareness, preparedness, infrastructure design, resilient products and, at the top, platforms that make services reliable by default.

**Platform Engineering at Google** starts where that pyramid ends. Its claim is that security, reliability and efficiency can’t be delivered by asking every developer to be careful. They have to be moved down into the languages, libraries, pipelines and infrastructure that all code is built on, so that experts solve each problem once and every team inherits the result. Only ten of its thirty-one planned chapters are published.

**Mastering Prometheus** (Hegedus, 2024) goes underneath the query language. It explains how the time series database stores samples, how discovery and relabeling decide what is scraped, how Alertmanager routes and groups, and then how to scale: sharding, high availability, remote storage, Thanos, mixins, CI for rules, SLOs and OpenTelemetry. Its theme is that Prometheus is simple until it isn’t, and that most trouble is cardinality.

**Observability with Grafana** (Chapman and Holmes, 2024) is the wider view: logs with Loki, metrics with Mimir and Prometheus, traces with Tempo, collected by OpenTelemetry and joined up in Grafana. Its second half is about running observability for an organisation: dashboards built for a person and a question, incident management, automation, platform architecture, real user monitoring, profiling, load testing and the DevOps life cycle.

## What the SRE book argues

- **100% is the wrong target.** Pick a target from what users need, and treat the gap as a budget to spend on change. (S2, S8)
- **Culture comes first.** Blameless learning, psychological safety and sustainable on-call are the base of the pyramid, not a soft extra. (S1, S4)
- **Measure from the user’s side.** SLOs belong to user journeys, alerts fire on how fast the budget burns, and low-traffic services need statistics, not thresholds. (S8, S9)
- **Mitigate before you understand.** Clear roles, generic mitigations and practised emergency modes shorten incidents more than better diagnosis does. (S10, S17)
- **Accidents are control problems.** STPA and CAST replace the hunt for a root cause with the question of why the system allowed the unsafe action. (S11, S12)
- **Changes cause most outages.** So test configuration like code, roll out progressively, compare a canary with a control, and roll back automatically. (S14, S17)
- **Shift down.** The durable fix for a class of failure is a platform that makes it impossible or handles it by default. (S18, S23)
- **AI cuts both ways.** AI systems need quality as a reliability signal, and AI operators need autonomy that is earned, bounded and reversible. (S19–S21)

## What the platform book argues

- **Shift down, not only left.** Shifting left finds a problem earlier and leaves it with the developer. Shifting down makes the platform responsible. (P15, P16)
- **Conformity buys leverage.** The more an ecosystem limits choice, the more liability it can carry for its users. Make that trade explicit with resources, rights and responsibilities. (P12)
- **Coupling is a decision.** It buys efficiency, performance, atomicity and traceability and costs reuse, extensibility, robustness and choice. The danger is coupling nobody chose. (P9)
- **Layers move at different speeds.** Experiments and products are fast; infrastructure, directives, culture and law are slow. Fast layers propose and slow layers decide. (P10)
- **If it isn’t secure, it shouldn’t compile.** Wrap each risky operation in a safe abstraction so the vulnerable program can’t be written, then carry the same idea into builds and deployment. (P15)
- **SRE is the blueprint; the platform is the machinery.** Put into the platform whatever has a wide blast radius, needs rare expertise or fails catastrophically. (P16)
- **One optimisation, every team.** Shared foundations let you see the whole fleet and fix the biggest consumer once, on by default. (P14)
- **A platform nobody uses is worth nothing.** Design the experience, run the platform as a product, and measure adopters against non-adopters. (P18, P19)
- **AI amplifies what is already there.** Good platforms and current documentation make assistants useful; poor ones make the mess arrive faster. (P22, P24)

## What the two observability books add

- **Cardinality is the cost.** Every label value is a new series in memory, in the index and on the bill. Limit it at the scrape, review it in CI, and keep IDs out of labels. (M3, M7, G4, G15)
- **Know what rate() really does.** It is reset-aware and extrapolates to the window edges; use $__rate_interval and at least four scrape intervals. (M3, G5)
- **Alerting needs routing, not just rules.** Group, inhibit and silence in Alertmanager; send every Prometheus to every Alertmanager; add a dead man’s switch. (M5, M6, G9)
- **Scale by federation of storage, not of servers.** HA pairs with a replica label, then remote write or Thanos for global queries and retention. (M6, M9, M10)
- **Treat monitoring as code.** Mixins, unit-tested rules, Pint in pull requests, dashboards and alert rules in Terraform. (M11, M12, G10)
- **Burn-rate SLO alerts are generated, not hand-written.** Request-based for steady traffic, window-based for low traffic. (M13, S8)
- **Each signal stores different things.** Numbers in metrics, events in logs with few labels, high-cardinality context in traces; link them with exemplars and trace IDs. (G4, G5, G6, G11)
- **Collect with a topology.** Node agents, one cluster agent and a gateway that does tail sampling and span metrics, with buffers sized for outages. (G10, G11, M14)
- **Observability runs through the life cycle.** Local stacks while coding, SLO thresholds in load tests, annotations and automatic verification at deploy, RUM and profiles in operation. (G12, G13, G14)

| Idea | In SRE or platform book | In the observability books |
|---|---|---|
| SLOs and burn rate | Error budgets, multi-window alerts, low-traffic statistics (S8, S9) | Generated recording and alert rules, window-based SLOs, Pyrra and Sloth (M13) |
| Golden signals | Latency, traffic, errors, saturation everywhere (S9, P16) | Golden signals, RED and USE; dashboards built around them (G8, G9) |
| Incident roles | Commander, operations, communications (S10) | Commander, communications, technical lead, plus gold–silver–bronze (G9) |
| Configuration as code | Config is tested and rolled out like code (S14, P15) | Rule unit tests, Pint, mixins, Terraform for Grafana (M11, M12, G10) |
| Safe change | Canary analysis and automatic rollback (S14, P16) | Deployment annotations and verification queries in the pipeline (G14) |
| Fleet-wide profiling | One profiler shows the costliest shared component (P14) | Continuous profiling with Pyroscope, eBPF or SDKs (G13) |
| Platform SLOs | The platform needs stricter objectives (P16) | The observability platform needs its own SLOs and a disaster plan (G11, G15) |

## Where the two books meet

| Idea | In the SRE book | In the platform book |
|---|---|---|
| Reliable by default | Emergent reliability, the top of the pyramid (S1, S18) | The whole thesis: quality attributes as properties of the platform (P12, P15, P16) |
| Budget for risk | Error budgets and a policy with three zones (S8) | Risk profiles: the budget sets the deployment policy automatically (P16) |
| Design for human error | Blameless postmortems, STPA and CAST (S11, S12) | Safe abstractions and guardrails that make the mistake impossible (P15) |
| Make the right way the easy way | Golden paths over mandates; the effectiveness zone (S18) | Path of least resistance; “friction is a directive” (P12, P18) |
| Hyrum’s law | Users depend on the reliability you actually deliver (S8) | Hidden dependencies block change; randomise what you don’t promise (P9, P14) |
| Safe change | Canaries, progressive rollout, config testing (S14, S17) | Canary analysis as a platform gate; signed artifacts; blueprints (P15, P16) |
| Break the rules safely | Emergency modes with independent fallbacks (S17) | Break-glass: permitted, logged, alerted, reviewed (P16) |
| Sublinear scaling | Cost grows more slowly than the service (S2) | Cost of each capability paid once and amortised (P14, P16) |
| AI | Earned, reversible autonomy for agents (S21) | Guardrails as a containment field for generated code (P12, P15) |

The difference is the point of view. The SRE book is written from the seat of the people operating services. The platform book is written from the seat of the people building what those services stand on. In an interview, the strongest answers use both: name the principle, then say which platform mechanism makes it the default.

## How to turn this into interview answers

1. **Principle.** One sentence, in your own words.
2. **Mechanism.** The concrete thing that enforces or measures it.
3. **AWS.** Which services you would use.
4. **Evidence.** One number or one story from the books or from your own work.

Example: “We shouldn’t rely on reviewers to catch SQL injection. I’d wrap the database driver in a typed query API and fail the build on raw queries. On AWS that is a wrapper over the RDS Data API and a CodeBuild check. Google reports no SQL injection in protected applications for over ten years with this approach.”

## What this summary does not cover

- Twenty-one chapters of the platform book are not published yet, including the ones that define ecosystem types, shifting down and golden paths.
- SRE appendices E and F were read once, not twice. Citation-only footnotes in the platform book were skipped.
- These are study notes in my own words. They don’t replace either book.
- The two Packt observability books were read in full once, figures included; corrections to their examples are noted in the lessons and POCs.
