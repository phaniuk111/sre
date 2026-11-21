"""Pass 2 of the reading workflow: synthesis across all four books.

One source of truth for four things, rendered twice: as Markdown in docs/ and as
lessons in the course page.

  EXEC     executive summary
  MAP      knowledge map: themes -> concepts -> chapters -> POC
  REQS     requirements: what the books say you should have in place
  NUMBERS  figures worth knowing cold

References: S8 = SRE book chapter 8; P15 = platform book chapter 15 (final numbering).
Everything is in my own words.
"""
import html as H
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(HERE, '..', 'docs')

# ───────────────────────────────────────────────────────────── executive summary
EXEC = [
    ('The two books in one paragraph each', [
        ('p', '<b>Site Reliability Engineering, 2nd Edition</b> describes how to run software so that it is as reliable as its users need and no more. It treats operations as an engineering problem, makes reliability measurable through service level objectives and error budgets, and organises everything else as a pyramid, the hierarchy of production health: culture at the base, then awareness, preparedness, infrastructure design, resilient products and, at the top, platforms that make services reliable by default.'),
        ('p', '<b>Platform Engineering at Google</b> starts where that pyramid ends. Its claim is that security, reliability and efficiency can’t be delivered by asking every developer to be careful. They have to be moved down into the languages, libraries, pipelines and infrastructure that all code is built on, so that experts solve each problem once and every team inherits the result. Only ten of its thirty-one planned chapters are published.'),
    ]),
    ('What the SRE book argues', [
        ('ul', ['<b>100% is the wrong target.</b> Pick a target from what users need, and treat the gap as a budget to spend on change. (S2, S8)',
                '<b>Culture comes first.</b> Blameless learning, psychological safety and sustainable on-call are the base of the pyramid, not a soft extra. (S1, S4)',
                '<b>Measure from the user’s side.</b> SLOs belong to user journeys, alerts fire on how fast the budget burns, and low-traffic services need statistics, not thresholds. (S8, S9)',
                '<b>Mitigate before you understand.</b> Clear roles, generic mitigations and practised emergency modes shorten incidents more than better diagnosis does. (S10, S17)',
                '<b>Accidents are control problems.</b> STPA and CAST replace the hunt for a root cause with the question of why the system allowed the unsafe action. (S11, S12)',
                '<b>Changes cause most outages.</b> So test configuration like code, roll out progressively, compare a canary with a control, and roll back automatically. (S14, S17)',
                '<b>Shift down.</b> The durable fix for a class of failure is a platform that makes it impossible or handles it by default. (S18, S23)',
                '<b>AI cuts both ways.</b> AI systems need quality as a reliability signal, and AI operators need autonomy that is earned, bounded and reversible. (S19–S21)']),
    ]),
    ('What the platform book argues', [
        ('ul', ['<b>Shift down, not only left.</b> Shifting left finds a problem earlier and leaves it with the developer. Shifting down makes the platform responsible. (P15, P16)',
                '<b>Conformity buys leverage.</b> The more an ecosystem limits choice, the more liability it can carry for its users. Make that trade explicit with resources, rights and responsibilities. (P12)',
                '<b>Coupling is a decision.</b> It buys efficiency, performance, atomicity and traceability and costs reuse, extensibility, robustness and choice. The danger is coupling nobody chose. (P9)',
                '<b>Layers move at different speeds.</b> Experiments and products are fast; infrastructure, directives, culture and law are slow. Fast layers propose and slow layers decide. (P10)',
                '<b>If it isn’t secure, it shouldn’t compile.</b> Wrap each risky operation in a safe abstraction so the vulnerable program can’t be written, then carry the same idea into builds and deployment. (P15)',
                '<b>SRE is the blueprint; the platform is the machinery.</b> Put into the platform whatever has a wide blast radius, needs rare expertise or fails catastrophically. (P16)',
                '<b>One optimisation, every team.</b> Shared foundations let you see the whole fleet and fix the biggest consumer once, on by default. (P14)',
                '<b>A platform nobody uses is worth nothing.</b> Design the experience, run the platform as a product, and measure adopters against non-adopters. (P18, P19)',
                '<b>AI amplifies what is already there.</b> Good platforms and current documentation make assistants useful; poor ones make the mess arrive faster. (P22, P24)']),
    ]),
    ('Where the two books meet', [
        ('table', ['Idea', 'In the SRE book', 'In the platform book'], [
            ['Reliable by default', 'Emergent reliability, the top of the pyramid (S1, S18)', 'The whole thesis: quality attributes as properties of the platform (P12, P15, P16)'],
            ['Budget for risk', 'Error budgets and a policy with three zones (S8)', 'Risk profiles: the budget sets the deployment policy automatically (P16)'],
            ['Design for human error', 'Blameless postmortems, STPA and CAST (S11, S12)', 'Safe abstractions and guardrails that make the mistake impossible (P15)'],
            ['Make the right way the easy way', 'Golden paths over mandates; the effectiveness zone (S18)', 'Path of least resistance; “friction is a directive” (P12, P18)'],
            ['Hyrum’s law', 'Users depend on the reliability you actually deliver (S8)', 'Hidden dependencies block change; randomise what you don’t promise (P9, P14)'],
            ['Safe change', 'Canaries, progressive rollout, config testing (S14, S17)', 'Canary analysis as a platform gate; signed artifacts; blueprints (P15, P16)'],
            ['Break the rules safely', 'Emergency modes with independent fallbacks (S17)', 'Break-glass: permitted, logged, alerted, reviewed (P16)'],
            ['Sublinear scaling', 'Cost grows more slowly than the service (S2)', 'Cost of each capability paid once and amortised (P14, P16)'],
            ['AI', 'Earned, reversible autonomy for agents (S21)', 'Guardrails as a containment field for generated code (P12, P15)'],
        ]),
        ('p', 'The difference is the point of view. The SRE book is written from the seat of the people operating services. The platform book is written from the seat of the people building what those services stand on. In an interview, the strongest answers use both: name the principle, then say which platform mechanism makes it the default.'),
    ]),
    ('How to turn this into interview answers', [
        ('ol', ['<b>Principle.</b> One sentence, in your own words.', '<b>Mechanism.</b> The concrete thing that enforces or measures it.', '<b>AWS.</b> Which services you would use.', '<b>Evidence.</b> One number or one story from the books or from your own work.']),
        ('p', 'Example: “We shouldn’t rely on reviewers to catch SQL injection. I’d wrap the database driver in a typed query API and fail the build on raw queries. On AWS that is a wrapper over the RDS Data API and a CodeBuild check. Google reports no SQL injection in protected applications for over ten years with this approach.”'),
    ]),
    ('What this summary does not cover', [
        ('ul', ['Twenty-one chapters of the platform book are not published yet, including the ones that define ecosystem types, shifting down and golden paths.',
                'SRE appendices E and F were read once, not twice. Citation-only footnotes in the platform book were skipped.',
                'These are study notes in my own words. They don’t replace either book.']),
    ]),
]

# ───────────────────────────────────────────────────────────── knowledge map
# theme -> (lead-in, [(concept, definition, refs, poc)])
MAP = [
    ('Targets and budgets', 'How reliable is reliable enough, and how the answer drives decisions.', [
        ('SLI, SLO, SLA', 'Indicator (good events over valid events), objective (the target), agreement (what happens if it is missed)', 'S8', '01'),
        ('Error budget', 'One minus the SLO: the failure you are allowed, to be spent on change', 'S2, S8', '01'),
        ('Burn rate', 'How fast the budget is being spent. Page on a fast burn confirmed by a short window', 'S8', '01'),
        ('Error budget policy', 'What changes as the budget shrinks: business as usual, growing trade-offs, freeze', 'S8', '01'),
        ('Critical user journey', 'A user goal and its tasks; SLOs are defined from it downward', 'S8, S9', '02'),
        ('Low-traffic alerting', 'Page only when a confidence interval’s lower bound exceeds the threshold', 'S8, S9', '01'),
        ('Risk profile', 'A service’s tier and remaining budget set its rollout policy automatically', 'S8, P16', '16'),
        ('The nines', 'Each extra nine cuts allowed downtime tenfold and costs far more than the last', 'S2, S8, P16', '16'),
    ]),
    ('Seeing the system', 'What you have to be able to observe, and who provides it.', [
        ('Observability', 'Someone without tribal knowledge can test and reject hypotheses quickly', 'S9', '02'),
        ('Four golden signals', 'Latency, traffic, errors, saturation, with the same names everywhere', 'S9, P16', '02'),
        ('Client-side telemetry', 'What servers can’t see: DNS, certificates, crashes, retries hiding errors', 'S9', '02'),
        ('Customer-centric invariant', 'A check from the user’s side, such as “sees non-zero valid results”', 'S9', '02'),
        ('Application productivity metric', 'Useful work divided by resources used; separates busier from slower', 'P14', '17'),
        ('Security signals', 'Frameworks report per request which protections ran; absence raises an alert', 'P15', ''),
        ('Model signals', 'Freshness, drift, confidence; for agents, tokens, latency, tool calls', 'S20, P16, P22', '19'),
        ('Joint cognitive system', 'People and tools share a working memory in an incident; consistency gives fluency', 'P16', ''),
    ]),
    ('Changing production safely', 'Changes are the main cause of outages in both books.', [
        ('Progressive rollout', 'Small exposure first, growing in stages with bake time', 'S14, S17, P16', '05, 16'),
        ('Canary analysis', 'Compare the new version with a control serving the same traffic at the same time', 'S14, P16', '05'),
        ('Automatic rollback', 'A regression halts and reverts the rollout without a human', 'S17, P16', '05'),
        ('Configuration as code', 'Versioned, reviewed, tested and rolled out like a binary', 'S14, P15', '10, 15'),
        ('Blueprint', 'A pre-validated template with locked invariants and a few parameters', 'P15', '15'),
        ('Conformance verification', 'Continuously compare what is deployed with the approved baseline', 'P15', '15, 10'),
        ('Attestation and deploy gate', 'Signed statements about an artifact, verified before it may run', 'P15', '14'),
        ('Bad-change marker', 'Flag one change and the deploy system refuses every build containing it', 'P9, P16', '14'),
    ]),
    ('Failure, response and learning', 'What to do when it breaks, and how to stop it breaking the same way.', [
        ('Incident roles', 'Commander directs, operations acts, communications informs', 'S10', '03'),
        ('Generic mitigations', 'Roll back, drain, add capacity, degrade, block: safe before diagnosis', 'S10, S13', '03, 09'),
        ('Emergency modes', 'Normal, emergency, disaster; each needs tooling with fewer dependencies', 'S17', '04'),
        ('Break-glass', 'A bypass that is permitted, logged, alerted on and reviewed', 'P16', '14, 16'),
        ('Blameless postmortem', 'Why the action made sense at the time; several contributing factors', 'S4, S11', '03'),
        ('STPA', 'Forward-looking: hazards, control structure, unsafe control actions, scenarios', 'S12', '03'),
        ('CAST', 'Backward-looking: the same model applied to an incident, down to systemic factors', 'S12', '03'),
        ('Rasmussen’s boundaries', 'Cost and workload pressure push a system towards the accident boundary', 'S11', ''),
        ('Institutional memory', 'If teams repeat an outage, change the platform default, not the training', 'P16', ''),
    ]),
    ('Resilience by design', 'Properties built in before the incident.', [
        ('Failure domains and N+1', 'Survive the loss of a zone or region; say which domain you mean', 'S15, S17, P16', '04, 07'),
        ('Graceful degradation', 'Serve something useful when a dependency is gone', 'S1, S17', '04'),
        ('Load shedding by criticality', 'Drop the least important work first; tag requests', 'S15, S17, P14', '04'),
        ('Retry budgets and adaptive throttling', 'Bound retries in the client library so one service can’t start a cascade', 'S17, P16', '04'),
        ('Deadline propagation', 'Stop work whose caller has already given up', 'P14', '17'),
        ('Fail open or fail closed', 'Degrade for optional features; refuse for security or correctness checks', 'P9, P22', '12, 19'),
        ('Operation invariants', 'The platform rejects unsafe actions, such as draining several regions', 'P16', '16'),
    ]),
    ('Capacity and efficiency', 'Having enough, and not paying for more.', [
        ('Forecast with uncertainty', 'Plan to a chosen risk, not to every edge case', 'S15', '07'),
        ('Pooling', 'Peaks rarely coincide, so a shared pool needs less than the sum of its parts', 'S15, P14', '07'),
        ('Stockout', 'Pooled services must survive not getting capacity', 'S15', '07'),
        ('Autoscaling', 'Predictive for the long term, reactive within minutes, horizontal and vertical', 'P16', '07'),
        ('Fleet-wide profiling', 'One profiler everywhere shows which shared component costs the most', 'P14', '17'),
        ('On by default', 'Ship optimisations to everyone; absorb small regressions; opt-outs are information', 'P14', '17'),
        ('Idle accelerators', 'Power stays high at low utilisation, so run fewer machines hotter', 'S20', ''),
    ]),
    ('Data', 'Losing data is worse than being down.', [
        ('RPO, RTO, RWO', 'How much you may lose, how long until you are back (detect, act, restore), how far back you can go', 'S16', '08'),
        ('3-2-1', 'Three copies, two media, one elsewhere; replication is not a backup', 'S16', '08'),
        ('Restore testing', 'A backup you have not restored is a hope', 'S16', '08'),
        ('Integrity first', 'Recover as much as possible, never at the cost of integrity', 'S16', ''),
        ('Shared database', 'Several services on one schema; the classic coupling antipattern', 'P9', '12'),
    ]),
    ('Platforms and shifting down', 'Where both books converge.', [
        ('Shift down', 'Move responsibility into the platform so teams inherit the result', 'S18, S23, P15, P16', '10, 13–16'),
        ('Ecosystem types 0 to 4', 'YOLO, ad hoc, guided, engineered, assured', 'S18, P12', '10'),
        ('Golden path', 'The supported, documented, easiest way to do a common task', 'S18, P18, P19', '18'),
        ('Resource or guardrail', 'A resource helps; a guardrail makes the safe choice the only one', 'P12', '14'),
        ('Effectiveness zone', 'Match the strength of a control to the severity of the outcome', 'S18', '10'),
        ('Shared fate and the three Rs', 'Resources, rights, responsibilities: the contract between platform and teams', 'P12', 'docs'),
        ('Large-scale change', 'One team changes thousands of projects at once; needs a uniform toolchain', 'P12, P14', ''),
        ('Pace layers', 'Six layers from experiments to law, each changing at its own speed', 'P10', ''),
        ('Platform SLOs', 'The platform is everyone’s single point of failure and needs stricter objectives', 'P16', '16'),
    ]),
    ('Coupling and architecture', 'What depends on what, and whether anyone decided it.', [
        ('Explicit and implicit', 'A direct call, or an unstated assumption such as a message format', 'P9', '12'),
        ('Retargetability', 'Being able to reuse a part elsewhere; what coupling trades away', 'P9', ''),
        ('Loose patterns', 'Layers, pipe and filter, publish-subscribe, federation, fail open', 'P9', '12'),
        ('Antipatterns', 'Shared database, distributed monolith, megamorphic artifact, control coupling', 'P9', '12'),
        ('Hyrum’s law', 'With enough users, every observable behaviour is depended on by someone', 'S8, P9, P14', ''),
        ('Discovering coupling', 'Static analysis, tracing, log correlation, chaos engineering', 'P9', '12, 06'),
    ]),
    ('Security by construction', 'Prevent classes of bug instead of hunting instances.', [
        ('Assurance', 'Confidence that a property holds for every behaviour; testing can’t give it', 'P15', '13'),
        ('Archetype and invariant', 'A recurring application shape, and the properties a platform can own for it', 'P15', ''),
        ('Risky operation', 'Safe only if a condition holds that nothing guarantees', 'P15', '13'),
        ('Safe abstraction', 'No safety condition on callers; the module owns the risk; reviewable alone', 'P15', '13'),
        ('SLSA build levels', 'L1 provenance exists, L2 signed by a hosted builder, L3 hardened builds', 'P15', '14'),
        ('Identity and authorisation', 'Workload identity, mutual TLS, a central relationship-based authorisation service', 'P15', ''),
        ('Insider risk', 'Multi-party approval, no direct production access, audited proxies', 'P15', ''),
        ('Prompt injection', 'No separate channel for data in a model, so it can’t be prevented by construction yet', 'P15, P22', ''),
    ]),
    ('People, teams and product', 'The sociotechnical half.', [
        ('Psychological safety', 'Safe to be wrong, to not know, to make an honest novel mistake', 'S4, P24', ''),
        ('Toil', 'Manual, repetitive, automatable, no lasting value; keep engineering above half', 'S1, S13, P16', '09'),
        ('Sustainable on-call', 'Limits on on-call share, rotation size and incidents per shift', 'S6, S10', ''),
        ('Engagement model', 'The contract of work between SRE and a product team', 'S7', ''),
        ('Developer experience', 'Feedback loops, cognitive load, flow', 'P18', '18'),
        ('Platform as a product', 'Customers, a value proposition, a lifecycle; jobs to be done', 'P19', '18'),
        ('Deprecation', 'A launch in reverse, with brownouts and a real off switch', 'P19', '18'),
        ('Education', 'Belongs to the platform team; next task to the most junior who can do it with guidance', 'S5, P24', ''),
    ]),
    ('AI', 'Running AI, and running with AI.', [
        ('Quality as a reliability signal', 'A fast success with a wrong answer is a failure', 'S20, P22', '19'),
        ('Qualification', 'Hardware, models and prompts are tested and canaried before serving', 'S20', '19'),
        ('Feature store and model registry', 'One source of feature values; one source of truth for versions', 'P22', '19'),
        ('Autonomy levels', 'From manual to full; earned per class of action, never assumed', 'S21', '11'),
        ('Reversible atomic actions', 'An agent may only do what it knows how to undo', 'S21', '11'),
        ('Guardrails as containment', 'Generated code must compile against safe APIs and pass the deploy gate', 'P12, P15', '13, 14'),
        ('Agentic platform', 'Agent-friendly interfaces, with the platform as the controls that always hold', 'P19, P22', ''),
        ('Amplifier', 'AI magnifies an organisation’s existing strengths and dysfunctions', 'P24', ''),
    ]),
]

# ───────────────────────────────────────────────────────────── requirements
REQS = [
    ('Targets', [
        ('Every critical user journey has an SLI and an SLO chosen from user need', 'S8, S9', '01'),
        ('A written error budget policy with three zones, agreed by product and engineering', 'S8', '01'),
        ('Paging alerts fire on burn rate, confirmed by a short window', 'S8', '01'),
        ('Low-traffic services alert on a confidence interval, not a raw ratio', 'S8, S9', '01'),
        ('Each service has a tier that the delivery pipeline reads', 'P16', '16'),
    ]),
    ('Observability', [
        ('New services get the four golden signals, logs and traces without doing anything', 'S9, P16', '02'),
        ('Metric names and dashboards are the same across services', 'P16', '02'),
        ('User journeys are measured from the client side as well as the server', 'S9', '02'),
        ('Monitoring does not depend on the systems it monitors', 'S9', ''),
        ('Each service reports useful work so productivity per unit of resource is known', 'P14', '17'),
    ]),
    ('Incidents and learning', [
        ('Anyone can declare an incident; roles are defined and practised', 'S10', '03'),
        ('Generic mitigations exist and can be run without diagnosis', 'S10, S13', '03, 09'),
        ('Emergency access, communication and documentation work when normal tools are down', 'S17', '04'),
        ('Postmortems are blameless, list several contributing factors and track actions to completion', 'S11', '03'),
        ('Repeated incidents lead to a changed platform default', 'P16', ''),
    ]),
    ('Change', [
        ('Every production change, including configuration, goes through one pipeline', 'S14, P15, P16', '05, 15'),
        ('Rollouts are staged, with bake time set by the service’s risk profile', 'S17, P16', '16'),
        ('A canary is compared with a control automatically, and regressions roll back', 'S14, P16', '05'),
        ('Artifacts are built by a hosted builder, signed, and verified before deploy', 'P15', '14'),
        ('A change can be marked bad and is then blocked everywhere', 'P16', '14'),
        ('Break-glass exists, needs an incident reference, and alerts security', 'P16', '14, 16'),
    ]),
    ('Resilience and capacity', [
        ('Critical services run across failure domains by default, sized to lose one', 'S17, P16', '04, 07'),
        ('The client library enforces backoff and a retry budget', 'S17, P16', '04'),
        ('Requests carry criticality and deadlines; overload sheds the least important first', 'S15, P14', '04'),
        ('The platform rejects operations that break an invariant', 'P16', '16'),
        ('Capacity is forecast with stated uncertainty and scaled automatically', 'S15, P16', '07'),
        ('Fault injection is run regularly, with SLO-based stop conditions', 'S14, P9', '06'),
    ]),
    ('Data', [
        ('Each data set has an RPO, RTO and retention window set by the business', 'S16', '08'),
        ('Backups are separate copies; writers to live data can’t delete them', 'S16', '08'),
        ('Restores are tested automatically and the restored data is validated', 'S16', '08'),
        ('Each service owns its data store behind an API', 'P9', '12'),
    ]),
    ('Security', [
        ('New code is written in a memory-safe language', 'P15', ''),
        ('Injection-prone operations are reachable only through typed safe APIs, checked in CI', 'P15', '13'),
        ('Dependencies come from a curated repository with automated updates', 'P12, P15', '14'),
        ('Workloads have their own identities; service calls are authenticated and authorised by the framework', 'P15', ''),
        ('Web security headers and TLS are set once, centrally', 'P15', ''),
        ('Infrastructure comes from reviewed blueprints, and drift is detected', 'P15', '15'),
        ('Adoption of each guarantee is measured across the fleet', 'P15', '13, 15'),
    ]),
    ('The platform as a product', [
        ('Customer segments are named, and their jobs to be done are written down', 'P19', '18'),
        ('Time to a first production deploy is measured and short', 'P18, P19', '18'),
        ('Console, command line, infrastructure as code and agents share one API', 'P18', ''),
        ('The golden path has documented escape hatches; exemptions have an owner and an expiry', 'S18, P18', '10'),
        ('The contract between platform and teams is published as resources, rights and responsibilities', 'P12', 'docs'),
        ('A scorecard reports user, system and business views', 'P19', '18'),
        ('The platform has its own SLOs, stricter than its tenants’', 'P16', '16'),
        ('Old platforms are retired with a plan, brownouts and an off date', 'P19', '18'),
    ]),
    ('People', [
        ('Engineering work is at least half of an SRE team’s time', 'S1, S6, S13', '09'),
        ('On-call load is capped and rotations are large enough to be sustainable', 'S6, S10', ''),
        ('Onboarding and training build confidence through practice', 'S5', ''),
        ('Platform teams have people with time allocated to support, writing and teaching', 'P24', ''),
        ('Internal documentation has owners and review dates', 'S4, P24', ''),
    ]),
    ('AI', [
        ('Model endpoints have a quality objective alongside latency and availability', 'S20, P22', '19'),
        ('Freshness, input drift and confidence are monitored and can page', 'P22', '19'),
        ('Models are signed, registered with lineage, evaluated and canaried before serving', 'S20, P22', '19'),
        ('Input and output guardrails run outside the model', 'P22', ''),
        ('Agents have least privilege, act only reversibly, and earn autonomy per class of action', 'S21, P22', '11'),
        ('Generated code passes the same safe APIs and deploy gate as human code', 'P12, P15', '13, 14'),
    ]),
]

# ───────────────────────────────────────────────────────────── numbers
NUMBERS = [
    ('99.9% over 30 days', '43.2 minutes of error budget', 'S8'),
    ('14.4× burn rate', '2% of a 30-day budget in one hour: page, confirmed by a 5-minute window', 'S8'),
    ('6× burn rate', '5% of the budget in six hours: page, confirmed by a 30-minute window', 'S8'),
    ('1× burn rate', '10% of the budget in three days: ticket', 'S8'),
    ('99% / 99.9% / 99.99% / 99.999% a year', '87.6 hours / 8.77 hours / 52.6 minutes / 5.26 minutes of downtime', 'P16'),
    ('At least 50%', 'of an SRE team’s time on engineering; the toil ceiling is a limit, not a target', 'S1, S6, S13'),
    ('At most 25%', 'of time on-call', 'S6'),
    ('6 per site across two sites, or 8 at one', 'minimum engineers for a sustainable rotation', 'S6'),
    ('About 2', 'incidents per on-call shift at most', 'S10'),
    ('100 to 1,000 engineer-hours', 'the cost of one hour of major downtime', 'S2'),
    ('53%', 'of visitors abandon a task when a page takes more than three seconds', 'S2'),
    ('1.4× and 1.8×', 'more likely to report better delivery and better business outcomes with strong operations practice', 'S4'),
    ('3.5×', 'more likely to adopt SRE practices with good documentation', 'S4'),
    ('About 40 days', 'from application to offer, after which candidates drop out sharply', 'S5'),
    ('Nearly a fifth', 'of SRE alerts at Google are universal alerts every service inherits', 'S9'),
    ('34 against 7', 'recommendations from STPA against the original postmortem in the Maps example', 'S12'),
    ('22 against 8', 'recommendations from CAST against the postmortem for the misnamed cities', 'S12'),
    ('0.1%, then about ten-fold a day', 'a rule of thumb for progressive rollout', 'S14'),
    ('100 to 1 and 2 to 1', 'cost of fixing severe and minor defects in production against earlier', 'S14'),
    ('99% of data sources within RPO, 99% of the time', 'an example fleet-level backup objective', 'S16'),
    ('About 6 months', 'the build horizon: older binaries may not run', 'S18'),
    ('L0 to L4', 'autonomy levels for AI operators, from manual to full', 'S21'),
    ('15×', 'growth in accelerator use at Google in 24 months', 'S3'),
    ('About 8%', 'of Google’s fleet usage was the memory allocator in 2015', 'P14'),
    ('Doubled in a year', 'the share of the fleet using profile-guided optimisation once it became automatic', 'P14'),
    ('Several hundred to one', 'developers to security experts, at Google and at small companies alike', 'P15'),
    ('60 to 70%', 'of high-severity vulnerabilities in large C and C++ codebases are memory-safety bugs', 'P15'),
    ('Over 70% to 24% in six years', 'Android’s memory-safety share after writing new code in safe languages', 'P15'),
    ('Zero in more than a decade', 'reported SQL injection in applications protected by safe query APIs', 'P12, P15'),
    ('About 20', 'web security controls enabled by default in Google’s frameworks', 'P15'),
    ('L0 to L3', 'SLSA build levels', 'P15'),
    ('Four engineers for several months', 'to build automated canary analysis; pays back within a year', 'P16'),
    ('8 billion screenshots', 'served by an internal tool run by about one part-time person, on shared infrastructure', 'P10'),
    ('More than 15 hours a week', 'developers spend on tasks other than writing application code', 'P18'),
    ('About 80%', 'of cases a golden path’s defaults should cover', 'P18, P19'),
    ('Under 18 months', 'of full-time work equals the hours in a computing degree', 'P24'),
    ('About fivefold in 15 years', 'growth in US computing enrolment, without matching teaching staff', 'P24'),
]


# ───────────────────────────────────────────────────────────── books 3 and 4: Mastering Prometheus (M) and Observability with Grafana (G)
EXEC[0] = ('The books in one paragraph each', EXEC[0][1] + [
    ('p', '<b>Mastering Prometheus</b> (Hegedus, 2024) goes underneath the query language. It explains how the time series database stores samples, how discovery and relabeling decide what is scraped, how Alertmanager routes and groups, and then how to scale: sharding, high availability, remote storage, Thanos, mixins, CI for rules, SLOs and OpenTelemetry. Its theme is that Prometheus is simple until it isn’t, and that most trouble is cardinality.'),
    ('p', '<b>Observability with Grafana</b> (Chapman and Holmes, 2024) is the wider view: logs with Loki, metrics with Mimir and Prometheus, traces with Tempo, collected by OpenTelemetry and joined up in Grafana. Its second half is about running observability for an organisation: dashboards built for a person and a question, incident management, automation, platform architecture, real user monitoring, profiling, load testing and the DevOps life cycle.'),
])
EXEC.insert(3, ('What the two observability books add', [
    ('ul', ['<b>Cardinality is the cost.</b> Every label value is a new series in memory, in the index and on the bill. Limit it at the scrape, review it in CI, and keep IDs out of labels. (M3, M7, G4, G15)',
            '<b>Know what rate() really does.</b> It is reset-aware and extrapolates to the window edges; use $__rate_interval and at least four scrape intervals. (M3, G5)',
            '<b>Alerting needs routing, not just rules.</b> Group, inhibit and silence in Alertmanager; send every Prometheus to every Alertmanager; add a dead man’s switch. (M5, M6, G9)',
            '<b>Scale by federation of storage, not of servers.</b> HA pairs with a replica label, then remote write or Thanos for global queries and retention. (M6, M9, M10)',
            '<b>Treat monitoring as code.</b> Mixins, unit-tested rules, Pint in pull requests, dashboards and alert rules in Terraform. (M11, M12, G10)',
            '<b>Burn-rate SLO alerts are generated, not hand-written.</b> Request-based for steady traffic, window-based for low traffic. (M13, S8)',
            '<b>Each signal stores different things.</b> Numbers in metrics, events in logs with few labels, high-cardinality context in traces; link them with exemplars and trace IDs. (G4, G5, G6, G11)',
            '<b>Collect with a topology.</b> Node agents, one cluster agent and a gateway that does tail sampling and span metrics, with buffers sized for outages. (G10, G11, M14)',
            '<b>Observability runs through the life cycle.</b> Local stacks while coding, SLO thresholds in load tests, annotations and automatic verification at deploy, RUM and profiles in operation. (G12, G13, G14)']),
    ('table', ['Idea', 'In SRE or platform book', 'In the observability books'], [
        ['SLOs and burn rate', 'Error budgets, multi-window alerts, low-traffic statistics (S8, S9)', 'Generated recording and alert rules, window-based SLOs, Pyrra and Sloth (M13)'],
        ['Golden signals', 'Latency, traffic, errors, saturation everywhere (S9, P16)', 'Golden signals, RED and USE; dashboards built around them (G8, G9)'],
        ['Incident roles', 'Commander, operations, communications (S10)', 'Commander, communications, technical lead, plus gold–silver–bronze (G9)'],
        ['Configuration as code', 'Config is tested and rolled out like code (S14, P15)', 'Rule unit tests, Pint, mixins, Terraform for Grafana (M11, M12, G10)'],
        ['Safe change', 'Canary analysis and automatic rollback (S14, P16)', 'Deployment annotations and verification queries in the pipeline (G14)'],
        ['Fleet-wide profiling', 'One profiler shows the costliest shared component (P14)', 'Continuous profiling with Pyroscope, eBPF or SDKs (G13)'],
        ['Platform SLOs', 'The platform needs stricter objectives (P16)', 'The observability platform needs its own SLOs and a disaster plan (G11, G15)'],
    ]),
]))
EXEC[-1][1][0][1].append('The two Packt observability books were read in full once, figures included; corrections to their examples are noted in the lessons and POCs.')

for theme, _, rows in MAP:
    for i, (c, d, r, poc) in enumerate(rows):
        add = {'SLI, SLO, SLA': ('M13, G9', '24'), 'Error budget': ('M13', '24'), 'Burn rate': ('M13', '24'), 'Low-traffic alerting': ('M13', '24'),
               'Observability': ('M1, G1', ''), 'Four golden signals': ('G8, G9', '29'), 'Client-side telemetry': ('G12', '30'), 'Fleet-wide profiling': ('G13', '30'),
               'Incident roles': ('G9', ''), 'Blameless postmortem': ('G9', ''), 'Configuration as code': ('M12, G10', '23, 29'), 'Automatic rollback': ('G14', '30'),
               'Sustainable on-call': ('G9', ''), 'Golden path': ('G10', ''), 'Platform SLOs': ('G15', ''), 'Platform as a product': ('G15', ''),
               'Progressive rollout': ('G14', '')}.get(c)
        if add:
            rows[i] = (c, d, f'{r}, {add[0]}', ', '.join(x for x in (poc, add[1]) if x))

MAP += [
    ('Metrics with Prometheus', 'How Prometheus stores, queries, alerts and scales.', [
        ('Series and cardinality', 'A metric name plus one label set; every new value is a new series in memory and index', 'M3, M7, G5', '21'),
        ('Head block, WAL and blocks', 'Two hours in memory with a write-ahead log, then immutable blocks compacted up to 31 days', 'M3, G5', '21'),
        ('Inverted index', 'Sorted postings lists per label pair, intersected shortest first', 'M3', '21'),
        ('rate, increase and irate', 'Reset-aware, extrapolated over the window; irate uses the last two samples', 'M3, G5', '20'),
        ('Vector matching', 'on, ignoring, group_left and group_right; and, or, unless for alert logic', 'M3', '20'),
        ('Relabeling', 'Rewrite targets before the scrape, series after it, and series before remote write', 'M4', '22'),
        ('Service discovery', 'Kubernetes, EC2, file and HTTP discovery turn inventory into targets', 'M4', '22'),
        ('Alertmanager routing', 'A tree of matchers with grouping, inhibition, silences and timers', 'M5, G9', '23'),
        ('High availability', 'Identical pairs differing by a replica label; deduplicate at query or write', 'M6, M9, M10', '25'),
        ('Sharding and federation', 'hashmod splits targets; federation only for small aggregates', 'M6', '22'),
        ('Scrape limits', 'sample_limit and label limits fail a scrape that would explode cardinality', 'M7, G15', '21'),
        ('Remote write', 'Sharded queues with backoff to long-term storage', 'M9, G5', '25'),
        ('Thanos, Mimir, VictoriaMetrics', 'Object-storage blocks with a global query layer, central multi-tenant ingestion, or efficient local disks', 'M9, M10, G5', '25'),
        ('Monitoring mixins', 'Jsonnet bundles of alerts, rules and dashboards, overridden through _config', 'M11', '29'),
        ('Rule CI', 'promtool syntax and unit tests, Pint against live data, in pull requests', 'M12', '23'),
        ('Window-based SLO', 'Count good and bad time windows instead of requests; suits low traffic', 'M13, S8', '24'),
    ]),
    ('Logs, traces and running observability', 'The rest of the Grafana stack, and observability as a platform.', [
        ('Loki labels are the index', 'Few low-cardinality labels; everything else is filtered or parsed at query time', 'G4', '26'),
        ('LogQL pipeline', 'Stream selector, line filters, parsers, typed label filters, formatting, metric functions', 'G4', '26'),
        ('Trace context', 'W3C traceparent and baggage carried across every hop; X-Ray and B3 at the edges', 'G6, M14', '27'),
        ('TraceQL', 'Select spansets by attributes and structure: child, descendant, sibling', 'G6', '27'),
        ('Exemplars', 'A trace ID attached to a metric sample, linking a spike to an example request', 'G5', ''),
        ('Tail sampling', 'Decide per whole trace in a gateway; keep errors and slow traces', 'G6, G11', '28'),
        ('Collector topology', 'Node agents, a single cluster agent and a gateway, with buffers sized for outages', 'G10, G11, M14', '28'),
        ('Connectors', 'spanmetrics and servicegraph derive RED metrics and service graphs from traces', 'G10', '28'),
        ('RED and USE', 'Rate, errors, duration for requests; utilisation, saturation, errors for resources', 'G9, S9', ''),
        ('Gold, silver, bronze', 'Strategic, tactical and operational levels of incident command', 'G9, S10', ''),
        ('Dashboard purpose', 'Who is it for, what do they need, where will they view it', 'G8', '29'),
        ('Dashboards and rules as code', 'Team folders, Terraform, linting in CI', 'G8, G10, M11', '29'),
        ('Real user monitoring', 'Web Vitals at p75 and sessions linked to backend traces', 'G12', '30'),
        ('Continuous profiling', 'Self time and total time; flame graph width is share of samples', 'G13, P14', '30'),
        ('Load test types', 'Smoke, average, stress, spike, breakpoint, soak; thresholds from SLOs', 'G13, S15', '30'),
        ('Deployment verification', 'Query telemetry after a deploy and roll back automatically', 'G14, S14, P16', '30'),
        ('Observability cost', 'Plan what you need, drop at collection, isolate noisy environments', 'G15, M7', '21'),
    ]),
]

REQS.insert(2, ('Metrics, logs and traces', [
    ('Every scrape job has sample and label limits, and new metrics are reviewed for cardinality', 'M7, G15', '21'),
    ('Prometheus runs as an HA pair sending to every Alertmanager in a cluster, with a dead man’s switch', 'M5, M6', '23, 25'),
    ('Alert and recording rules have unit tests and are linted in pull requests', 'M12', '23'),
    ('SLO burn-rate rules are generated from a spec, not written by hand', 'M13, S8', '24'),
    ('Loki labels are few and low-cardinality; IDs live in the log line', 'G4', '26'),
    ('W3C trace context is propagated everywhere, with conversion at AWS or B3 boundaries', 'G6, M14', '27'),
    ('Collectors run as node agents, one cluster agent and a gateway, with buffers sized for a backend outage', 'G11', '28'),
    ('Dashboards and alert rules live in Git, in team folders, applied with Terraform', 'G8, G10, M11', '29'),
    ('Every deployment is annotated and verified automatically against telemetry', 'G14', '30'),
    ('Load tests run with SLO thresholds, and their telemetry is kept out of production', 'G13', '30'),
    ('The observability platform has its own SLOs, cost dashboards and a tested disaster plan', 'G15', ''),
]))
for g, rows in REQS:
    for i, (req, r, poc) in enumerate(rows):
        add = {'Monitoring does not depend on the systems it monitors': 'M5, M6', 'Paging alerts fire on burn rate, confirmed by a short window': 'M13',
               'Anyone can declare an incident; roles are defined and practised': 'G9', 'User journeys are measured from the client side as well as the server': 'G12'}.get(req)
        if add:
            rows[i] = (req, f'{r}, {add}', poc)

NUMBERS += [
    ('2 hours', 'of samples in the Prometheus head block before it is cut into a block', 'M3'),
    ('2h → 6h → 18h → 54h', 'compaction steps, up to 31 days or 10% of retention', 'M3'),
    ('2 ms, at most 1% of the interval', 'scrape timestamp jitter Prometheus snaps away to keep timestamps cheap', 'M3'),
    ('30 s / 5 m / 4 h', 'Alertmanager group_wait, group_interval and repeat_interval defaults', 'M5'),
    ('2,500 / 500 / 200', 'remote write queue capacity, batch size and maximum shards', 'M9'),
    ('30 seconds', 'of silence before Mimir’s HA tracker fails over to the other replica', 'M9'),
    ('5 m after 40 h, 1 h after 10 days', 'Thanos downsampling', 'M10'),
    ('Replication factor 3', 'needs two successful writes in Thanos Receive', 'M10'),
    ('64 members, 8,192 bytes', 'W3C baggage limits', 'G6'),
    ('3 to 5', 'SLIs per service', 'G9'),
    ('1,440 against 8,640', 'queries a day per alert rule evaluated each minute against every 10 seconds', 'G9'),
    ('LCP 2.5 s, INP 200 ms, CLS 0.1', 'good Core Web Vitals, judged at the 75th percentile', 'G12'),
    ('15 seconds', 'default Pyroscope profiling interval', 'G13'),
]

M_LESSON = {1: 'm-1', 2: 'm-1', 3: 'm-3', 4: 'm-4', 5: 'm-5', 6: 'm-6', 7: 'm-7', 8: 'm-8', 9: 'm-9', 10: 'm-10', 11: 'm-11', 12: 'm-12', 13: 'm-13', 14: 'm-14', 15: 'm-14'}
G_LESSON = {1: 'g-1', 2: 'g-2', 3: 'g-2', 4: 'g-4', 5: 'g-5', 6: 'g-6', 7: 'g-7', 8: 'g-8', 9: 'g-9', 10: 'g-10', 11: 'g-11', 12: 'g-12', 13: 'g-12', 14: 'g-14', 15: 'g-14'}


# ───────────────────────────────────────────────────────────── rendering: Markdown
def _md(t):
    t = re.sub(r'<b>(.*?)</b>', r'**\1**', t)
    t = re.sub(r'<i>(.*?)</i>', r'*\1*', t)
    return H.unescape(re.sub(r'<[^>]+>', '', t))


def _poc_md(poc):
    return '' if not poc else poc if poc == 'docs' else 'POC ' + poc


def write_docs():
    out = ['# Executive summary: four books', '',
           '*Synthesis (pass 2) of the chapter summaries in `docs/chapters/`. S8 means SRE book chapter 8; P15 means platform book chapter 15 in the final numbering; M = Mastering Prometheus, G = Observability with Grafana.*', '']
    for title, blocks in EXEC:
        out += [f'## {title}', '']
        for kind, *rest in blocks:
            if kind == 'p':
                out += [_md(rest[0]), '']
            elif kind in ('ul', 'ol'):
                out += [(f'{i + 1}. ' if kind == 'ol' else '- ') + _md(x) for i, x in enumerate(rest[0])] + ['']
            elif kind == 'table':
                head, rows = rest
                out += ['| ' + ' | '.join(head) + ' |', '|' + '---|' * len(head)] + ['| ' + ' | '.join(_md(c) for c in r) + ' |' for r in rows] + ['']
    open(os.path.join(DOCS, 'executive-summary.md'), 'w', encoding='utf-8').write('\n'.join(out))

    out = ['# Knowledge map', '',
           f'*{len(MAP)} themes across all four books. Each row is a concept, a one-line definition, where it is taught, and the POC that implements it. S = SRE book chapter, P = platform book chapter (final numbering), M = Mastering Prometheus, G = Observability with Grafana.*', '']
    for theme, lead, rows in MAP:
        out += [f'## {theme}', '', lead, '', '| Concept | In one line | Chapters | Code |', '|---|---|---|---|']
        out += [f'| **{_md(c)}** | {_md(d)} | {r} | {_poc_md(poc)} |' for c, d, r, poc in rows] + ['']
    open(os.path.join(DOCS, 'knowledge-map.md'), 'w', encoding='utf-8').write('\n'.join(out))

    out = ['# Extracted requirements', '',
           '*What the four books say a team or platform should have in place, as a checklist. Use it to assess a system, or to structure a "how would you improve this?" answer. S = SRE book chapter, P = platform book chapter (final numbering), M = Mastering Prometheus, G = Observability with Grafana.*', '']
    n = 0
    for group, rows in REQS:
        out += [f'## {group}', '', '| | Requirement | Source | Code |', '|---|---|---|---|']
        for req, refs, poc in rows:
            n += 1
            out.append(f'| R{n} | {_md(req)} | {refs} | {_poc_md(poc)} |')
        out.append('')
    open(os.path.join(DOCS, 'requirements.md'), 'w', encoding='utf-8').write('\n'.join(out))

    out = ['## Numbers to know cold', '', '*Curated from all four books. The full mechanical extraction follows.*', '', '| Figure | What it is | Chapter |', '|---|---|---|']
    out += [f'| **{_md(a)}** | {_md(b)} | {c} |' for a, b, c in NUMBERS] + ['']
    return '\n'.join(out), n


# ───────────────────────────────────────────────────────────── rendering: course lessons
def _table(head, rows, cls=''):
    return (f'<div class="scroll"><table class="{cls}"><thead><tr>' + ''.join(f'<th>{h}</th>' for h in head) + '</tr></thead><tbody>'
            + ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows) + '</tbody></table></div>')


def _ref(refs):
    """S8 -> SRE chapter 8; P15 -> platform lesson for final chapter 15; M3 -> Prometheus lesson; G9 -> Grafana lesson."""
    pe = {9: 1, 10: 2, 12: 3, 14: 4, 15: 5, 16: 6, 18: 7, 19: 8, 22: 9, 24: 10}

    def one(m):
        book, n = m.group(1), int(m.group(2))
        if book == 'S':
            return f'<a href="#ch-{n}">S{n}</a>'
        if book == 'M':
            return f'<a href="#{M_LESSON[n]}">M{n}</a>'
        if book == 'G':
            return f'<a href="#{G_LESSON[n]}">G{n}</a>'
        return f'<a href="#pe-{pe[n]}">P{n}</a>' if n in pe else m.group(0)

    return re.sub(r'\b([SPMG])(\d+)\b', one, refs)


def _poc(poc):
    return '' if not poc else 'docs/platform' if poc == 'docs' else 'POC ' + poc


def lessons():
    def section(sec_id, dot, nav, chip, sub, h1, body):
        return (f'<section class="lesson" id="{sec_id}" data-part="7" data-dot="{dot}" data-title="{nav}">\n'
                f'<div class="meta"><span class="chip">{chip}</span>{sub}</div>\n<h1>{h1}</h1>\n{body}\n</section>')

    ex = '<p>The short version of all four books, and where they meet. S8 means SRE chapter 8; P15 means platform book chapter 15 in its final numbering; M3 means <i>Mastering Prometheus</i> chapter 3; G9 means <i>Observability with Grafana</i> chapter 9. The references are links.</p>'
    for title, blocks in EXEC:
        ex += f'<h2>{title}</h2>'
        for kind, *rest in blocks:
            if kind == 'p':
                ex += f'<p>{rest[0]}</p>'
            elif kind in ('ul', 'ol'):
                ex += f'<{kind}>' + ''.join(f'<li>{_ref(x)}</li>' for x in rest[0]) + f'</{kind}>'
            elif kind == 'table':
                ex += _table(rest[0], [[_ref(c) for c in r] for r in rest[1]])

    km = f'<p>{len(MAP)} themes across all four books. Each row is a concept, a one-line definition, the lessons that teach it and the POC that implements it. Use it to find your way back to a topic, or cover the middle column and test yourself.</p>'
    km += '<div class="parts">' + ''.join(f'<a href="#km-{i}" style="--c:var(--inkline)"><b>{t}</b><span>{len(rows)} concepts</span></a>' for i, (t, _, rows) in enumerate(MAP)) + '</div>'
    for i, (theme, lead, rows) in enumerate(MAP):
        km += f'<h2 id="km-{i}">{theme}</h2><p>{lead}</p>' + _table(['Concept', 'In one line', 'Lessons', 'Code'], [[f'<b>{c}</b>', d, _ref(r), _poc(poc)] for c, d, r, poc in rows])

    rq = ('<p>What the four books say a team or platform should have in place. Tick what is true of a system you know. The gaps are your answer to “how would you improve this?”. Your ticks are kept in this browser.</p>'
          '<p id="reqScore" style="font-weight:800"></p>')
    n = 0
    for group, rows in REQS:
        rq += f'<h2>{group}</h2><div class="reqs">'
        for req, refs, poc in rows:
            n += 1
            rq += (f'<label class="req"><input type="checkbox" data-req="R{n}"><span><b>R{n}</b> {req} '
                   f'<small>{_ref(refs)}{" · " + _poc(poc) if poc else ""}</small></span></label>')
        rq += '</div>'

    nm = ('<p>Figures interviewers expect you to produce without looking. Cover the middle column and say what each one is.</p>'
          + _table(['Figure', 'What it is', 'Lesson'], [[f'<b>{a}</b>', b, _ref(c)] for a, b, c in NUMBERS]))

    return [section('summary', 'F', 'Executive summary', 'Synthesis', 'All four books on one page', 'Executive summary', ex),
            section('map', 'G', 'Knowledge map', 'Synthesis', f'{sum(len(r) for _, _, r in MAP)} concepts in {len(MAP)} themes', 'Knowledge map', km),
            section('checklist', 'H', 'Requirements checklist', 'Synthesis', f'{n} requirements', 'Requirements checklist', rq),
            section('numbers', 'I', 'Numbers to know', 'Synthesis', f'{len(NUMBERS)} figures', 'Numbers to know cold', nm)]


CSS = '''
#map td:last-child{white-space:nowrap}
.reqs{display:grid;gap:6px;margin:12px 0 22px}
.req{display:flex;gap:12px;align-items:flex-start;padding:10px 12px;border:1px solid var(--rule);border-radius:10px;cursor:pointer}
.req:hover{background:var(--panel)}
.req input{flex:none;width:20px;height:20px;margin-top:3px;accent-color:var(--green)}
.req small{display:block;color:var(--mute);font-size:14px}
.req:has(input:checked){background:color-mix(in srgb,var(--green) 9%,var(--bg));border-color:color-mix(in srgb,var(--green) 40%,var(--rule))}
'''

JS = '''
{
const boxes=[...document.querySelectorAll('.req input')];let ticked=new Set();
try{ticked=new Set(JSON.parse(localStorage.getItem('sre_reqs')||'[]'))}catch(e){}
const show=()=>{const el=document.getElementById('reqScore');if(el)el.textContent=ticked.size+' of '+boxes.length+' in place'};
boxes.forEach(b=>{b.checked=ticked.has(b.dataset.req);b.addEventListener('change',()=>{b.checked?ticked.add(b.dataset.req):ticked.delete(b.dataset.req);try{localStorage.setItem('sre_reqs',JSON.stringify([...ticked]))}catch(e){}show()})});
show();
}
'''

if __name__ == '__main__':
    curated, n = write_docs()
    print('docs written;', n, 'requirements;', sum(len(r) for _, _, r in MAP), 'concepts;', len(NUMBERS), 'numbers')
