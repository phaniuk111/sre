# Third pass: the book’s diagrams, and a full re-read of chapters 1–3 and 9

Study notes in my own words. Every figure in the book was looked at for this pass. The diagrams themselves are redrawn in the interactive course; here they are described in text. Sections are grouped by chapter.

## Chapter 1: What SRE is, and the model behind it

### Why the old pyramid was replaced

The first edition used a pyramid drawn by Mikey Dickerson in 2013, modelled on Maslow. Interviewers who read that edition may still have it in mind, so know both and know what changed.

|      | Dickerson’s hierarchy (2013)           | Hierarchy of production health (2nd edition)                     |
|------|----------------------------------------|------------------------------------------------------------------|
| Base | Monitoring                             | Sociotechnical foundations: culture and people                   |
| Then | Incident response, postmortems         | Situational awareness: SLOs, observability, toil tracking, goals |
| Then | Testing and release, capacity planning | Continuous preparedness: incidents, learning, training           |
| Then | Development                            | Infrastructure design: delivery, testing, data, capacity         |
| Top  | Product                                | Resilient products, then emergent reliability                    |

The book gives four reasons for the redesign. The lower layers were all reactive. Capacity planning had a layer of its own while data integrity was hidden inside “development”. Culture was assumed, not named. And nothing described the end state, where a platform makes services reliable by default.

> **The inverted pyramid.** You don’t have to finish one layer before starting the next. Grow the pyramid wider and taller at the same time. What you must avoid is a wide top on a narrow base: clever self-healing platforms run by a team with no blameless culture and no SLOs.

### Details from the full chapter

#### SRE is a role, not only a skill set

Any team can borrow SRE methods, and DevOps shows that works. The book still argues for a dedicated role, for three reasons.

- **It’s hard to do part-time.** Feature deadlines always win the week.
- **It needs depth and breadth.** An SRE sees across service boundaries, where most large outages live.
- **Reliability needs its own voice.** It is a long-term investment, and the next launch will override it unless someone is accountable for it.

The stance matters as much as the role: SREs are enablers, not gatekeepers.

#### Three advantages of the software mindset

- **Objective understanding**: Health is measured through SLOs and observability, and processes are derived from first principles: postmortems, STPA, CAST.
- **Automation**: Efficiency and consistency together. It also gives you a reason to simplify, because simple systems are easier to automate.
- **Dev and ops integrated**: One shared language and a feedback loop from production back into design.

That is why every SRE is expected to write code, even if on a given day the code is only a monitoring configuration.

#### Three ways to shrink an incident

1.  **Length**: Detect fast, mitigate fast
2.  **Frequency**: Follow through on postmortem actions
3.  **Scope**: Failure domains and graceful degradation

*Preparedness cuts impact along these three dimensions. On-call is a means to that, not the purpose of the team.*

#### What each upper layer contains

| Layer                 | What the chapter puts in it                                                                                                                                                                                                                                                                                                                     |
|-----------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Situational awareness | SLOs and observability, plus two things people forget: toil tracking (no exact number exists, so use outages, ticket throughput and a rough maintenance estimate) and business alignment through OKRs and feature velocity. Without the last one SRE gets sidelined.                                                                            |
| Infrastructure design | Six areas: release management (changes are the top cause of outages, so use incremental rollouts, trunk-based development and many small releases), configuration management (GitOps, feature flags), data, capacity (load balancing, throttling, DoS protection), production testing (probers, fault injection, load tests) and observability. |
| Resilient products    | Shrink the blast radius with failure domains, horizontal scaling with failover, and graceful degradation (a page that loads without profile pictures still works). Then simplify, above all by removing circular and unnecessary dependencies.                                                                                                  |
| Emergent reliability  | The platform makes whole classes of failure impossible. Where it can’t enforce, it monitors, for example by spotting a global push in the logs. Teams rarely break rules on purpose, so teach as well as block.                                                                                                                                 |

AI is missing from the pyramid on purpose. The authors treat it as something that cuts across every layer, which is why it gets its own part at the end of the book.

## Chapter 2: The value of reliability

### One hour of downtime, counted properly

The chapter’s most quotable table argues that a major outage costs 100 to 1,000 times its length in engineering time. Roughly, for one hour of serious downtime:

| Where the hours go                              | Engineer-hours |
|-------------------------------------------------|----------------|
| Operations team managing the outage             | 5–10           |
| Post-incident review, timeline and bug tracking | 10–20          |
| Internal communication and presentations        | 20–50          |
| Remediation: working through the repair items   | about 100      |
| Customer communication                          | about 100      |

On top of that, rollouts slow down for weeks afterwards because everyone is cautious. The same chapter has a simple worked example for an internal system: a finance outage that idles 400 people for two days at \$325 a day is \$260,000 before anyone counts the knock-on effects.

> **A number worth remembering.** Google’s research found that 53% of visitors give up on a task when a page takes more than three seconds to load. Slow counts as down.

### Details from the full chapter

#### The startup that deferred everything

A sidebar describes a SaaS company growing revenue 200% a year while putting off basic production hygiene. The bill arrived as twelve months of all-hands catch-up work. Uptime went from 99.84% to 99.999%, which is the difference between about an hour of downtime a month and a few seconds. The operations lead joked that the recovery plan had so many phases it ran out of letters.

The lesson for an interview: reliability debt compounds, and paying it later costs a year of feature work.

#### What to adopt, by stage

- **Early stage: the cheap five**: Automated tests, CI/CD (changes are the largest outage trigger at Google), basic observability, a simple incident process, and design reviews.
- **Mature organisation**: SLOs as a tool for strategic decisions, managing accumulated complexity, formal incident response with defined roles, and centrally maintained tools.

#### Six questions before you adopt SRE

1.  What are your biggest operational challenges?
2.  What resources do you have? That includes skills, and whether the culture will fall back to quick fixes.
3.  Can you start small?
4.  What is at stake if you’re unreliable?
5.  How do users interact with you? If they retry, short outages hurt less than long ones. A flash sale may still sell out during a blip and damage your reputation anyway.
6.  Is timing a factor, such as a peak season?

#### Smaller points that come up

- Not every Google system has SRE support. The mission-critical ones do, and SRE can hand a pager back.
- Traditional operations is rewarded for stability, so it resists change. SRE shares an error budget with developers, so both sides own the trade.
- The CFO’s argument: machines are fast and cheap, people are slower and far more valuable. One global load-balancing platform serves Search, Maps and YouTube.
- Reliability is a company-wide habit. Sales and marketing should warn engineering before a campaign. Google Meet’s growth during COVID is the example of business growth arriving without warning.

## Chapter 3: Trends in production: what the cloud changed

### How platforms evolved

1.  **About 2010 · Tickets**: A service desk, days or weeks of waiting, and a “wall of confusion” between dev and ops
2.  **2016–2026 · Self-service**: Internal developer platforms and golden paths. A “vending machine”: pick a template and get an instance with monitoring, security logging and backups already on
3.  **Next · Intent-based**: You declare a latency target or a budget. The platform picks tiers, isolates, migrates and throttles to meet it

*Governance moved with it: from auditing what humans did, to guardrails built into the system.*

The book names three things an intent-based platform has to get good at: filtering signals adaptively, carrying regulatory logic inside the platform, and treating energy and sustainability as constraints alongside cost.

#### Google’s production stack, with AWS equivalents

The chapter walks through Google’s environment. You won’t be asked to recite it, but being able to translate it shows you understand what each piece is *for*.

| Google                    | What it does                                                                                      | Closest on AWS                                                                   |
|---------------------------|---------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------|
| Borg                      | Cluster operating system: runs jobs made of tasks                                                 | EKS or ECS                                                                       |
| Colossus                  | Cluster file system under everything else                                                         | S3 and EBS                                                                       |
| Spanner                   | Globally consistent relational database                                                           | Aurora (global database), DynamoDB global tables                                 |
| Bigtable                  | Sorted key-value map at petabyte scale                                                            | DynamoDB, Keyspaces                                                              |
| Blobstore                 | Large immutable objects                                                                           | S3                                                                               |
| gRPC and Protocol Buffers | Typed RPC between services                                                                        | gRPC on ALB or VPC Lattice                                                       |
| GSLB                      | Load balancing at three levels: DNS by geography, service, and RPC                                | Route 53, Global Accelerator, ALB, VPC Lattice                                   |
| Piper                     | One repository for code and configuration                                                         | A monorepo with infrastructure as code (CDK, Terraform)                          |
| Push-on-green CI          | Tests run on production clusters; green builds ship                                               | CodePipeline with automated gates                                                |
| Monarch                   | Planet-scale time-series monitoring                                                               | CloudWatch, Managed Service for Prometheus                                       |
| Boq                       | Internal developer platform with conformance rules and built-in overload, retry and caching hooks | A platform team’s golden path: Backstage, Service Catalog, shared CDK constructs |
| BeyondCorp                | Zero trust: access by identity and device, not network                                            | Verified Access, IAM Identity Center                                             |

#### How the storage layers stack

1.  **Spanner · Bigtable · Blobstore**: Three services with different data models
2.  **Colossus**: One cluster file system under all of them
3.  **Byte storage**: Disks and flash

*After Figure 3-1. Blobstore even splits its own work: small objects go into Bigtable, large ones straight to Colossus.*

The design lesson is layering. Each service solves one problem and builds on the one below, so an improvement in Colossus reaches everything above it. The risk is the mirror image: a Colossus problem is everybody’s problem, which is why the lower a layer sits, the stricter its SLO has to be.

### Details from the full chapter

#### Capacity became a finance problem

On-premises, you bought for the peak and the hardware sat idle 51 weeks a year. In the cloud you rent elasticity for Black Friday. The catch is that capital expense turns into operating expense that can swing wildly if nobody watches it. That is the job FinOps does: commitments for the steady base, spot for work that can be interrupted, and tags so every team sees its own bill.

#### From the 2016 “fortress” to now

Ten years ago the unit was a hand-tended VM on a SAN, with configuration drift and a specialist team per layer. Three decouplings changed that. Separating storage from compute removed what the book calls the preallocation tax: you no longer pay for disks sized for a peak that may never come. Networking became software-defined and driven by identity.

Two forces shape the next decade. One is **digital sovereignty**: a single service may need to run under ten sets of national rules. The other is **autonomous optimisation**, where control loops trade performance against energy and cost on their own. Both push SRE away from allocating resources and towards governing policy.

#### Observability: components to context

- The single pane of glass is a myth. Use open standards so context flows between tools.
- Distributed tracing is now a basic primitive, not an advanced extra.
- Quality over quantity: SLOs are the primary signal, and cardinality needs discipline.
- Access should be open across teams. Telemetry silos are an antipattern.

#### Why RTO and RPO fall short

They are binary and reactive, like a stopwatch that only starts after a disaster, and their values often come from history or politics. They can’t describe a gray failure such as “30% slower for 10% of users”. An SLO can.

#### How Google’s own environment changed

- **Platformisation.** The P2020 programme set standards for CI/CD and observability. Boq gave Borg applications a paved road with conformance requirements.
- **Compliance shifted left.** Rules such as GDPR, the DSA and the DMA are written as policy-as-code and checked before deployment.
- **AI at scale.** More than 3.2 quadrillion tokens a month by mid-2026, accelerator use up fifteen-fold in two years, and machine learning used to predict hardware failures and tune cooling.

1.  **Data ingestion**: and processing
2.  **Training**: and experimentation
3.  **Deployment**: and serving
4.  **Observability**: Drift, decay, retraining

*The four stages of an AI pipeline. Each one needs its own reliability thinking, which chapter 20 picks up.*

## Chapter 5: Hiring, training and career management

### The Treynor curve

Ben Treynor Sloss drew Google’s hiring bar as a curve, not a line. A candidate who clears the software bar is a fit, and so is one who clears the systems bar. The interesting part is the middle.

> **Diagram.** Chart with software skill across and systems skill up. A curve joins the two hiring bars; candidates above the curve are hybrid SRE hires. After Figure 5-1. Someone slightly under both bars can still be a hire if the two skills together land above the curve. Below it, there isn’t enough of either.

This is why the interview loops differ but the job doesn’t. It also explains a line you can use about yourself: “I’m stronger on the systems side, and here is the software I’ve written to automate it.”

#### How scope grows with seniority

1.  **Reactive**: Handles what arrives
2.  **Proactive**: Prevents the next one
3.  **Comprehensive**: Owns a whole system
4.  **Long-term**: Plans across years
5.  **Directional**: Sets where the organisation goes

*After Figure 5-3. The move is from tactical to strategic. Promotion cases are easier to write when you can say which step you are working at.*

#### Growing your own hiring pipeline

Figure 5-2 charts a university outreach programme Google ran in Ireland over seven years. Internships and placements grow first, and full-time hires follow a few years later as interns return. Two points to take from it: get students in early, in their first or second year, because the bar for an internship is lower and it lets both sides try the job. And report short-term wins, such as applicant numbers and interns hired, because a seven-year payoff needs sponsors who stay interested. Much of the benefit showed up in under three years.

## Chapter 7: SRE engagement models

### A second worked example: the Azure playbook

The chapter includes Microsoft’s engagement playbook, which is useful because it attaches a measurable KPI to each phase. A service in phases 1 to 3 is “nascent”; 4 to 6 is “mature”.

| Phase | What is measured                                                                                          |
|-------|-----------------------------------------------------------------------------------------------------------|
| 1     | Compliance with security and quality baselines; security posture score                                    |
| 2     | Share of critical user journeys covered by an SLO; share of outages detected automatically                |
| 3     | 75th-percentile time to mitigate; incident volume and repeat rate; alert noise ratio and routing accuracy |
| 4     | Lead time, change failure rate, deployment frequency                                                      |
| 5     | Number of critical risks; age of the last threat model                                                    |
| 6     | Capacity plans kept up to date                                                                            |

Notice the order. It follows the hierarchy of production health: see the service first, respond well next, then deliver safely, then manage risk. If an interviewer asks how you would measure an SRE engagement, this table is a ready answer.

## Chapter 8: SLOs, error budgets and burn rate

### The error budget policy is a ramp, not a cliff

People often describe the policy as a switch: budget gone, features stop. The book’s figure shows something gentler and more useful.

> **Diagram.** Line chart. Reliability work stays low while the budget is healthy, climbs as the budget nears zero, and takes nearly all engineering time once the budget is overspent. After Figure 8-1. As the remaining budget falls, the share of engineering time spent on reliability rises through three zones.

Write your policy with all three zones. In the middle one, name the trade-offs explicitly: slower rollouts, a reliability item in every sprint, a second approver for risky changes. A freeze should be the last step of a ramp everyone saw coming.

> **Hyrum’s law and Hidalgo’s corollary.** Hyrum’s law says every observable behaviour of a system will be depended on by somebody. Alex Hidalgo’s corollary applies it to reliability: the level you actually deliver is an observable behaviour too. Run at 99.99% for a year against a 99.9% SLO and your users will build on 99.99%. That is the argument for controlled budget burn, and for checking in with consumers every quarter or two.

> **Code Yellow and Code Red.** Google’s names for an organised emergency. A Code Red is already causing major damage, or will within a day or two. A Code Yellow could cause outages or business problems over the coming quarter: feature work stops and a temporary team forms. An exhausted error budget on a critical journey is a common trigger for a Code Yellow.

## Chapter 9: Observability and monitoring

### From user goal to SLO

Server SLOs can be green while users can’t finish what they came to do. The book’s example is an email client whose send button is disabled: every API is healthy and nobody can send mail. The fix is to define SLOs from the user’s journey downward.

1.  **Goal**: “Stay in touch with my friends.” Why the user came. You can’t instrument this
2.  **Tasks**: “Send an email.” Steps towards the goal
3.  **Interactions**: Click compose, type, click send. The critical ones are very common or essential
4.  **Instrumentation**: Server SLI, client SLI, end-to-end SLI
5.  **SLOs**: Availability, latency, client-side success, quality

*After Figure 9-4. A critical user journey (CUJ) is a goal plus its tasks; tasks are built from critical user interactions (CUIs).*

- **Bad minute.** To roll several SLIs up into one journey SLO, call a minute bad if any SLI in the journey was bad in that minute.
- **The journey is a dimension.** A CUJ or CUI identifier travels with the request in trace context, so every metric can be sliced by journey.
- **Change supervision per journey.** Watch each journey across five kinds of change: server binary, server configuration, mobile app release (which can’t be rolled back), feature ramps and data updates.
- **A central registry** of journeys and an SDK give teams a well-lit path.

#### Case study: Maps and the “successful” failure

Maps has more than two billion monthly users. A server once returned well-formed responses built from malformed data, so searches “succeeded” with zero results. Server metrics saw nothing. The team wrote an invariant from the user’s side: the customer sees a non-zero number of valid results.

Two things followed that are worth telling in an interview. First, better detection looked like *more* outages for a while, because problems that had always been there became visible. Second, once the signal existed, canary rollouts that raised the zero-results rate paused themselves. The team then sold customer-centric monitoring to product leads as delivery speed: the supervision built during the emergency could now protect every new feature.

#### Client-side telemetry

1.  **Instrumentation**: In the app or browser
2.  **Uploader**: Batches and sends
3.  **Public endpoint**
4.  **Collector service**: Samples, validates
5.  **Storage**

*Server metrics can’t see failed DNS, an expired certificate, a crash, or retries hiding an error. The client can.*

| Trade-off                                                   | What to do about it                                                                                                                                              |
|-------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Batched uploads arrive late, with device clocks that drift  | Record both device and server time, and expect late events in pipelines                                                                                          |
| On-device storage fills up and events are dropped           | Dropping the oldest hides the trigger; dropping the newest hides the present. Report counts ingested, uploaded and dropped, with reasons, so you have error bars |
| A crash-looping app turns telemetry into a DDoS on yourself | Sample at the collector *and* push sampling down to clients                                                                                                      |
| The collector shares fate with the main service             | Isolate it, or you lose telemetry exactly when you need it                                                                                                       |
| Old builds never update                                     | Tag everything with build, release channel and OS or browser                                                                                                     |

YouTube uploads are the book’s example: server-side API availability looked high, and client-side instrumentation showed a noticeably worse experience.

#### Alerting on evidence, not on a single ratio

One error in twenty requests is a 5% error rate, and it is almost certainly noise. The book’s method treats each request as a trial, computes a confidence interval for the true error rate, and pages only when the **lower** bound is above the SLO threshold. The observed rate can cross the line many times without the alert firing (Figure 9-7 shows exactly this). The Labs station has a calculator for it.

For latency, compare against the service’s own past: group requests into cohorts by method, customer and workload shape, keep a 30-day mean and standard deviation, and alert on z-scores. “Slower than usual” is an implicit SLO that works across products.

#### What telemetry costs, and what you keep

Data loses value as it ages, so retention is a design decision. Google’s Horizontal Monitoring Data (HMD) collects a common set of series centrally, so a new service gets them without asking.

| Data                   | Kept in memory | Kept on disk                                                   |
|------------------------|----------------|----------------------------------------------------------------|
| Raw, minute-level      | Hours          | Weeks                                                          |
| Precomputed aggregates | Hours          | Full resolution for weeks, then 30-minute resolution for years |

Aggregation saves at least ten-fold, series nobody has read for months are phased out, and owners can extend retention if they have quota. On AWS the same thinking gives you CloudWatch metric resolution tiers, log retention per log group, S3 lifecycle rules for traces and logs, and cost allocation tags for chargeback.

#### Four questions before adopting an observability product

1.  How well supported is it?
2.  Does it conform to open standards such as those from the CNCF?
3.  Does it work on every platform you have: backend, mobile, web?
4.  What happens if you don’t adopt it?

Waze is the cautionary tale. It moved from an in-house library to OpenCensus to OpenTelemetry, the last migration took over a year, and overlapping systems confused developers. The team calls instrumentation a ten-year decision. Open standards let you keep the agent and swap the backend, but dashboards and alerts still have to be migrated.

#### Also in the chapter

- **Universal and horizontal alerts.** About a fifth of all SRE alerts at Google are universal ones every service inherits. Component owners also publish alerts for everything that uses their component, such as an auth library.
- **High-availability telemetry must come back fresh.** After a monitoring outage, serve the newest data first and relax completeness before availability. Monitoring must not depend on the services it watches.
- **eBPF** gives logs, profiles, network metrics and traces without code changes, in exchange for kernel-level permissions and less depth than hand instrumentation.
- **Privacy.** “Anonymous” per-region data is not anonymous when one customer is alone in a region. Classify data, minimise and redact, keep it in its locale, set wipe-out periods by type, and use one vetted SDK so teams can’t overshare.
- **Agents.** A trace shows what an agent was asked and what it answered, and says nothing about whether the answer was good. Quality needs its own signal.

### The knowledge graph, drawn

1.  **Product A**: Where users notice
2.  **Service**
3.  **Service**
4.  **Shared dependency**: Where it started

*After Figures 9-1 and 9-5, simplified. The book’s versions show whole product areas as nodes, with normal call paths in one colour and the path of a performance problem in another.*

This is what “product-focused observability” looks like in practice. An investigator sees which products are affected and where the degradation entered, without needing to be an expert in every service in between. It is also the structure an AI assistant needs: a graph it can walk is far more useful to it than a wall of dashboards.

On AWS you can get part of the way with X-Ray or Application Signals service maps, and resource tags that name the product each service belongs to. The tags are the part teams skip, and the part that makes the graph answer product questions.

> **What the Maps failure looked like.** Figure 9-6 is a screenshot worth picturing: a search for “coffee” in the middle of San Francisco, and Maps replying that it can’t find any. Every server returned success. That one image is the argument for measuring from the user’s side.

## Chapter 11: Learning from incidents

### Rasmussen’s boundaries, drawn

Of the safety-science models in this chapter, Rasmussen’s is the one that needs a picture. A team works inside a space with three edges. Go past the first and the business fails. Go past the second and people burn out. Go past the third and you have an accident.

> **Diagram.** A space bounded by economic failure, unacceptable workload and acceptable performance. Arrows show cost pressure and least effort pushing the operating point towards the performance boundary, and safety culture pushing back. After Figure 11-1. Two steady pressures move the operating point away from the cost and workload edges, which means towards the accident edge. The margin shrinks without anyone deciding to shrink it.

This explains “drift into failure”. Nobody chose to be unsafe. Each shortcut was a sensible answer to cost or workload pressure, and each one that didn’t cause an outage looked like proof it was fine. The counter-force has to be deliberate and continuous: error budgets, game days, postmortem follow-through. A poster campaign after an outage pushes back for a week.

## Chapter 12: Safety engineering with STPA and CAST

### The control loop, drawn

> **Diagram.** A controller box above a controlled-process box. A control action arrow goes down, a feedback arrow goes up, and requests and responses pass through the process. After Figure 12-3. Every STPA and CAST analysis is built from loops like this one. Most outages come from the two arrows and the mental model, not from the boxes.

Read the picture as four places to look for trouble: the control action can be wrong or late, the feedback can be missing or misleading, the controller’s mental model can be out of date, and the process can behave in a way nobody modelled.

### Two ways to explain the same outage

1.  **A change with a bug is submitted**: Fix: add a test
2.  **The release includes it**: Fix: run tests on every build
3.  **It rolls out to production**: Fix: progressive rollout
4.  **Services crash**: Fix: crash alerts

*After Figure 12-1. The chain-of-events view. Each link gets a patch, and each patch is reasonable.*

The trouble is that the chain only describes this bug. The systems view in Figure 12-2 asks a different question at each step: what *influenced* the decision?

| Controller        | Factors that shaped its decisions                                    | What followed                                             |
|-------------------|----------------------------------------------------------------------|-----------------------------------------------------------|
| Engineers         | Missing tests, time pressure, tool limits, code complexity, skills   | The change was submitted, rolled out, and not rolled back |
| Build system      | Missing tests, flaky or skipped tests, no QA acceptance step         | The bug was included in the release                       |
| Deployment system | Global rollouts, limited telemetry, complex production configuration | Production crashed                                        |

Notice that software systems are treated as decision-makers too. Fixing “time pressure” or “global rollouts” prevents many future outages, including ones with entirely different bugs.

#### A worked unsafe control action

In the Maps example a geospatial data specialist asks for approval, and a review team’s approver consults subject-matter experts before answering. One unsafe control action falls straight out of the diagram: the approver approves when the experts have *not* approved. Nothing failed. The structure allowed it. The hazard that analysis is protecting against is stated plainly: the published map disagrees with the real world.

#### How CAST layers an incident

1.  **Adverse events**: Bug introduced, buggy release deployed, not rolled back, service crashed
2.  **Controllers’ behaviour**: What each person or system did, and why it made sense to them
3.  **Causal factors**: Global rollouts, missing tests, limited telemetry, time pressure, tool limits
4.  **Systemic factors**: Management of change, safety culture, safety information, communication, environment

*After Figure 12-9. A postmortem that stops at the first box fixes one bug. Recommendations aimed at the last box fix a class of them.*

> **Why bother before launch.** The book’s Figure 12-11 makes the economic case in one picture: most design flaws are introduced during design, most are found in testing or production, and fixing them is most expensive by far in production. Ben Treynor Sloss’s summary of STPA is that it is like being told about your outages before they happen, so you can choose which to fix and which to live with.

#### The misnamed cities, in one picture

1.  **Census dataset arrives**
2.  **Evaluated**: By sampling
3.  **Published to Maps**
4.  **Users report wrong names**
5.  **Data rolled back**
6.  **Fixed**

The data was too large to review by hand, so the specialists checked four states where they had local knowledge: Washington, California, Texas and New York. The six states with wrong city names were Montana, Kansas, Indiana, Kentucky, Tennessee and Georgia. Figure 12-7 puts both sets on a map and they don’t overlap at all.

A classic postmortem calls that imperfect sampling and stops. CAST asks why sampling four states seemed sufficient, who knew the sample wasn’t representative, and what feedback would have shown it. That is how the same incident produced 22 recommendations where the postmortem had 8.

The final figure in the chapter repeats the design-flaw grid with one arrow added, labelled STPA, pointing from production back to design. The whole method is that arrow: find the flaw where fixing it is cheap.

## Chapter 13: Automation, tooling and toil

### Where automation fits in the incident loop

1.  **Detect**
2.  **Triage**
3.  **Mitigate**
4.  **Resolve**
5.  **Learn**
6.  **Remediate**: Fix the class, which feeds detection

*After Figure 13-2. Automation can help at every stage. Start where humans are slowest and the action is safest, which is usually detection and generic mitigation.*

Two footnotes from the chapter are worth carrying into an interview. Static thresholds force a trade between false alarms and missed problems, so the more ambiguous the signal, the more hand-tuning it needs: that is toil with a mathematical cause. And automation has limits of its own. Google’s automatic capacity tool never worked for one large traffic system because the configuration grew big enough to break the solver.

#### Is it worth the time?

For the pure time-saving case, the chapter points to the well-known xkcd chart (number 1205) that tells you how long you can spend automating a task before you lose more time than you save, counted over five years. The sum behind it is simple enough to do in an interview: time saved per run × runs per day × 1,825 days.

| You save   | How often      | Break-even over five years |
|------------|----------------|----------------------------|
| 30 seconds | 50 times a day | about 760 hours            |
| 5 minutes  | once a day     | about 150 hours            |
| 1 hour     | once a month   | 60 hours                   |
| 5 minutes  | once a year    | 25 minutes                 |

Then say why the chart is not the whole answer, because the book does. Time is only one of four reasons to automate. A task you run once a year in an emergency fails the chart and may still be the most valuable thing to automate, because consistency under stress and scale matter more than minutes.

## Chapter 14: Testing for reliability

### The hierarchy of tests

> **Diagram.** A four-layer pyramid: unit tests at the base, then integration, system, and resilience tests at the top. After Figure 14-1. The familiar test pyramid with one more layer on top: resilience testing, where you break things on purpose (fault injection, DiRT, load tests).

#### A rollout rule of thumb

1.  **0.1%**: Start here
2.  **1%**: Ramp fast at the low end
3.  **10%**: A day per step
4.  **50% → 100%**: Slow down at the high end

*From a footnote in the chapter: begin at 0.1% of traffic and grow roughly ten-fold every 24 hours, moving across server locations as you go.*

The reasoning is about exposure. At 0.1% a bad release hurts almost nobody, so move quickly. At 50% a bad release is a major outage, so bake longer. On AWS this is a CodeDeploy or AppConfig deployment strategy with a bake time and a CloudWatch alarm that triggers rollback.

> **Client-focused supervision.** The book’s Figure 14-3 shows why you watch a rollout from the caller’s side. A frontend calls two backend tasks. The one on the new version returns bad data with a success code, and the user sees an error. The backend’s own dashboards look healthy, and only the client-side view shows the failure.

One more honest detail: the old claim that a bug costs 100 times more to fix in production is more nuanced than the slogan. The chapter notes it is closer to 100 to 1 for severe defects and about 2 to 1 for minor ones. Use the nuanced version and you will sound like you’ve read the source.

## Chapter 15: Capacity planning

### The iron triangle of capacity

> **Diagram.** A triangle with performance, cost and reliability at the corners and business goals in the centre. After Figure 15-1. Capacity planning is choosing a point inside this triangle on purpose. Pull one corner and the other two move.

Spare capacity buys reliability and costs money. Running hot saves money and costs latency under load. There is no free corner, which is why the chapter keeps repeating that the target is a business choice.

#### Making capacity fungible

Stranded capacity is capacity you own in a place or shape you can’t use. The chapter’s figures show two ways out. Work that tolerates delay can fill the troughs of local demand, which lowers the global total. And you can make workloads easier to move:

- **Architect for constraints**: Break a rigid application into services that scale on their own and don’t care which region they run in.
- **Shift work in time**: Batch, training and backfills run when interactive demand is low.
- **Improve connectivity**: A better network lets demand in one place use supply in another.

On AWS: Spot and Batch for time-shifted work, Auto Scaling groups with several instance types so you aren’t tied to one, and multi-Region designs so demand can follow supply.

### Case study: the Google Meet loop

When COVID lockdowns began, demand for Meet grew faster than any forecast. Figure 15-7 shows the process the team ran every day. It is the best single diagram in the chapter for an interview, because it turns “we scaled” into a method.

1.  **Review the inputs**: Customer onboarding and promotions, lockdown trends, forecast models, usage trends
2.  **One question**: Do we have enough for the load we expect a week from now?
3.  **Yes**: Wait a day and ask again
4.  **No**: Start the four workstreams

- **Capacity**: Are there more raw resources we can turn into capacity? If not, find some.
- **Dependencies**: Can every system we depend on take the extra load? If not, find workarounds.
- **Bottlenecks**: Can we remove artificial limits to use what we have better? Then find the next limit.
- **Control knobs**: Can we change the system quickly to head off a large outage? If not, build more escape hatches.

Everything the four workstreams produce goes through a fifth, production changes, whose only job is to deploy safely. Then the loop starts again. The one-week horizon is the detail to remember: short enough to forecast, long enough to act.

#### Why pooling works

Figure 15-4 plots resource use for four regions over three days. Each has a daily peak, and the peaks fall at different hours. That is the whole reason a shared pool needs less than the sum of its parts. Figure 15-3 shows how Google layers it: physical CPU, memory and drives feed foundational pooled services (compute and memory in Borg, disk in Colossus), and those feed composite services built on top, such as Bigtable.

## Chapter 16: Data management

### RPO, RTO and RWO on one timeline

> **Diagram.** A timeline of backups, an incident and a restore. RWO spans from the oldest retained backup to the latest. RPO spans from the latest backup to the incident. RTO spans from the incident to full restoration. After Figure 16-3. Three objectives, three different stretches of time. RTO is cumulative: the clock starts at the incident, so slow detection spends your recovery time before you’ve begun.

The figure also marks a point of no return. If the corruption is older than your oldest retained backup, no restore can help, which is why RWO has to be longer than your worst realistic time to notice a problem. Silent corruption found after 40 days with 30 days of backups is unrecoverable.

#### Incremental or differential?

|                               | Incremental                                        | Differential                         |
|-------------------------------|----------------------------------------------------|--------------------------------------|
| Each backup holds             | Changes since the last backup of any kind          | Changes since the last *full* backup |
| To restore Wednesday you need | The full backup plus Monday, Tuesday and Wednesday | The full backup plus Wednesday       |
| Backup size                   | Smallest                                           | Grows through the week               |
| Restore                       | More steps, more that can go wrong                 | Faster and simpler                   |

This is an RPO-against-RTO trade in miniature: incrementals are cheap to take often, differentials are quick to restore. AWS Backup takes incremental backups for most services and handles the chain for you, but the trade still shows up in restore time, so measure it with a restore test.

> **Integrity outranks recovery.** The chapter describes Bigtable’s stance: recover as much as possible before declaring data lost, but never at the price of integrity. The team must be able to say that no person compromised user data on the way, and exceptions need senior engineering, customer and legal approval.

#### Legal is not the same as right

|                  | Lawful good                                                        | Lawful neutral                                 | Lawful evil                                                   |
|------------------|--------------------------------------------------------------------|------------------------------------------------|---------------------------------------------------------------|
| With users’ data | Follows the law and puts the user’s interest first, even at a cost | Follows the law, makes no sacrifices for users | Follows the law and uses every permitted advantage for itself |

The chapter borrows the alignment grid from Dungeons & Dragons (Figure 16-1) to make one point: all three columns obey the law. Aim for the first. Its test is practical: if you use data in a way the user didn’t ask for and only you benefit, think about how they would react on finding out.

## Chapter 17: Designing for resilience

### Two pictures from the chapter

- **Region A · zone 1**: 25% of capacity
- **Region A · zone 2**: 25% of capacity
- **Region B · zone 1**: 25% of capacity
- **Region B · zone 2**: 25% of capacity

After Figure 17-1: two regions with two zones each. Lose a zone and you lose a quarter; lose a region and you lose half. So “N+1” is not a number you can state without saying which failure domain you mean. Sized to survive a zone, each remaining zone must take a third more. Sized to survive a region, each region must carry everything.

Figure 17-2 shows incident severity growing from normal, to emergency, to disaster, which is the same three-step scale as the incident modes above. The practical point is that the tooling for each step must depend on less than the step before it.

> **Risk register.** For rare, severe risks the chapter suggests a simple register: for each risk, its probability, its impact, an owner and a mitigation. It turns “what if a region disappears?” from a debate into a list someone is accountable for.

## Chapter 18: Platform engineering in SRE

### The effectiveness zone

> **Diagram.** Chart with consequence severity across and control strength up. A diagonal band is the effective zone. Above it controls are too restrictive; below it there is too little control. After Figure 18-2. Match the strength of a guardrail to the cost of getting it wrong. Controls are effective along the diagonal.

A hard block on a typo-level risk teaches people to route around the platform. A gentle hint on an action that can delete production data relies on nobody ever having a bad day. When a team complains that a guardrail is annoying, place it on this chart before arguing.

#### How far has a practice been built into the platform?

1.  **0 · YOLO**: Nothing in place
2.  **1 · Ad hoc**: Each team does it its own way
3.  **2 · Guided**: Documented best practice
4.  **3 · Engineered**: Built into the paved path
5.  **4 · Assured**: Enforced and verified by the platform

*After Figure 18-3. A typology for any one quality attribute, such as “safe rollouts” or “backups”.*

“Shift down” means moving a practice from type 2, where every feature team has to know and do it, to type 3 or 4, where the platform does it. The chapter’s first figure draws this as a line: assurance moves from above the line (feature teams) to below it (the platform).

> **Build horizon.** One of Google’s quieter guardrails: binaries older than roughly six months are not allowed to run. Nobody has to chase teams to pick up security fixes, because standing still stops being an option. It is a good example of changing the game so the safe choice is the easy one.

## Chapter 20: How SRE supports AI

### Three pictures from the chapter

#### The model release pipeline

1.  **Develop and version**: Model, prompt and config together
2.  **Qualify automatically**: Platform checks, then model evals, then simulated user journeys
3.  **Readiness gate**: Fail and it goes back
4.  **Progressive rollout**: Canary
5.  **Serve and monitor**: Feedback returns to development

*After Figure 20-2. The same shape as a software release, with one extra kind of test: does the model still give good answers?*

The qualification step has three layers on purpose. Infrastructure checks ask whether the model runs at all on this hardware. Evals ask whether its answers are good. Journey simulation asks whether the product built on it still works. A model can pass the first two and fail the third.

#### Why idle accelerators are expensive twice

> **Diagram.** Curve of power against machine utilisation, starting well above zero, rising steeply, then flattening. After Figure 20-4. Power rises steeply at low utilisation and flattens at the top. Going from 30% to 35% costs far more power than going from 75% to 80%.

So a half-idle fleet wastes the hardware and still pays most of the power bill. Run fewer machines hotter, and turn the rest off, since shutting down is the only way to remove idle draw.

#### Securing agents: two layers and a test loop

- **Runtime policy enforcement**: Hard limits on what the agent is allowed to do, checked outside the model. Dependable, because it doesn’t rely on the model behaving.
- **Reasoning-based defences**: A hardened base model, classifiers and safety fine-tuning. Flexible, but probabilistic.
- **Continuous assurance**: Regression tests, variant analysis, red teams and human reviewers keep both layers honest.

After Figure 20-5. The interview line: never let the model be its own only guardrail. On AWS that means IAM policies and service control policies as the hard layer, Bedrock Guardrails as the reasoning layer, and evaluation jobs as the test loop.

> **Isolation is more than memory.** A footnote warns that sharing accelerators between models needs isolation of high-bandwidth memory, interconnect bandwidth and duty cycle. Otherwise one model’s prefill phase can starve another model’s decoding, and a noisy neighbour shows up as someone else’s latency.

#### Planning accelerator capacity

1.  **Demand**: Organic growth plus inorganic: launches, model changes, new hardware generations
2.  **Forecast**
3.  **Order or rebalance**: Periodic orders, or move supply across the fleet
4.  **Allocate**: A footprint and sizing matrix, with redundancy and location rules
5.  **Deploy**: Moves and resizes
6.  **Monitor**: 7-day 95th-percentile occupancy against targets

*After Figure 20-3. Monitoring feeds the next forecast. The loop is the ordinary capacity loop from chapter 15; what changes is that supply takes months to arrive and can’t be bought on demand.*

## Chapter 21: How AI supports SRE

### The safety loop for an agent with production access

> **Diagram.** Flow: an AI agent proposes an action, a risk assessment engine routes it either to a human approval queue or to an atomic execution manager, and the outcome feeds back to improve the agent. After Figure 21-1. Every proposed action is scored for risk before anything runs. Low-risk actions go straight to an executor that can undo them; high-risk ones wait for a person.

- The agent sends its **reason** with the action, so a reviewer or an audit can check the thinking, not only the command.
- **Progressive authorisation**: as a class of action proves safe, it moves from the approval queue to automatic execution.
- The executor treats each action as a **transaction**: do it, validate the result, roll back if validation fails. Destructive migrations need extra design work to be reversible at all.
- Below a confidence threshold, the system should not show the suggested mitigation to the on-caller. A weak suggestion during an incident is worse than none.

#### What an investigation agent actually does

1.  **Plan**
2.  **Read server errors**
3.  **Fetch job details**
4.  **Check for anomalies**: Is this transient?
5.  **Is an incident open?**
6.  **Find the owner**
7.  **Escalate**: To the right developer

*After Figure 21-4, shortened. Each step is a tool call a human on-caller would also make. The value is doing all of them in seconds, in the same order every time.*

#### Why anomaly detection is harder than the slide suggests

- **The ideal**: A flat, predictable baseline and one clean spike. Any threshold finds it.
- **The reality**: A noisy line shaped by a feature launch, a viral search topic, a local ISP outage and a regional traffic migration, all in the same window.

After Figure 21-2. This is why the chapter argues for models that take context as input. A threshold can’t tell a launch from an outage. A system that knows a launch was scheduled can.

#### Grading the agent: LLM as judge

Figure 21-5 shows how Google evaluates its investigation agent. A second model scores each run against labelled incidents on two questions, was the **diagnosis** right and was the **mitigation** right, and writes a critique. A failed run also records the failure mode, the step where it went wrong, and why.

The example failure is instructive: the agent had a tool for correlating failures with recent rollouts, didn’t call it, and followed a log line about an old bug instead. It missed the chance to roll back. That is exactly the mistake a tired human makes, and having it written down per step is what lets you fix the prompt or the tool order.

On AWS the equivalent is a Bedrock evaluation job with a judge model, run against a set of past incidents every time you change the agent’s prompt, tools or model.
