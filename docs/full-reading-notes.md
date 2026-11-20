# Second-pass study notes: what a full reading of every chapter adds

Case studies, numbers and named models from *Site Reliability Engineering, 2nd Edition*, written in my own words. They complement the chapter summaries in the [interactive study guide](https://claude.ai/artifact/Q35uEdK1hrKUhbZ15vWvVy) and [aws-concept-map.md](aws-concept-map.md). Each section ends with an interview angle.

## Part I · culture, people and organisation

### Chapter 4: Culture: measuring it, and changing it through behaviour

#### Seven elements, two foundations

The chapter rests everything on two foundations: put the user first (which is *not* the same as reliability at any cost) and treat reliability as a core value that's rewarded like a feature. On top sit seven cultural elements: a data-driven mindset, collaboration and shared responsibility, continuous learning, blamelessness, psychological safety, trust and empowerment. If you're asked "what does a good SRE culture look like?", list the two foundations first and then give one concrete practice per element.

#### Data-driven means measuring the process too

Google noticed postmortems were being written late and their action items left open, so it put SLOs on the postmortem process itself: a maximum time to the first draft and to publication, with dashboards and reports to management. Publication got faster, more action items closed, and repeat incidents with the same root cause dropped. Three incident-health metrics come up repeatedly: the share of incidents that weren't actionable (noisy monitoring), the share detected manually by users or other teams (weak SLIs or coverage) and pages per incident (an on-caller drowning in alerts). On the people side they track on-call time and how often on-callers make manual production changes, aiming for nearly zero.

#### Blame awareness and just culture

Blamelessness is the default, but the book goes further with **blame awareness**: admit that blaming is a natural reflex, then ask why the action made sense to the person given what they knew and the pressure they were under. Watch for the fundamental attribution error (others' mistakes are character flaws, ours are circumstances) and hindsight bias. Blameless doesn't mean nobody is accountable. Postmortems still check whether engineering standards were met. For regulated industries that worry about malice, the **just culture** model separates honest mistakes, at-risk behaviour, reckless conduct and criminal acts. Only the last two justify discipline, and even then you still ask what least-privilege, auditing or approval control should have made the act impossible.

#### Trust, safety, empowerment

Psychological safety (Amy Edmondson's definition) is what makes people escalate early and ask awkward questions like "have we ever tested a restore?". Managers build it by admitting what they don't understand and by not reacting with feigned surprise to questions. Repairing trust after one tense exchange takes roughly five to seven positive ones, which is why distributed teams invest in meeting in person. Empowerment at Google means any engineer can propose a code change anywhere, any team can request a postmortem (near misses included) and assign action items to other teams, and SRE can push back on launches or, in extreme cases, hand the pager back.

#### DORA and Westrum

Westrum's three cultures differ in how information flows. In **pathological** cultures messengers are punished, failure leads to scapegoating and new ideas get crushed. In **bureaucratic** ones messengers are neglected, failure leads to "justice" and new ideas cause problems. In **generative** ones messengers are trained, risks are shared, failure leads to inquiry and new ideas get implemented. DORA found that teams strong in modern operations practices are 1.4× more likely to report better delivery and operational performance and 1.8× more likely to report better business outcomes. Teams with good documentation are 3.5× more likely to adopt SRE practices.

#### Learning → confidence → behaviour → culture

You change culture by changing what people do; their thinking follows. Training builds confidence, and you can measure culture cheaply by asking people to rate their confidence in action-oriented tasks on a **grounded scale**: no idea, could do it with help, could work it out from docs, could do it from memory, could teach it. Survey before training, straight after, at one month and at six. People who went through SRE onboarding scored 15 to 49 percentage points higher on top-box confidence than those who did general onboarding. When you design training, think about three groups: the change-curious, the change resisters ("what's in it for me?") and change champions (experienced hires who can tell success stories).

#### Brownfield and greenfield

For an existing service, the sequence is: train all stakeholders together, pick one service that matters and has an engaged team and code access, assess its maturity, collect a baseline SLI on a critical user journey, then hold **the crucial conversation** with the business: is today's reliability good enough, and what does slow, broken or down cost us? Engineers tend to underestimate what's needed and business stakeholders tend to overestimate it. Set two or three realistic SLOs (if you're at 99.5% today, don't promise 99.999%), start blameless postmortems, then publicise the wins. For a new service, the SLO is a **design input**: 99.99% pushes you away from single-homed designs and towards redundancy, idempotent operations for retries, instrumentation built in as a feature, and load and chaos testing. Swap fixed-cadence releases ("every other Tuesday") for SLO-gated ones.

> Interview angle: "Our new SRE team keeps getting blamed after outages. What would you change?"
>
> Name the culture type (likely bureaucratic or pathological), introduce blameless and blame-aware postmortems with an independent author, measure the postmortem process itself, get an executive to model the behaviour, and separate the rare reckless or malicious case using just culture, so people stop fearing that every mistake will be treated like one. Warn that renaming an ops team "SRE" without changing incentives poisons the idea for years.

### Chapter 5: Hiring, training and careers

#### What predicts a good SRE

Breadth predicts success better than depth, so Google hiring committees are told to look for strengths rather than gaps, and to remember that one bad interview may say more about the interviewer. Most Google SRE hires have no previous SRE experience. Backgrounds range from computer science to physics and music theory. The non-technical traits are curiosity, a low tolerance for toil, helpfulness (the incident response team helps whoever escalates, even if the escalation turns out to be unnecessary) and the confidence to challenge the status quo respectfully. New SRE managers and directors spend their first six months as individual contributors, qualifying for on-call.

#### Two hiring profiles

**SRE-SWE** candidates go through the standard software engineering loop with data structures, algorithms and API design. **SRE-SE** candidates have a systems focus and a dedicated non-abstract large system design (NALSD) interview, where they must give realistic numerical estimates and reason about trade-offs down to the hardware. The "Treynor curve" plots the acceptable mix of the two skill sets. Every senior candidate gets a leadership interview. Process lessons: dropout rises sharply once time from application to offer passes about 40 calendar days, so optimise latency for each candidate rather than throughput; avoid brainteasers; and let a committee, not the hiring manager, decide.

#### The new-graduate programme (Ireland)

Students didn't know Google hired engineers in Dublin, didn't know what SRE was, had little practical coding and struggled to think aloud in interviews. Volunteers fixed this with open days, campus talks, CV workshops, algorithm workshops, code retreats, public NALSD material and early internships. Recent graduates proved especially relatable as speakers. Over seven years, hiring grew more than tenfold, with much of the gain within two years. The "circle of life" means former students now run the programme. Each volunteer gave one to eight hours a quarter.

#### Training design

The ROI comparison (Appendix A) puts sink-or-swim against structured onboarding: faster ramp-up and lower first-year attrition pay back the instructor hours. Match investment to the organisation: small and slow-growing, rely on mentoring; small and fast, build an onboarding programme; large and slow, invest in continuing education for retention; large and fast, build the full lifecycle. Informal methods include N+1 mentoring (a mentor from another team), shadowing and **reverse shadowing**, the Wheel of Misfortune, reverse-engineering systems and reading postmortems. Team-specific methods include an **on-call learning checklist**, whiteboard talks where the newcomer draws the architecture (as a forcing function, not a test) and starter projects that are useful, self-contained, achievable, not time-critical and off the critical path.

#### SRE EDU

The week-long orientation focuses on building confidence rather than overwhelming people with information. Its test for adding material: does a two-week-old hire need it, and is it more important than something already in the course? The centrepiece is **breakage scenarios** on real production infrastructure, with a private stack per group of three. The instructor triggers a page, and their role shifts from driving the response, to coaching, to standing aside as a guide. A self-paced Going On-Call series follows one to two months in: On-Call Basics, IMAG and declaring an incident, and escalations. The Annual Week of Education runs near round the clock and gets recorded. Write learning objectives with ADDIE and "a student should be able to…" plus an action verb ("identify memory usage in our monitoring tool", never "understand").

#### Running training like a production service

To teach production safety to tens of thousands of developers (more than ten times orientation's capacity of about 1,000 a year), the team built a self-paced course with automated reminders that escalate up the management chain. They canaried it to 1% of the audience, then rolled it out progressively. Net Promoter Score rose 30 points for what was essentially a compliance module, and over 95% completed it. "On-Call Ready" turned the breakage labs into a self-service reservation system with automated reset and a volunteer teaching assistant in each group of three, reaching five times the old maximum.

#### Careers and retention

Three keys: breadth, initiative and teamwork, each scaling from team scope to organisation scope. (For example, a junior SRE tunes one service's alert thresholds; a senior SRE designs alerting principles and libraries for a whole product area.) Managers aren't expected to be the team's best engineer, which leaves room for IC technical leaders. Teams are typically 7–10 people per site across two sites. Onboarding to on-call can take up to a year, which makes attrition expensive, so managers keep N+1 coverage for on-call and for expertise. They also offer flexible on-call (shorter or split shifts, swaps, exemptions), since on-call is the most common reason people leave, and they encourage moves within SRE: Mission Control, a one-week SRE exchange, and mobility made easier by standardisation.

> Interview angle: "How would you onboard SREs faster?"
>
> Give a checklist-driven, project-based ramp-up with a mentor, simulated breakages before the real pager, shadowing and then reverse shadowing, and confidence surveys at 0, 1 and 6 months to prove it works. Mention canarying the training itself.

### Chapter 6: Organisation design, maturity and scorecards

#### Centralised, decentralised or hybrid

A **centralised** model concentrates expertise and keeps practice consistent. It's the natural start in low-trust, high-control organisations, but it risks a transactional "IT services" mindset and slow onboarding. A **decentralised** model gives deep context, fast feedback and real ownership, but it risks an us-versus-them split and the role being quietly redefined or dropped. Trust has to run both ways. Google is centralised but uses hybrid mechanisms: a community of practice, written engagement models, and a dedicated SRE technical programme manager role. Let practice drift too far and you get "shadow SRE". Reorganisations cost trust and context, and the organisation dips before it improves (a J-curve), so roll changes out gradually with first-mover teams and metrics.

#### Spotify: ownership without a central SRE org

Teams operate what they build ("Ops in Squads", now "Ops in Areas"). A platform group supplies standard stacks, observability defaults (dashboards and alerts come bundled with the service framework) and automation. A small **IMOC** (Incident Manager On-Call) rotation of senior engineers follows the sun. It owns no services, doesn't debug and doesn't take over mitigation. It's engaged only when coordination is the bottleneck: unclear ownership, incidents spanning teams, or cross-cutting decisions such as rerouting traffic or contacting external parties. Two lessons: distributed ownership only scales once operational variance is reduced through standardisation, and IMOC must not become a quiet way to hand off accountability.

#### Team design numbers

A lone SRE is a single point of failure; without the headcount for a team, prefer a DevOps model. Every Google SRE team has a leadership-approved **charter** (Appendix B): mission, scope as a connected whole, services, and success criteria as time-bound outcomes. Limits: at least 50% engineering time, at most 50% operational work, at most 25% on-call. Two sites 6–9 hours apart allow follow-the-sun, with at least six engineers per site (two to three on-call weeks a quarter each). A single site needs at least eight. Split a team once it reaches twice its minimum size. Ideally the current on-caller absorbs all the ops work, about 15% of team capacity. Meet key partners in person at least once a year to pay down "relationship debt".

#### Working with developers

Every Google SRE team has at least one active development partner, often more than ten. Share on-call: developers cover business hours with SRE as escalation, and SRE covers nights with developers as escalation. If SRE alone is primary, developers keep a 24×7 secondary rotation. Keep a shared backlog and give work to whichever team can do it best. Internally, "look left and right" before building something custom. Managers can't block transfers.

#### The weekly production meeting

It's about services, not people's status updates. The agenda: outages and pages (did monitoring work, is the fix durable?), postmortems (written, reviewed, actions done?), SLOs and trends, non-paging alerts and tickets (delete the unactionable ones, promote the critical ones to pages, automate anything found manually) and upcoming changes (raise awareness, don't block). With many partners, hold separate syncs with delegates. Track action items between meetings (Appendix D shows example minutes).

#### Maturity matrix

The dimensions are operational process, risk management, productivity, velocity, system complexity, product lifecycle, teams and leadership. The phases:

- **Absent**: only features count, and users find the bugs. Fine for incubation or a fully automated sunset.
- **Reactive**: fixing the latest outage, heroics, brief freezes.
- **Proactive**: joint risk reviews, dependency management, graceful degradation required (except for policy-enforcing systems that can't fail open). This should be the minimum for anything critical.
- **Strategic**: whole classes of risk removed through architecture, and reliability and velocity both sustained. Expect four or more years to get here.
- **Visionary**: self-healing systems, production knowledge spread everywhere, publishing for the industry. Rare.

It isn't a score, organisations can regress, and the right level depends on context.

#### Scorecards: useful proxies, dangerous targets

KPIs reduce subjective arguments (if the SLOs are green, there's nothing to debate). But they're proxies, and they fail in four ways: leaders weaponise them, teams game them (deploying the same binary every hour to inflate DORA deployment frequency), Goodhart's law kicks in, and you get tunnel vision. Google's **ProdEx**, running since 2015 with more than 1,900 reviews, shows how to do it well. A central scorecard covers on-call load, alert quality, outages, postmortems, SLOs, data integrity, efficiency, bug hygiene and OKR discipline. Reviews happen every few quarters, run by two very senior SREs from *outside* the team's management chain, who coach rather than judge and set scores by hand with context. Alternatives seen at customers include a capabilities model (a baseline set plus per-product maps) for a siloed bank, and tiered "model services" with a shared dev and SRE backlog for a retailer.

> Interview angle: "Leadership wants a reliability scorecard ranking teams. Thoughts?"
>
> Agree to measure, but frame it as coaching: reviewers outside the management chain, context-aware manual scoring, metrics that cover several health domains, and no ranking of winners against losers. Explain Goodhart's law with the hourly-redeploy example.

### Chapter 7: Engagement models: from PRRs to outcomes

#### Organisation structure vs engagement model

Org structure answers who pays and who manages. The engagement model is the **contract of work**: does SRE consult, build, or carry the pager? You can judge an engagement's maturity on three axes: intent (reactive, then specialised, then integrated), impact (depth-first or breadth-first) and value (tactical, then optimised, then strategic, the last asking "how do we make launches succeed?").

#### Scoping archetypes

- **Kitchen sink**: everything SRE. The most common archetype, often an ops team that has just been renamed.
- **Embedded**: depth-first, but risks isolation.
- **Product or application**: business-aligned, but infrastructure gets duplicated without a platform.
- **Infrastructure**: in its modern form, essentially a platform engineering team.
- **Tools**: risks solving the wrong problems.
- **Consulting**: office hours and PRRs, but advisers can lack context.
- **Blended**: a central function, embedded SREs for young products, product SRE for critical ones, infrastructure SRE publishing infrastructure SLOs, shared onboarding and a chief reliability officer.

Monoliths pull you towards product teams; uniform microservices pull you towards infrastructure teams. Re-scope regularly.

#### Consumer vs enterprise

Consumer products have millions of users, so you lean on metrics, SLOs, error budgets and even sentiment from search trends, and incident response is **mitigate first, ask questions later**. Enterprise products have concentrated revenue and contracts, so one big customer's broken workload can matter even within SLO. Implicit guarantees (Hyrum's law) mean you have to watch business logic on critical journeys. Synthetic probers can drown out real signal, so support cases become a detection channel. Response becomes **communicate first, mitigate second**, with dedicated comms responders. Rolling back a change that customers already depend on may be unsafe, which calls for surgical fixes and architectural isolation of large customers. Expose customer-facing failure domains so customers can build their own fallbacks. Freeze changes around customers' big days (Black Friday, New Year's Eve), and organise teams around customer experience (say, all authentication services together) rather than frontend versus backend.

#### Google's three engagement models

**1. PRR gate (the original).** A service was either SRE-supported or "you build it, you run it". The SRE mission: meet availability targets; subject to that, maximise long-term feature velocity; use software instead of toil; and engage only where SRE is more efficient than developers. Funding came through headcount transfers, which pushed developers to build simpler services. A PRR took quarters and typically produced SLOs, lower pager load, documentation, progressive rollouts, backup plans, capacity plans and failure domains. The problems: engagements became sticky, knowledge stayed with SRE, and SRE arrived late in the lifecycle.

**2. Tiers.** Baseline (consulting and office hours, no funding), assisted (projects, embedded SREs, maybe shared on-call) and full. It failed because moving between tiers was as painful as onboarding, nobody wanted to give up a tier they'd "earned", and everything still revolved around who holds the pager.

**3. Outcomes (2025).** Funding is negotiated once per product-area partnership. **Foundational offerings** go to every service: postmortem reviews, office hours, an incident response team. Everything else is an **outcome** delivered through a few time-boxed engineering **efforts**, ranked by business priority and staffed until capacity runs out. Examples: cut operational load by x%, define and defend user-centric SLOs, build a multi-failure-domain architecture, a data integrity and restore plan. On-call exists to gather information for that engineering work. If the same outcome keeps recurring across partnerships, it becomes an infrastructure team or platform feature.

#### Case studies

**Persistent Disk** had SREs semi-embedded in feature teams, overloaded tech leads, unclear ownership (developers assumed SRE owned "all monitoring") and low morale. Leadership agreed foundational offerings (incident response, product SLO alerts, ownership of expanding into new regions) and four outcomes (faster detect-to-mitigate, an exercised disaster recovery plan, lower ops cost, faster releases and rollbacks). They regrouped into four teams, decoupled on-call rotations from team structure and wrote OKRs as progress on outcomes. SRE also built self-service alerting so developers no longer depended on them.

**Microsoft Azure** grew from about 40 SREs in 2015 to about 200. It uses a written playbook with six sequential phases, each with KPIs: service fundamentals; service health and safe deployment practices (critical user journeys, SLOs, phased rollout of code, config and data); operational efficiency (time-to-x metrics measured at P75); release management (three of the four DORA metrics); risk reduction through threat modelling; and scalability. Proven solutions become reusable "SRE patterns". The team scales through platforms, horizontal teams (Service Health, Change) and shift-left standards. Its strongest evidence wasn't dollar ROI but the fact that SRE-supported services improved faster on division quality KPIs.

**Disney** runs a central team embedded long-term: engagements pivot rather than end, with lightweight agreements (what outcome, what risk, what's reliable enough, how it's measured). Proximity builds empathy, empathy builds trust, and trust speeds things up. On-call is treated as a signal of system health, and models vary by domain (theme-park systems hand over to park engineering after launch). Their hard lesson: when new business leadership no longer wanted modern practices, staying on burned people out. Their rule: don't go where you aren't invited, and leave when the invitation lapses.

#### Beyond PRRs

Building the engagement around on-call is an antipattern, and so is SRE "holding the pager" after developers move on; hand services back with a plan. PRRs gatekeep, cost effort that grows linearly with launches, and arrive too late. Replace them with opinionated platforms, standard rollouts, horizontal regression monitoring and automatic rollback, keeping deep reviews for the riskiest launches. Scale influence by guiding (office hours), sharing knowledge (don't be the "human abstraction layer for production") and reducing the need for SRE (standard frameworks, automated policy). Bring product managers in: they should own the definition of SLOs and hear about user impact regularly. An SLO of 99.99% under 10 ms needs a very different design from 99% under 250 ms.

> Interview angle: "SRE is drowning in services it inherited. Fix the engagement model."
>
> Separate foundational offerings from outcome-based efforts, rank outcomes with dev leadership, staff only the top ones, time-box each effort, decouple on-call from team structure, and plan handbacks with training for low-priority services. Point to Persistent Disk as the evidence.

## Part II–III · incidents and learning

### Chapter 10: Incident management in depth

#### Classify before you respond

Bugs, incidents and outages need different behaviour (immediate engagement versus a ticket). Watch the politics in both directions: if leadership counts outages, people under-label; if declaring an outage lets you bypass policy, people over-escalate. Notifying a whole team invites the bystander effect, while relying on one person creates a single point of failure.

#### On-call design

Aim for no more than two incidents per shift, assuming each takes four to six hours end to end. A service that almost never pages may not justify SRE at all. Schedule options include business hours, daytime (6am–8pm), a daylight span across sites of about 21 hours, and 24-hour coverage via follow-the-sun or compensatory time. Required response time drives staffing: about three minutes needs at least two engineers ready to act; thirty minutes or more may not need a laptop at all. Constraints such as data residency, citizenship or security clearance matter, and Google uses a constraint solver for fair rotations. Relax requirements before you burn people out.

#### IMAG and IRTs

The incident commander holds every role until they delegate one, and comms may split into internal and external leads. Incidents can move between states in any order, and big ones become a tree of child incidents under a parent that waits until all the children are resolved. Incident response teams are paged directly by criteria. Large organisations run federated IRTs (Google has Tech IRT plus Cloud, Search and YouTube IRTs, all on the same framework). Small organisations use a **swarm** of senior volunteers per incident. Google found consensus-driven and executive-as-IC models slower and more stressful. Make business context queryable ahead of time: which customers are critical, which racks hold whose workloads.

#### Triage and mitigation

Favour data about user experience over whatever errors are easiest to see. Don't penalise false-positive declarations, but remember investigation isn't free, so curate dashboards. **Risk tolerance scales with impact**: a widely visible outage justifies a riskier mitigation, while a minor one calls for caution, and standing down quickly after triage counts as a win. Mitigate first, and never blame a reasonable mitigation that didn't work; that's outcome bias ("resulting"). Weigh any action against the risk of doing nothing. OODA has a weakness here: it's hard to tell whether your action caused the change or it was coincidence.

#### Coordination costs

Humans are poor at passive monitoring beyond about 30 minutes. Assume a responder who has had no question, input or task for an hour has disengaged. Tens or hundreds of responders means you need better observability or training. MTTR averages mislead, because a rollback takes minutes and a physical repair takes days. Track coordination instead: ramp-up time for new joiners, how often status interrupts work, and the number of channels and tools. In big incidents the IC directs and shouldn't pick up tasks. Assignments should be specific ("check whether the latest rollout's timing and locations match the latency rise").

#### AI in incidents and Etsy's model

Use AI as a rubber duck, and for agents that log their full reasoning with signals and confidence, each with its own identity and authorisation. Treat human approvals as training feedback towards autonomy, not as clutter. **Etsy** reports monthly incident metrics to leadership, runs an incident-announce channel with about 1,000 members, gives every incident its own Slack channel created automatically from alerts, sets safe defaults (severity can change later) and runs a weekly 24×7 **LSE coordinator** rotation of senior leaders. That coordinator separates business decisions from technical restoration. Postmortems are mandatory for SEV1/2 and open with a standard blameless statement that avoids "root cause" and names. The motto: slow is smooth, smooth is fast.

> Interview angle: "Your incident has 60 people on the bridge and no progress."
>
> Split it into child incidents with their own leads, appoint ops and comms leads, give everyone a specific task or release them, have the IC stop doing hands-on work, set a fixed status cadence so people aren't constantly interrupted, and escalate to an IRT or coordinator for cross-team decisions.

### Chapter 11: Learning from incidents: theory and the Paris outage

#### What a postmortem must contain

Key facts (timeline, activities, people), impact (which customers and systems), contributing causes (deviations, actions, data) and lessons learned. Ask non-judgemental questions: not "why did you think it was OK to deploy?" but "what about the situation made deploying look like the best option?". Socialise widely: Google sends curated weekly outage reports and a twice-yearly "Greatest Hits" newsletter.

#### How the practice evolved

Postmortems now look at the sociotechnical system through STPA and CAST, incident storytelling, communication logs and interviews about responders' mental models. An **independent postmortem lead**, someone who wasn't in the incident, interviews participants, guards against outcome bias and hindsight bias, and also records what went right. **Restorative accountability** means the people closest to the decisions help design and own the fixes. Reviews happen in layers: peer, team, organisation and executive. AI helps too: load a notebook with past postmortems and ask whether a proposed design change would have prevented them.

#### Safety-science models to name-drop correctly

- **Swiss cheese (Reason)**: active and latent holes line up, the slices are both technical and human, and near misses are the cases where only one slice held, so ask where you got lucky.
- **Rasmussen**: economic and workload pressures push operations towards the edge of acceptable performance, so you need continuous "fire prevention".
- **Hollnagel's Safety-I vs Safety-II**: Safety-I prevents bad outcomes; Safety-II makes good outcomes more likely by studying normal work and human adaptation.
- **Cook**: complex systems always run degraded (some disks in Colossus are always failing), change constantly, and need several failures lined up to collapse.
- **Woods**: graceful extensibility and sustained adaptability. The danger is **decompensation**: points of presence fail one by one and get absorbed, until one more failure takes the whole network down.
- **Leveson's STAMP**, with CAST for analysis after the fact and STPA for analysis before it.

#### Case study: Paris, April 2023

A cooling-pipe water leak in europe-west9 led to a battery-room fire, and the fire brigade ordered power off for one of the region's three buildings. Regional Spanner lost quorum, and a design flaw turned that into a *global* outage for some API methods that fan out across regions. A known generic mitigation failed. The IC had the team brainstorm, picked the three options that could be built and tested in hours, and ran them in parallel; the first fixed the global impact about four hours later. Customers' complaints were nearly 12 hours of recovery after power returned, and slow, vague updates; one awkward phrase in an update became a media joke.

The analysis found that nobody was making decisions for Compute Engine as a whole, even though it has separate control plane, data plane and hardware on-call rotations. It also found that fact-checking slowed updates yet still let errors through (a wrong region was named as impacted), that no process existed for large-scale customer outreach, and that generic mitigations took hours when they needed minutes. Paging in a product communications lead was what went right. The actions:

- A rotation of **product-level incident commanders**.
- Faster cluster shutdown and restore.
- "Hide the region" made into a safe, repeatable tool.
- Broken generic mitigations fixed and added to disaster recovery exercises.
- The comms lead paged automatically for significant outages, with templates and a formal outreach process.

In March 2025, a power loss in us-east5-c stayed local and took about 6 hours instead of more than 11.

> Interview angle: "What makes a postmortem good?"
>
> An independent author, a full timeline including the comms timeline, multiple contributing factors across people and technology, what went right and where you got lucky, action items mapped to prevent, detect and mitigate with owners, and a follow-up showing the next similar incident went better (Paris versus us-east5-c).

### Chapter 12: STPA and CAST: the Maps case studies

#### Why safety engineering

A 2019 Google Maps postmortem was well written, yet leaders felt it was insufficient, because *no component had failed*. Chain-of-events models are about a century old, and picking a "root cause" is arbitrary, since you can always go further back. A better question is whether the fix would prevent *similar* incidents, not just this one. Safety is an **emergent property**: you can't read it from one component's spec.

#### Doing STPA well

Losses include "loss of mission" (a user can't navigate) as well as revenue and trust. A hazard is a state, for example a published map that doesn't match the real world. Build a **functional** control structure, not a structural one: five teams that can deploy become one "deploys updates" controller. Google's diagrams usually have 5–10 boxes, roughly a tenth the size of a dataflow diagram, and drawing one together gives teams a shared language. Every controller has responsibilities, a control algorithm and a process model (for software) or mental model (for humans), and those models are only as good as the feedback is correct, complete and timely. To find causal scenarios, ask: was feedback missing or wrong, was the model inaccurate, was a safe action overridden or lost in communication, or did the system react unexpectedly?

#### Maps in Japan

A team deliberately dropped connections between nested administrative polygons, expecting the daily repair pipeline to restore them. The update was split into smaller serialised changes, so dashboards declined gradually. Nobody had ever validated the design assumption that inconsistencies would be local in time and space; in reality many features stayed broken for weeks. The approval was rushed under data-freshness pressure, across a Japanese public holiday. The STPA took 2 engineers part-time for 5 weeks and covered more than 30 subsystems and over a dozen teams. It found 56 causal scenarios: almost every defect in the original postmortem plus gaps that could cause at least four other major incidents. It made 34 recommendations against the postmortem's 7.

#### CAST and misnamed cities

Authority increases as you go up the control structure, and confusion about responsibilities points to causes. Blame is the enemy of safety: replace the person and the same system leads the next one to the same choice. The incident unfolds in layers: events, then controller behaviour, then causal factors, then systemic factors. Validation sampled four large states while the bug hit six others. As datasets grew over the years, the system drifted into a riskier state (Rasmussen's drift again), and splitting the data by state let each piece pass a "small change" check. CAST took 5 people and 81 hours and produced 22 recommendations; the postmortem took 3 people and 16 hours and produced 8. Its recommendations reach the top of the control structure: processes, hiring rubrics, ownership after reorganisations, and measuring whether postmortem fixes worked.

#### Getting adoption

A design flaw costs one engineer an afternoon in a design doc, or a whole team a month once it's in production. Senior engineers' design intuition can't be taught directly, but STPA can. Lead with a surprising finding and reveal the method afterwards. Start small: a limited STPA with one or two subject experts in under a week. Pick systems with past surprises, high consequences, people working alongside automation, or that are still in early design. STPA also feeds DiRT: it suggests multi-step, multi-controller scenarios that go beyond what people can imagine on their own.

> Interview angle: "Nothing broke, but users got wrong data. How do you analyse that?"
>
> Use CAST. Map the control structure, find where a controller's process model went wrong and why the feedback didn't correct it, then look for systemic factors such as pressure, incentives and drift. Recommend controls that remove the whole class, such as continuously monitoring design assumptions.

## Part III · building it right

### Chapter 13: Automation and toil, with the real trade-offs

#### Why and how far to automate

There are four reasons to automate: saving time in normal operations, saving time in emergencies (cutting a Cyber Monday outage from 15 minutes to 5 beats shaving an hour off weekly qualification), consistency (especially for emergency actions that need elevated privileges) and scale. The levels run from none, to partial (where teams can get stuck), to full, which can be local, platform-wide or, best of all, **inherent behaviour** (for example, a sync job disappears once there's one source of truth). Capacity provisioning shows the path: a hard-coded prototype becomes platform defaults until GA, then automated planning with two independent layers (minutes-to-hours autoscaling and days-to-months forecasting). Pick the abstraction carefully, letting users choose mean, P90 or peak load rather than tuning forecasts themselves.

#### Pitfalls and the ironies

Bainbridge's ironies of automation: automation creates new and harder work (watching it and repairing it), erodes operators' skills, and so demands more skilled people. The other traps are dangerous automation without rate limits, scope limits, do-no-harm checks and circuit breakers; deskilling (the 99% case); automation surprise; automating over a broken foundation; automating a moving target; and automating ambiguity.

#### Deciding

Run the cost-benefit numbers (and assume you've underestimated the costs), then weigh the things you can't quantify: strategic value (patching a fleet fast), the cost of the safety mechanisms themselves, the ambiguity factor, and the annoyance factor (a five-minute task that wakes someone at night). In Google's network fault mitigation case, speed dominated, but a bad signal could drain healthy infrastructure, so it needed a safety system ("never drain more than X% of a region"). Over time those overlapping checks became hard to reason about and started blocking legitimate repairs. Standardising deployment on Pod changed the economics: once regionalisation came built in, hundreds of low- and medium-risk services adopted it. Restarting a process with a memory leak is fine if the leak is rare and expensive to fix, but it becomes debt if the restarts outpace your release cadence.

#### Incremental automation

"See one, do one, automate one." Use the production meeting to pick candidates, then go from manual, to scripts a human triggers, to fully integrated. An early safety ladder: the automation first only detects and alerts, then suggests an action, then acts and notifies, so the whole team can follow along. Prioritise the fastest wins first to start an **automation snowball**. Don't stop at 90%, because half-automated processes confuse people and add cognitive load; give the automation readable logs and dashboards with linkable events. Make sure defaults never act on everything: outages have happened when a missing variable such as the region was treated as "all".

#### Traffic Director

Google chose multi-single-tenant (one instance per tenant) for velocity and to limit each tenant's blast radius, and Pod's single config made complexity grow sublinearly for a while. Eventually it became the largest config at Google. Per-tenant flags diverged, rollouts got stuck and production ran a two-month-old binary. The postmortem's "Blood and Toil" section described hundreds of manual operations per release. After an 18-month joint stabilisation effort with the platform team, the service moved to multi-tenancy. The lesson: revisiting an architecture that served well for five years is a sign of maturity, not of failure.

#### Toil

Toil is manual, repetitive, scales linearly and leaves nothing lasting behind. Hard engineering work, like a new security policy or tests after an outage, isn't toil. Measure toil, and track the ratio of actionable to noisy alerts. Keep engineering above 50% (for example, reduce toil from 50% to 30%). Catch toil at launch with a checklist, and notice the pages you *should* have received. Reward fixing whole classes of problems, through peer bonuses and promotion criteria. Watch for process toil, like reports nobody acts on, and for **relay** on-call, where the page should go straight to the team that can act. What doesn't work: declaring toil an emergency, making everyone fill in spreadsheets (toil on top of toil), declaring bug bankruptcy, naming a "toil expert", outsourcing toil to a team that isn't on-call, and handing toil to new hires. Toil is acceptable for mitigation (a few days of manual restarts while you investigate a deadlock), for learning (log every command in a recovery drill, then turn them into reusable logical operations) and for human judgement (a human kept the trigger on database recovery, which paid off when a monitoring glitch fired every alert at once). It isn't acceptable to cover product gaps, to absorb work that grows with the system, or to stand in for safe tools when access is restricted.

> Interview angle: "Should we auto-restart the service when memory crosses 90%?"
>
> Yes as a tactical measure if the leak is rare and expensive to fix, with a rate limit, alerting and a ticket for the real fix. No if restarts are becoming more frequent than releases, because then you're hiding debt.

### Chapter 14: Testing, configuration, DiRT and formal methods

#### Philosophy

Testing measures how wrong your mental model of the system is. The pyramid shows which tests depend on which, not their value; the "testing trophy" puts more weight on integration and testing in production. Watch for performance creep: a run of small regressions took one service from 50 to 250 ms in a year. Other techniques: property tests (the output is sorted *and* a permutation of the input), mutation tests, fuzzing (never on production PII), and making illegal states unrepresentable. Hermetic tests have no network calls and use controlled dependencies.

#### Configuration is the sharpest edge

Several big Google outages came from config. VOIS gives you a version to roll back to, a way to see whether a change is live, the ability to soft-launch separately from code, and a safe default for emergencies. Test in three layers:

- **Syntax checks**, kept even in the emergency push tool.
- **Semantic checks**: did something drop to zero, jump 300×, or open new ports? Write these as policy (OPA).
- **Dynamic checks**: dry runs, hermetic launches with probes, going beyond `terraform plan`.

Config drift (production differing from what's committed) breaks the safe-default guarantee. Your options are bundling config with code (not recommended), alerting on drift, or auto-reconciling, as Google and ArgoCD do.

#### Canaries and emergencies

Canary analysis is an A/B comparison between versions, not monitoring. It's also the first time production config and new code meet, so it's really an integration test. Emergency pushes may bypass the gate, but tests keep running and their failures get annotated back onto the push.

#### DiRT

The test week isn't announced in advance. Tests range from tabletop to live ("tear down this datacentre and rebuild it elsewhere with no downtime"), and teams proctor each other across time zones. Google once ran itself for a week from Dublin without Mountain View. Taking the incident management system offline went fine; taking document rendering offline lasted only hours. Fault injection needs a back-out plan anyone can run, peer review including downstream owners, broadcast results even when they're bad, and tests at enough traffic to give a signal. Google tools inject RPC errors and delays (Catzilla) or drop packets per datacentre. Example: a nightly soft-dependency test makes spellcheck fail and checks the product still works.

#### Client-focused change supervision

A low overall error rate during a rollout can hide failing clients. Propagate version metadata through RPC side channels using interceptors or Envoy. Track hops with outbound bookkeeping, TTLs and logical groupings, and build the server-to-client map daily from monitoring. The cost is cardinality: more than 5,000 label values per metric.

#### Formal methods and agents

TLA+ catches non-atomic check-and-set races. Model checking is push-button and produces counterexamples, but the state space explodes. Theorem proving (Isabelle, PVS, TLAPS, Rocq) handles infinite state. A formal spec also solves the **oracle problem** for model-based testing. Google applies formal methods selectively: P4 verification has found more than 300 forwarding bugs since 2020. For agents:

- Treat evals as tests.
- Use several LLM judges and check their agreement (Cohen's kappa).
- Follow OTel GenAI conventions.
- Set budgets with explicit fail-open or fail-closed behaviour, and test failover to a local model.
- Watch for sycophancy drift and tool-name collisions.
- Test how agents handle 429s and malformed tool responses, and replay trajectories.

Failures at one level of agent complexity are hard to see with the tools built for the level below.

> Interview angle: "How do you stop config pushes from causing outages?"
>
> Apply VOIS, layered syntax, semantic and dynamic checks with policy-as-code, progressive rollout with canary comparison, drift detection or auto-reconcile, an emergency path that still validates and back-annotates, and keep the last good config in memory so you can swap back instantly.

### Chapter 15: Capacity: risk, pooling, Meet and the AI era

#### First decide if you need it

Provisioning for every edge case is like aiming for 100% availability. Small workloads should just overprovision, because compute is cheap compared with engineering time. Simple autoscaling rules (add two instances above 70% CPU for five minutes, remove one below 40% with a floor of five) cover most services.

#### Demand

**Organic** demand you forecast from trends (regression, Holt–Winters, ARIMA). **Planned inorganic** demand comes from launches, the Olympics and Black Friday. **Unplanned inorganic** demand (going viral, an unannounced celebrity livestream) you handle with buffers, autoscaling and demand shaping. Also budget for performance regressions and DDoS. Forecast in percentiles (P50, P95, P99) across scenarios, backtest old forecasts, and check postmortems for capacity contributions. Track the **ratio** of infrastructure to business metrics (cores per 1,000 active users) and alert when it shifts, which catches regressions. Shorter provisioning lead times shrink how far ahead you must forecast.

#### Supply and the plan of record

Constraints turn the unconstrained forecast into a plan of record, and layering business metrics on top tells you what a shortfall costs. Supply varies in fungibility, lead time and elasticity. Shared cloud supply carries contention risk, because the same event that spikes your traffic can strain the provider, so pre-buy dedicated capacity for big events. Don't do that permanently, except in regulated, trading or large ML-training settings.

#### Requirements belong to traffic, not services

Provision redundantly for the strict subset of traffic and serve relaxed traffic from spare capacity. Tag requests through OTel context with **criticality** (cheap to discard under overload) and **latency tolerance** (route it to idle datacentres on the other side of the world). Shedding assumes you have enough *global* capacity for critical and batch traffic combined, sized for the single global peak rather than the sum of regional peaks, so batch work rejected in one region retries in another. Physical partitioning (reserved instances for users, spot for batch) is simple but costly; sharing with criticality is efficient but brings noisy neighbours. Clients you don't control can cause a thundering herd as you recover.

#### Failure domains through a capacity lens

Typical cloud SLAs are 99.5% for a zone and 99.99% for multi-region services. Avoid single-zone deployments. Pre-provisioned spare capacity beats autoscaling when the whole internet is scaling at once. Know where your provider's control plane lives, because the failover API may sit in the zone you're fleeing. With two zones, losing one doubles the load on the other. Run evictable work in reserved resilience capacity. Multicloud cuts correlated failure, but only if your cross-cloud orchestration doesn't become the weak link.

#### Crumple zones and efficiency

Define the degradation profile: how much slower, when users notice, and whether failure means throttling or days of manual restore. A cat-photo app and a grid controller are different universes. Shaping demand is cheaper than adding supply; measure shedding so the business can see what it gave up. Utilisation is usage over capacity. Prioritise costly services, don't assume low utilisation means waste (DDoS defences sit idle until needed), question high-frequency low-value work (a query every minute versus once a day) and skip cheap services.

#### Peak of sums and Flex

In the book’s example, provisioning each service separately at its own peak needs 60 units; pooled at the combined peak they need 48. Google's **Flex** pools quota and saves about 5–20%. It gives each account a ceiling and an optional committed floor, oversubscribes, and keeps unused capacity committed for a while to avoid cold starts. When oversubscription fails you get a **stockout**, so services need to survive stockouts. Flex Autoscaling halts at scaling limits to protect the underlying services and alerts SREs; responders can disable it for one service rather than globally. Reclaiming stranded capacity (Maps reroutes background navigation requests across the globe) must still provision for the combined peak, or low-priority work fails at peak.

#### Google Meet during COVID

Meet was stable enough that nobody had invested in deployment automation. Then it grew up to 30× (and up to 400× in some regions by mid-May 2020), with first pages on 17 February in Asia. The team ran it as an incident with workstreams:

- **Capacity estimation**: spreadsheets grew into models, and machines were borrowed from other teams.
- **Dependency mapping**: a 10× target against the pre-COVID peak, tracked in one sheet.
- **Bottlenecks**: fewer log writes, and doubling per-instance size halved the instance count by cutting per-instance overhead.
- **Degradation knobs**: lower video and audio quality, or drop video entirely.
- **Manual production changes**: a month of toil before there was time to automate.

The lessons: adapt incident management for month-long events, use pooling, prepare for unplanned inorganic demand, build control knobs ahead of time, and watch for burnout.

#### The AI era

Supply and demand curves converge, and because you can reshape both the bins and their contents, it stops being simple bin packing. "Minimum viable capacity" brings riskier early capacity online, and tolerant workloads get routed to it. Spatial flexibility moves and resizes workloads automatically to prevent stockouts. AI agents triage capacity crises, reclaim expired ML quota and propose and implement optimisations. Principles: think like FinOps, weighing resource, engineering, inflexibility and unreliability costs; scale planning effort to the service tier; automate by default; keep services mobile; size buffers from SLOs; collaborate with finance.

> Interview angle: "We expect 10× traffic for a one-off event in six weeks."
>
> Map dependencies against a 10× target, find bottlenecks and per-instance overhead, pre-buy capacity rather than relying on autoscaling during the event, build and test degradation knobs and criticality-based shedding, run a load test until goodput plateaus, and staff the event as a planned incident.

### Chapter 16: Data management: law, integrity, backups and recovery

#### Why data failures are different

Lost data stays lost without a working backup, and exfiltrated data can't be pulled back. On 9/11, Aon's planning had it operating again within hours with no data lost. The chapter's authors run Bigtable: 10 exabytes and 7 billion queries per second.

#### Legal and ethical first

Check the law in every place where data originates, is stored and is processed.

- **Minors**: COPPA needs verifiable adult consent under 13, and no behavioural profiles.
- **Retention and deletion**: backups expiring counts as part of deletion, which caps backup retention. Support soft and hard deletes, and TTLs you can clear or disable. GDPR fines reach €20M or 4% of global revenue.
- **Bigtable** offers a **fast** deletion SLO and an **eventual** one that it honours even when underprovisioned, by putting deletion ahead of user traffic.
- **Residency**: Google Cloud's "hurricane policy" means regionally restricted data is never moved, even to save it, because those customers prefer data loss to breaking the law.
- **Purpose limits**: under the DMA, music preferences aren't used for ads without consent, and HIPAA restricts patient data.
- **Ethics**: aim to be "lawful good", not merely lawful.

#### Classification

Original data needs more care than derived data, but derived data that's expensive to rebuild (like the Search index) gets treated as original. Hashing or stripping identifiers doesn't anonymise data; it has to be generalised across many subjects. Avoid collecting high-value personal data (keys, government IDs, sensitive attributes) unless you truly need it.

#### Hierarchy of data needs

Integrity, then security, then availability, then efficiency, captured in the storage team's motto that you, and only you, can always read your data.

- **Integrity** ("what you read is what you wrote") needs redundancy across disks, servers, racks and regions; DB constraints; checksums at the application, every storage layer and the RPC layer; append-only logs and MVCC.
- **The GFS case**: one read in three failed application checksums. Swapping RAM, CPUs and switches didn't help; a faulty Cat5 cable was corrupting data in a way that passed the TCP, RPC and GFS checksums. Bigtable now sees about one minor silent-corruption event a year.
- **Reconciliation versus repair**: reconciliation handles expected inconsistency by design; repair fixes unexpected inconsistency and signals a bug. Log repairs with debugging info and alert on a threshold, which may be one.
- **Security**: exceptional access should be narrow (one account, limited time) and logged to a system the accessor doesn't control. Use least privilege, customer-managed keys and multi-party approval. Never test on production data; Google's "crash" instances are wiped regularly, and sandboxes are named nothing like production.
- **Availability**: how often data is read is a poor proxy for how much its unavailability hurts.
- **Efficiency**: cross-region "RAID" (half the data in A, half in B, parity in C) has 50% overhead instead of 100%, cutting cost by 25%.

#### Failure scenarios and defences

- **Operator error or malice** (agents included): snapshots, backups, and no unilateral human access.
- **Bad application writes**: snapshots, transaction logs for replay, invariant checks and reconciliation. Replication doesn't help.
- **Storage-system bugs**: RocksDB research found roughly one corruption per 3 months per 100 PB, with 40% already copied to replicas. Use backups or dual writes to separate systems.
- **Hardware**: change the encoding (RAID5 to RAID6), replicate, back up. Snapshots won't help.
- **Region loss**: off-region backups and replication.

#### RPO, RTO, RWO

Set the objectives first and let them drive the design, not the other way round. RPO sets backup frequency, which limits how long each backup can take, which can force sharding and application changes. RTO is cumulative: detection, plus action, plus restore. It also tells you how much spare bandwidth a full restore needs. Partial restores can be slow: tape is sequential, a SQL backup restores whole tables, and tar archives must be read in full. RWO example: daily backups kept for two days can't recover corruption from three days ago, and with 14 days you can still lose up to 24 hours if the corruption landed at 23:50.

#### Replication

Replication alone isn't recovery: corruption propagates, and so do deletes. If async replication is five minutes behind, failing over means losing those five minutes. Three replicas in separate regions is the norm. Single-leader setups give ordering; multi-leader setups need conflict resolution, and last-write-wins may be wrong. Async needs an upper bound and per-shard lag telemetry, and best-effort replication leads to divergent replicas. On losing a follower, wait or replace it; on losing a leader, promote one and bound the lost writes. Watch for split-brain.

#### Backups

- **Snapshots** are copy-on-write metadata: cheap and quick, ideal before a risky change, but they share fate with live data.
- **Backups** are separate physical copies. Follow 3-2-1, and anything that can write live data must have no admin rights over backups.
- **PITR** is a backup plus a write log.
- **Full, incremental or differential**: full backups are simple and independent but slow. Incrementals are cheapest, but one bad link breaks the chain. Differentials need only the full plus one diff, though each grows until the next full.
- **Smart vs simple**: a raw file copy is smart but version-locked and fragile; a SQL export is simple and portable but spikes load.

#### Restore testing, plans and recovery policy

If you can't afford a test restore, you can't afford a real one, so make manual restore just the automated test run with different flags. Cover routine restores, user-requested partial restores, bad-data restores and hardware loss. The YouTube backup race: listing videos, copying files, then copying *all* metadata leaves metadata without video. Catch bugs like this with STPA and with application-level validation of restored data. Plan in five stages: discover and classify, define SLOs, design the architecture, design validation, then governance with CTO, CFO and COO sign-off. Build a catalogue with labels and group it into buckets, then give each bucket objectives (24 h RPO with 12 h RTO works manually; 5 min RPO with 3 min RTO must be software-driven). Give data without backups an explicit SLO. Stagger backups so they don't all run at midnight, and make backup setup automatic for new data sources. A restore is the routine path; recovery is extraordinary. Bigtable's policy forbids manual data edits even if data is lost, unless an authorised person signs off, to preserve provenance. Decide in advance: repair or restore, partial restore, salvaging records around a bit flip, who decides what to lose, whether engineers may inspect data, who can override and who approves after hours.

> Interview angle: "Design backups for a new orders database."
>
> Classify the data, get the business to set RPO, RTO and RWO (with RWO capped by deletion law), use PITR for bad writes, locked cross-account backups for operator error, cross-region copies for region loss, automated restore tests that validate application invariants, and a written recovery policy signed off by leadership.

### Chapter 17: Resilience principles: the parts people miss

#### Reliability vs resilience

Reliability means staying within designed norms. Resilience means detecting and handling active failures, novel ones included, with prepared responses. Five nines is a practical ceiling for many systems, but the remaining tail can still burn years of budget, so look for cheap partial mitigations. Likelihood times impact breaks down for rare catastrophes. For likely failures, use cheap default-on mitigations and test with all optional dependencies disabled. For rare ones, first write down how you'd handle it *today*, then fully address a few rather than half-addressing many. Prioritise what has happened to you, then what has happened to others, then realistic risks, then known unknowns.

#### Enforce through technology

A written policy alone overloads people; platform defaults and programmatic checks compound over time. A complex plan might work, but resilience has to work every time. Teams see risk vertically, through their own stack; leadership sees it horizontally, asking every team the same risk questions.

#### Change management details

- Avoid both too many components in one update and several updates to one component.
- Global data needs versioning, and its clients must fail safe on bad data.
- Roll binaries and data separately: one zone, then two, then more. Never change interacting components (a server and its clients or schema) in parallel.
- Google's Canary Analysis Service checks each replica's health; for the most critical systems, include the health of dependents too.
- Rollback isn't guaranteed, so be ready to roll forward.
- Feature flags have fewer dependencies than a binary rollback.
- Give people an inherently safe **emergency stop**, and the psychological safety to press it.
- Alert when more outages than usual are being declared, because the cause may be outside your system.

#### Dependencies

Lock down which dependencies are allowed, at build, config, startup and runtime. Production must never depend on non-production. Optional dependencies fail open; if you can't prove a dependency is optional, treat it as required. When defending dependents, restore critical ones first, start risky changes where dependents matter least, and protect your fallbacks. A fallback can be an earlier version (cheap, but shares fate) or a distinct low-dependency implementation (expensive, but shares little).

#### Failure domains and alignment

A failure domain is only real if everything it needs is local. Alignment matters: two regions with two zones each lose 25% of capacity per zone, while one zone per region without anti-affinity loses 50%. Scale by adding zones rather than growing them, or a zone becomes too large to fail, since draining it would cause a thundering herd. Recovery means isolating, repairing, reassembling and reaching the domain, keeping security patches current while parts are in repair, and keeping global recovery powers in safe places. Protect global state with a **pristine** domain: rollouts delayed by weeks, no emergency pushes, used only to recover others (it's not a warm standby).

#### Overload and input

The goal: a system sized for X that receives 10X should still serve about X and recover on its own. Degrade to roughly 80% quality for 20% of the compute. Load-test until goodput plateaus. Retry at one layer only, using standard client libraries. Reuse per-user quotas for shedding and retry budgets: servers keep a per-request budget, and clients a per-service one. Treat config and code as control inputs. Reject empty updates (an empty ACL locks everyone out), use expected-size fields, keep the previous version in memory to swap back, and alert on bad input.

#### Data resilience and qualification

Risks include losing metadata, losing encryption keys (restores need them) and lower storage layers dropping replicas without understanding the data. Deglobalise storage rollouts, pause mutating operations when redundancy is short, block accidental TTLs on critical data, keep independent metadata backups in a different DBMS, and preserve keys. Qualify through pretend disaster role-play (D&D meets IMAG), then run safer variants for real. Isolating a test environment from DNS and load balancers exposed local cyclic dependencies. One drill revealed too little quota to restore all user data.

#### Incident modes and response journeys

- **Normal**: rich tools for everyone.
- **Emergency**: low-dependency fallbacks with the same interfaces, usable by most responders with minimal training. Invest here first, because it's more likely than disaster.
- **Disaster**: zero-dependency CLIs and direct network access, for small trained teams.

Tools need to keep their security posture in every mode, and errors should point people to the fallback. Response user journeys are comms, IMAG, dashboards, reaching people, docs, privileged access (including multi-party approval), debugging and fixing. Train people to know these exist, then practise them in order: core (reach, comms, privileged access, docs, IMAG), then common (dashboards, debugging, fixing), then bespoke. A common regression is a fallback quietly acquiring a dependency on the system it's meant to replace.

> Interview angle: "Your chat and video tools are down during an outage. Now what?"
>
> Switch to emergency mode: the pre-agreed fallback comms (IRC or a phone bridge), playbooks available offline, a reach list, break-glass access with multi-party approval. Then explain that you'd prove all of this in drills beforehand, ordered by journey priority.

## Part IV–V · platforms, environments and AI

### Chapter 18: Platform engineering: gardens, paths and legibility

#### What a platform is

A platform is the abstraction over your infrastructure plus the culture around it. A good one makes the reliable way the default. A horizontal SRE team (advisory, shared tools, standards) does mostly platform engineering. Google moved from "bring me requirements, not solutions" to **requirements plus curated solutions**: a vetted set of tools, not one monolith, because the old approach led to duplication and made it hard for SREs to move between teams. Curation done well makes the right way the easy way.

#### Policy as a style guide for production

Enforce it with compliance checkers, the way a linter enforces a style guide: in the editor, at commit or at runtime, minding how much noise each adds. Ask what goal a rule serves before adding it. Use warnings unless you're certain no exceptions exist, and even errors need a break-glass path.

#### Models to cite

- **Cynefin**: the domains are clear, complicated, complex, chaotic and, in the middle, confusion. A platform moves accidental complexity towards clear, making the routine 90% easy so experts can focus on the hard 10%.
- **Systems thinking**: system dynamics, Meadows' leverage points, and Ashby's law of requisite variety (a controller needs at least as many states as the system it controls).
- **Direct versus indirect control**: pulling a weed versus improving the soil.
- **Legibility** (James C. Scott): make systems readable by imposing order.
- **Techne versus metis**: shift down the universal knowledge so teams can focus on their system-specific knowledge.

#### Choices, incentives and paths

Use strong defaults (JVM tuning), small menus (regional, continental or global databases) and remove options whose downsides dominate. Stop bikeshedding about the monitoring tool and talk about SLOs instead. Punishment invites gaming; make the good practice the easy one, or as Daria Barteneva puts it, change the game so the good outcome is the rational one. **Desire paths** are informal, shared tacit knowledge; **golden paths** are self-service, opinionated templates built on transparent abstractions. Guardrails range from landscape design and antipaths, to IDE hints, to warnings, to hard errors.

#### Exceptions and feedback

Too many exceptions builds complexity debt; too few builds workaround debt. Make reversible exceptions self-service, and send risky ones to review by whoever would have to staff the risk. Enumerate every exception. Get feedback from three personas: developers (adoption, onboarding time, boilerplate, why desire paths appear), operators (training needed, how many services one team can run, toil, CSAT) and the business (SLOs, incident time, DORA metrics, efficiency).

#### Shift down, effectiveness zones, frameworks

Shift left puts quality work earlier in the lifecycle, but it doesn't scale if every team needs every kind of expertise. Shift down embeds those capabilities in the platform, and the two complement each other. The **ecosystem effectiveness zone** runs from YOLO through ad hoc, guided and engineered to assured. It isn't a maturity ladder: match the constraints to the consequences of failure. Frameworks own the binary's lifecycle, RPC, auth, logging, backoff with jitter and hedging. In a monorepo (one version, live at head), fixing a framework module, such as moving ACL storage, rolls out everywhere at the next build, and introspection tells you when the old version is gone.

#### Legible risk and brownfield exemptions

Write SRE knowledge down as opinionated checks, for example:

- Customer-facing services run in at least two points of presence.
- Alerts route to an active team.
- SLOs exist.
- Incident load stays under a threshold.

Introspect production for these signals, show owners their gaps and give leadership rollups; uncertainty about technical debt is a bigger problem than its cost. Remediate with bugs, proposed changes (AI can draft them) or automatic fixes when you're confident (enabling overload protection everywhere). Block greenfield violations at commit. Exempt brownfield by default with a structured exemption: policy, services, bug, expiry date, reason. Then choose a convergence rate: allow indefinitely, require periodic risk acceptance, require compliance on the next substantive change, or set a deadline. Think of it as eventual consistency for best practices. Building a platform is product management.

> Interview angle: "How do you roll out a new reliability policy to 500 services?"
>
> Encode it as a check, make the platform default compliant, block new violations, auto-exempt existing services with expiry and reason, publish legible rollups, auto-fix where safe, and pick the convergence mode by risk. That's exactly what POC 10 does.

### Chapter 19: SRE at the tipping point

If generating code becomes nearly free, what becomes expensive? The development lifecycle phases stay the same but shrink, and a two-hour build phase leaves no time for the small refinements a two-week one allowed. Fast feedback helps functional requirements, not reliability or security. AI-written code is about as reliable as before (there's evidence it may be less), and models learned from far more code that merely works than code that's reliable in production. Conway's law weakens when one person with one agent can take a spec to production. Non-functional trade-offs, like whether to prioritise paid over free traffic, are social, and AI may recommend, decide or design them away.

The predictions:

- The rate of change will outrun human timescales, cherry-picking fixes stops working, and **roll-forward may become primary**, the reverse of the usual SRE preference.
- Ten times the delivery likely means about ten times the incidents. Automation will take the easy cases, so humans see the hard ones at the rate they used to see easy ones (and how do you learn on those?).
- **Strategic incoherence**: agents handle low-context tasks well, but coherence degrades as features pile up, duplication bloats the context window, and agents become tireless generators of technical debt. Specification-driven development counters this.
- Versioning may need to work per request; "what's actually running?" becomes hard to answer; staging may become impossible.
- Debugging context has to be built on the fly with lossy tools; there may be disposable production environments, replaced when recovery is exhausted; causal chains get longer (more suspects in the murder mystery).
- Cheap response could starve prevention of funding, and skills erode while tools are weakest in the tail where SREs work.

The bright spots are cheaper observability (with more duplicated metrics) and tractable formal methods. Humans remain the understanders of last resort, with comprehension shifting from when code is written to when it fails, and the SRE role starts to look like a staff engineer's.

> Interview angle: "How will AI change SRE?"
>
> More change and more incidents with longer causal chains, so you need stronger rollout automation, evals and change tracking. Roll-forward pressure makes reversibility a design goal. Guard against strategic incoherence with specs and platforms, and keep human skills sharp with drills.

### Chapter 20: How SRE supports AI systems

#### The stack and engagement

Google's first ML SRE team started in 2009 for ad click prediction. The stack runs from accelerators, to cluster management (topology-aware and gang scheduling), to frameworks (JAX or PyTorch compiled through XLA to Pathways), to shared inference, to data lineage (often underbuilt), to agents and applications. Teams supporting researchers mix enterprise-style partnership with consumer-style "mitigate first". Agents are supported by the existing product SRE team, because the expertise is domain-specific. The serving layer routes between model sizes and can **fall back to a smaller model**, trading quality for availability. SRE engages deeply once a model enters a continuous training pipeline. In Ads, failing to produce a fresh model on time counts as an outage.

#### Four SLO pillars

**Availability** covers hardware, the training control plane and attestation. **Throughput** is measured as ML goodput, the share of allocated time doing useful work. **Latency** covers time to first token, scheduling latency and data staleness. **Quality** covers golden datasets, prediction bias and tool-call success rates. For online learning, put SLOs on upstream data producers, and have degraded inputs pause training before the model is corrupted. Evaluate in tiers: lineage checks (halt on freshness or volume drops), cheap statistical drift checks, then sampled model-as-judge scoring. An eval score is an SLI, and its pass threshold is the SLO. For agents, track tool-use success, valid JSON and divergence from the task, since an early hallucination cascades. Security SLOs cover evidence freshness and attestation availability, because for Private AI Compute an attestation failure *is* an outage.

#### Reliability is a spectrum

Responses range from server errors, to the model giving up or answering poorly, to good answers. Instrument intentional degradation (smaller-model fallbacks) and safety-filter hits. Capture explicit feedback (downvotes) and implicit feedback (prompt rewrites, abandonment). Load tests need quality thresholds. Request costs vary wildly, so uniform-cost assumptions and simple thresholds break.

#### Qualification

Hyrum's law hits harder because researchers depend on undocumented behaviour. Qualify accelerators continuously from late engineering validation onwards, testing performance, correctness and relative quality across a workload × architecture × topology matrix prioritised by production usage. Hardware only becomes **SLO-eligible** after a steady stream of qualification data (pre-release and obsolete hardware aren't eligible). Gate new models on structure, op compatibility and resource estimates. Weights, preambles and prompt templates are all change surfaces to canary. Performance gates watch duty cycle and HBM; quality gates use golden sets, human ratings and A/B comparison. Agent workflows need scenario tests for task success, robustness and the absence of destructive actions.

#### The loss framework

Utilisation is measured as duty cycle (for example, P95 occupancy over seven days). Starting from 100%, six losses explain the gap:

1.  **Max utilisation**: real-time serving may queue at around 50%, batch at around 90%. Find the real limit with a redline canary.
2.  **Unrealised demand**: fill launch buffers with preemptible work, pool capacity, grow in steps.
3.  **N+1 redundancy**: use smaller failure domains, and scope redundancy to the critical classes.
4.  **Disaggregation imbalance**: tune the prefill-to-decode server ratio.
5.  **Load balancing**: request costs are uneven and KV-cache locality pulls against even spread. Use least-loaded or peak-EWMA routing, plus cost-aware routing by input tokens.
6.  **Fragmentation**: a large model has a minimum footprint (say 100 chips), so consolidate models, prefer prompting over fine-tuning, and serve multiple tenants.

Also: central fleet pools, hardware fungibility, cost per query reported by the inference engine to drive automated planning, topology-aware, gang and goodput-aware scheduling, defragmentation, bin-packing models, and checkpointing to survive preemption.

#### Power

An ML machine draws roughly 3× a CPU machine, and a 1,000-machine job needs one grid, so its smallest useful footprint is about 3,000× larger. Training load is a square wave of tens of megawatts. Oversubscribe like an airline selling 105 seats for 100. When everyone shows up, shed load before a breaker trips, since breakers tolerate an overload for only seconds. Throttle accelerators first (milliseconds), then after about 5 seconds terminate tasks by priority band (seconds), or shut machines down. Spread sensitive services across power domains.

#### Security

The model and its training data are crown-jewel IP. The system prompt shares a channel with user input, which is the root of prompt injection. Other risks are poisoned weights in the supply chain, MCP and agent-to-agent trust boundaries, and generated code that's effectively remote code execution as a feature, so sandbox it. Centralise controls in the platform (audit logging, trusted execution environments), but don't platformise too early for frontier teams. Log prompts and responses (redacted), tool inputs and outputs, and reasoning traces. Detect quickly with embedding drift checks and regexes, and deeply with a model as judge.

> Interview angle: "Define SLOs for an LLM chat feature."
>
> Availability of the endpoint, time to first token and tokens per second at P95, and a quality SLO from sampled evals plus implicit-feedback proxies, with fallback-to-small-model counted as degraded. Add tool-call success for agents and an attestation SLO if confidential computing is involved.

### Chapter 21: How AI supports SRE

#### Framing

Probabilistic tools at production scale bring probabilistic failure at scale: a 1% error rate spread across all of production is a catastrophe. Organise around three capabilities. **Experimentation** treats results as provisional, because what fails today may work in months. **Productionisation** adds guardrails and evals and keeps validating, because a more capable model may take more action than you expect. **Enablement**: the hardest part is rebuilding senior engineers' intuition. The strategy follows the hierarchy of production health. The book expects more SRE work rather than less (the Jevons paradox).

#### Safety architecture

Production has no safe sandbox: a coding agent's worst case is a failed build, while a production agent's is draining a healthy cluster. The three pillars:

- **Transparency**: the agent shows its reasoning, signals and confidence.
- **Contextual awareness**: freezes, error budgets and active incidents all count.
- **Progressive authorisation**: read-only, then proposing, then autonomous for low-risk actions.

Start with least privilege and dry-run audits. If the error budget is exhausted, downgrade the agent to advisory. Give agents SLOs too: proposal latency, a helpfulness SLO (say 95% of suggestions accepted) and a safety budget that pauses autonomy when spent. Keep a break-glass block on agent access. **Reversible operations**: act only if you know the undo, and validate over a context-aware window that includes warm-up. Treat act, validate and roll back as one transaction. Agents force the strict reversibility the industry usually skips by fixing forward. The foundations are real-time retrieval over topology and incident history, MCP tools, agent-to-agent protocols and agent orchestration.

#### Situational awareness: Detectr

Aggregate SLOs hide pain. At a 0.1% error rate, a customer making 1,000 calls per operation sees nearly every operation fail, and a 0.1% average might really be 1% of customers failing 10% of the time. Classic anomaly detection never caught on because launches and load shedding look like anomalies. Written feedback carries intent ("I tried X in Y and got Z"). **Detectr** pulls in social media, support and forum posts, attaches system state, filters with an LLM, clusters by embedding and then with an LLM, writes a structured report and notifies through normal channels. Cluster volume works as a severity signal, and the effort it takes to write feedback filters out noise. It became core infrastructure in early 2026 and saved thousands of hours of customer impact. AI also maps incidents to impacted customers and matches incoming cases to live incidents.

#### Preparedness and infrastructure

Agents summarise incident channels for joiners and handoffs, and build incident-specific dashboards from similar past incidents, playbooks and intent. Mitigation is about *selecting* from a set (rollback, drain, upscale) with a confidence score; root cause analysis is detective work over topology. Agents draft postmortems, mine the whole corpus, deduplicate bugs and generate a draft playbook when none existed. Rollout speed adapts to risk instead of a fixed wait between failure domains. AI reviews running config for drift. For toil, it clusters tickets (avoiding recency bias), intercepts duplicates, generates playbooks from successful human fixes, retunes itself when a human reopens a ticket, and asks submitters for missing information up front. For resilience tests, it tags each test with a property from a taxonomy, pre-reviews safety, compares the test window against steady state (checking that traffic in the drained datacentre really went to zero) and finds testing gaps by mapping incidents to the properties that would have prevented them.

#### Force multiplier and autonomy

Toil reduction has a ceiling: with toil at 25%, even processing it 5× faster barely moves overall productivity. The real value is new capability: design reviews trained on reliable designs and incident history, launch-review agents that examine the actual prototype, and codebase scans that find every other service sharing a lesson's vulnerability. The autonomy table covers monitor, investigate, approve, actuate and self-direct, from L0 to L4. Not every system should reach L4. **AI Operator** works as the first responder:

- **L1**: summarises and finds similar incidents.
- **L2**: proposes a drain or rollback with the exact commands, for a human to approve.
- **L3**: restarts one aberrant task or clears a known cache on its own, but only after a dedicated eval shows a very high L2 success rate.

It improves itself by comparing its actions with golden human responses and using LLM-judge critiques. Organisationally, Google accepted duplicated solutions and sponsored incubators, with paths to graduate the best ones, a reversal after a decade of standardisation.

> Interview angle: "When would you let an agent act without approval?"
>
> Only for a narrow, well-understood action that's reversible and validated, after a high success rate at L2 in an eval framework. It must also have a healthy safety budget and the error-budget context to act, a kill switch, and an audit trail. POC 11 implements exactly these gates.

### Chapter 22: SRE in diverse environments

#### Solo SRE

You're the firefighter, the builder and the evangelist, often starting at 80% toil. Priorities:

- **P0, stop the bleeding**: fix the repeat outage first.
- **P1, visibility**: business and system metrics, symptom alerts switched on at the start of the day (never at home time), and structured JSON logs.
- **P2, automate the scariest task**, usually deploys. Rollback matters most, because it stops fix-forward chains.
- **P3, developer self-service.**

Use one integrated toolset to answer four questions: is it down, slow, broken, or driving users away? Write playbooks for the last five outages, for non-SREs, and keep them available when everything's down (a repo, a local panic package). Probe critical user journeys, share on-call with developers, and insist on human code review even when AI reviews too.

#### Hybrid and legacy

Google on-callers can see their dependencies' telemetry and roll back or reroute without asking. Elsewhere, a NOC may have only surface access. Fix this by giving an IC explicit authority, with predefined time-bound emergency access the IC can grant, alongside least privilege, two-person rules and immutable audit logs. If you can't walk away from a service, run a toil audit and turn it into a business case ("automating X frees Y hours"). In regulated industries, postmortems can serve as CAPA (corrective and preventive action) evidence for regulators, which raises the priority of fixes. For closed COTS systems, stabilise what surrounds them: IaC, scripts for common mitigations, and an **anticorruption layer**, a wrapper you own that adds observability, rate limits and validated config. For silos, favour generic mitigations, incremental adoption, a limited scope, context-specific goals and drills for systems you can't change, with symptom-based alerts as the unifier.

#### Case studies

**B2B SaaS**: a 20-developer company stuck in "garage mode" set up visibility standards, one-click rollbacks, playbooks for its ten most common failures and basic SLOs, and put all of engineering on call. Six months later, downtime across critical journeys was down about 60% and a major feature shipped 60 days early. It now has about a 7:1 developer-to-SRE ratio, and developers spend about 5% of their time on ops, down from nearly half.

**Bank**: independent silos meant taking a capabilities-based approach. Each vertical's map marked capabilities as existing, must-have, nice-to-have, unneeded or explicitly undesirable, with a ratified baseline. A "chief reliability officer" (a managing director) ran reliability as its own meta-vertical. Third-party "meta tools" plugged into existing monitoring, then disaster role-plays and a standing postmortem review committee followed. Results: consistent SLO reporting, lower MTTR, and fewer layers than the old five-plus-level escalation stack.

**Mortgage lender**: a three-month SRE workshop seeded the practice. A central team offered issue-flow advice, 90-day engagements, one to three designated SREs at 50–75% for critical services, and a training rotation, then ran an eight-week enablement programme. It cut **weaponised blamelessness**, where "no blame" was used to dodge ownership.

#### Waymo: crises, not just outages

Waymo's IRT covers on-road incidents, physical security and local events, drawing on legal, safety, ops, comms and policy on-callers, while SRE coordinates without mitigating. It runs two simultaneous primary roles: the **incident coordinator** (a conductor who manages breakouts and dissent and keeps safety first) and the **incident scribe** (record-keeper and presenter who flags contradictions between what the room and the field are saying). SRE fits because it's continuously trained in incident management and owns the tooling. It works at a "Goldilocks" size, past the point where all senior people can jump on a call but before you have dedicated corporate responders, and in companies with diverse job functions.

#### Security and privacy

These share SRE's constructive pessimism; only the adversary differs. In the **CrowdStrike** incident (19 July 2024), Windows VMs crash-looped. The VM-infrastructure SRE team and the guest OS team each had the wrong scope, so support went straight to the vendor. The lesson was about knowing roles across boundaries. For **Log4j** (CVSS 10), security and Tech IRT launched per-department response groups under a Code Red with exit criteria: upgrade everything, file exceptions, document status. That happened during a holiday code freeze. What went well: defining the end-to-end process up front and tracking centrally. What to improve: instructions for verifying an upgrade.

> Interview angle: "You're the first SRE at a startup. First 90 days?"
>
> Walk the P0–P3 stack, answer the four questions with one toolset, write playbooks for the last five outages, ship one-click rollback, set two or three SLOs with the founders, start a shared on-call and code review, and show the wins with numbers.

### Chapter 23: Future of SRE, plus appendices A–D and G

Two things won't change: reliability matters more as technology becomes societal infrastructure, and humans stay involved for novel problems. Three things are transforming. First, shift left is becoming **shift down**, with managed services and opinionated frameworks. Second, **risk is becoming a leading indicator**, because availability only tells you after the fact. Every postmortem should catalogue the risks it uncovered, alongside proactive STPA and AI reviews of designs and code, all classified with a taxonomy based on the SEI's risk taxonomy. Mapping incidents against it showed that many came from mishandled overload, which led to overload protection being built into the core RPC stack. Third, AI changes the practice itself: release pipelines for many more, smaller changes, more systems and tools to standardise, and SREs moving from specialists to generalists who direct agents. The closing idea is that SREs will automate themselves into new jobs rather than out of them.

#### Appendices

- **A, training ROI**: sink-or-swim takes 550 weeks plus \$220k; structured training takes 483 weeks plus \$210k. That saves 67 weeks and \$10k.
- **B, charter template**: status, mission, scope, services, success measures, values.
- **C, example charter (gShoe)**: success looks like 100% SLO coverage, toil 50% below the 2022 level, launch prep cut from three months to one, at least 60% utilisation while absorbing a 5× spike for an hour.
- **D, production meeting minutes**: announcements, action-item review, outages, paging and non-paging events, a toil check, monitoring changes, planned changes, key metrics, resources and new action items.
- **G, statistics and ML**: a Wilson baseline from the last two weeks suits most metrics, and a forecasting model (TimesFM) helps for strongly cyclical ones. Weigh explainability and cost; ML is most cost-effective after an alert, for analysis, rather than for detection.
