# Platform track, lessons 6-10, plus practice material.
from extras import flow, tiles, table, seq
from extras2 import pic, p, ul
from pe import L, h2, h3, note, deeper, code, ol

# ══════════════════════════════════════════════════════════════ 6 Reliability
_nines = '''
<line class="ln" x1="70" y1="230" x2="700" y2="230" marker-end="url(#ah)"/><line class="ln" x1="70" y1="230" x2="70" y2="24" marker-end="url(#ah)"/>
<path class="hl" d="M110 214C300 208 520 178 660 40"/>
<text transform="translate(34 130) rotate(-90)" text-anchor="middle" class="m">Cost and complexity</text>
''' + ''.join(f'<line class="dash" x1="{x}" y1="230" x2="{x}" y2="{y}"/><circle class="fc" cx="{x}" cy="{y}" r="6"/><text x="{x}" y="252" text-anchor="middle" class="b">{a}</text><text x="{x}" y="272" text-anchor="middle" class="m">{b}</text>'
                    for x, y, a, b in [(110, 214, '99%', '87.6 h a year'), (293, 199, '99.9%', '8.77 h'), (477, 153, '99.99%', '52.6 min'), (660, 40, '99.999%', '5.26 min')]) + '''
<text x="200" y="184" text-anchor="middle" class="m">engineering hygiene</text>
<text x="400" y="128" text-anchor="middle" class="m">dynamic and automated</text>
<text x="640" y="30" text-anchor="end" class="m">autonomous, sharded</text>'''
L.append(dict(
    id='pe-6', dot='6', part='P1', nav='Reliability', h1='Reliability: the platform turns SRE into a default',
    final=16, by='Bharath Modhipalli and Michelle Brush', poc='POC 16',
    learn=['Why reliability is a global cost that local teams underfund', 'How a platform encodes the four SRE principles, including risk profiles', 'What each extra nine requires, and why it can’t be funded team by team', 'What to shift down: blast radius and the cost of a mistake', 'Why the platform itself needs stricter SLOs than anything running on it'],
    body=(
        h2('The big picture')
        + p('Reliability means meeting what users expect, consistently and correctly. Uptime is one part of it. A system can be up and too slow to use, or up and returning wrong data. The chapter lists six dimensions: availability, latency, correctness, freshness, durability and throughput. For AI services, correctness becomes probabilistic.')
        + p('The central sentence of the chapter is this one, paraphrased: <b>SRE provides the blueprint for reliability, and platform engineering provides the machinery that produces reliable services at scale.</b> Asking every team to learn and apply SRE practices on their own doesn’t scale. The platform’s job is to capture those practices as code and APIs, so a team inherits them by using the standard path.')
        + h2('The economics: local savings, global costs')
        + p('Feature teams are rewarded for shipping. That is a local measure. When a team skips resilience work to ship sooner, the cost doesn’t disappear. It moves to the organisation as cascading failures, firefighting and cross-team incident response. Economists call that an externality.')
        + p('The chapter is kind about motive: teams rarely decide to trade reliability for speed. They assume everything will be fine. It names the result bluntly, though. Reliability becomes an <b>unfunded local mandate</b>, and everyone suffers.')
        + p('A platform internalises the cost. Building an automated canary analysis service might take four engineers several months. After that, no product team writes or watches its own deployment checks, and the investment typically pays back within a year.')
        + note('Canary analysis as a platform gate', 'Google’s service compares a new release’s telemetry (latency, errors, resource use) statistically against the version already running. It sits in the deployment platform as an automatic gate. A significant regression stops the rollout and triggers a rollback. Nobody stares at a dashboard during a deploy.')
        + h2('Four SRE principles, encoded')
        + table(['Principle', 'What the platform does', 'Example from the chapter'],
                [['Operations is a software problem', 'Replaces manual work with self-service', 'Customer onboarding that took weeks of configuration becomes automated, which is faster and makes fewer mistakes'],
                 ['Eliminate toil', 'Automates routine approvals', 'Cloud quota increases needed an engineer for hours and customers waited days. Now the system validates and approves reasonable requests itself'],
                 ['100% is the wrong target', 'Enforces the velocity-risk balance in the delivery tooling', 'Risk profiles (below)'],
                 ['Learn from incidents', 'Changes the system so the right action is easy and the wrong one is hard', 'Ask what made the action look right to the person at the time, then change the platform']])
        + h3('Risk profiles')
        + p('This is the most concrete new idea in the chapter. A service’s <b>risk profile</b> sets its deployment policy, so nobody has to judge how careful to be with each change.')
        + table(['Service', 'Policy the platform applies'],
                [['Critical, with a tight error budget', 'Multi-stage progressive rollout, long canary bake times, strict automated supervision'], ['Low-risk internal tool, or plenty of budget left', 'Permissive: changes reach production quickly']])
        + p('The organisation’s risk tolerance is enforced by the pipeline. The safe choice is the default, and low-risk work isn’t slowed down to protect high-risk work.')
        + h2('Getting the nines')
        + pic(720, 290, _nines, 'Allowed downtime shrinks tenfold with each nine while the cost of getting there climbs steeply. Downtime figures are from the chapter.', 'Curve of cost and complexity against availability target, rising gently to 99.9% and steeply to 99.999%, with yearly downtime for each level.')
        + table(['Target', 'What it takes', 'Who can fund it'],
                [['Two to three nines', 'Engineering hygiene: error budgets, standard pipelines, basic telemetry, automated backups, static multi-zone redundancy, regional load balancing', 'Well understood, but still belongs in the platform. Otherwise every team rebuilds it, or quietly skips it'],
                 ['Four nines', 'A steep step. Active-active across clusters, global application-layer load balancing, N+1 planning by region, automated failover, dynamic capacity, distributed tracing, automated canary analysis and rollback, fault injection and chaos testing', 'Only a shared platform. Per-team funding is unsustainable'],
                 ['Five nines', 'Sharded serving, smart retries everywhere, request hedging, staggered change propagation, autonomous response, analysis of near misses', 'Only the most critical shared components']])
        + p('Spanner is the example at the top. Its multi-region service is offered at five nines, and getting there took dedicated GPS receivers and atomic clocks in every data centre for globally consistent time, plus consensus replication across regions. No product team could justify that. As a platform service, a team provisions an instance and inherits it.')
        + deeper('what to shift down, the capabilities, and the platform’s own reliability')
        + h2('What belongs in the platform')
        + p('Not everything. A platform stuffed with business-specific logic becomes rigid and hard to understand. The chapter gives a risk-driven test.')
        + tiles([('Blast radius', 'If one team’s misconfiguration can hurt everyone, the platform must enforce a standard. One service retrying aggressively without backoff can overwhelm shared databases and load balancers.', 'red'),
                 ('Complexity', 'If a capability takes rare expertise, such as multi-region failover or canary statistics, abstract it so teams don’t each build it.', 'orange'),
                 ('Cost of a mistake', 'If an error is minor, leave teams free to choose. If it could be catastrophic, such as draining every region or losing data, the platform takes responsibility and blocks it.', 'purple')])
        + p('Retries are the model case. Google didn’t ask each developer to write careful backoff loops. Its RPC framework provides adaptive throttling and retry budgets and sheds excess load on the client side. gRPC is the public descendant of that framework.')
        + h2('Six capabilities to shift down')
        + table(['Capability', 'What the platform provides', 'Google example'],
                [['Abstracting infrastructure', 'You declare desired state; the platform keeps it true and reschedules around failures. Critical services can’t be deployed to a single zone', 'Borg, which makes machine failure invisible to services'],
                 ['Safe change management', 'One opinionated pipeline: staged rollouts, automated canary analysis, automatic rollback, and a clear view of what is deployed where', 'The Rollouts platform, whose goal is to make production changes boring and predictable'],
                 ['Capacity', 'Forecast-based provisioning, autoscaling and N+1 redundancy by default', 'A long-term planner that forecasts and places capacity, and an autoscaler that reacts in minutes, both horizontally and vertically'],
                 ['Preventing unsafe operations', 'Invariants enforced in code, not in documents', 'A command that would drain more than one region is rejected'],
                 ['Standard observability', 'The four golden signals for every service, same names and method everywhere, and SLO tracking as a service', 'One monitoring system fed automatically by every job; tracing built into the RPC library'],
                 ['Constant evolution', 'Lessons from incidents become platform changes', 'See “institutional memory” below']])
        + p('Two details in that table are worth saying aloud. Capacity changes are rolled out through the <i>same</i> progressive pipeline and canary checks as software, so an infrastructure change is as safe as a release. And the platform owns the <i>how</i> of deployment while the developer owns the <i>what</i>.')
        + note('Break-glass, done properly', 'Strict rules sometimes have to be bypassed to restore service. Suppose only signed, scanned images may deploy, and an emergency fix can’t wait for the full pipeline. A break-glass mechanism lets responders override the policy with an explicit marker on the deployment. The important part is what happens next: the override is written to the audit log, a high-priority alert goes to security and operations, and the record is permanent for review afterwards. It is a platform feature with accountability, never a silent bypass.')
        + h3('Observability and the human')
        + p('The chapter describes an incident as a <b>joint cognitive system</b>: people and tools share a working memory, with operators relying on the system to show them what is happening. When every service’s metrics have the same names and every dashboard the same layout, responders work from muscle memory and spend their attention on the problem. When each service is different, they spend the first critical minutes decoding the environment.')
        + p('For AI and agent workloads the golden signals aren’t enough. Add model freshness, version skew, data quality and probabilistic correctness, and for agents: tokens used, end-to-end latency of an invocation, and which external tools were called and how often.')
        + h3('The platform as institutional memory')
        + p('If several teams have outages from the same kind of misconfiguration, the answer is not retraining or a documentation update. Change the platform: add validation, change the default, or remove the setting altogether. That is how an organisation stops having the same outage.')
        + p('A related feature at Google: any change in source control can be marked as a <b>bad change</b>, and the deployment system then refuses every rollout that contains it.')
        + h2('The reliability of the platform itself')
        + p('Centralising makes the platform the most critical system in the company. If the deployment system is down, nobody can release, and nobody can roll back either. If monitoring is down, everyone is blind. A reliable platform multiplies stability for everything on it. An unreliable one aggregates risk.')
        + p('So platform teams must apply SRE to themselves, and to a higher standard than the applications they host.')
        + ul(['<b>Strict, published SLOs</b> for the platform: build success rate, deployment latency, monitoring ingestion lag.', '<b>Defence in depth:</b> no internal single points of failure, and graceful degradation.', '<b>Conservative rollouts</b> with fast rollback, because a platform bug has the whole organisation as its blast radius.', '<b>Disaster practice</b> for the case where the platform is the thing that is down.'])
        + table(['Platform', 'What its SLOs cover'],
                [['Cluster scheduler', 'Scheduling latency and the share of tasks ready to serve, with tiers: strict for user-facing jobs, relaxed for batch'],
                 ['Build service', 'Failures caused by the system, deliberately excluding errors the user caused, with latency targets by priority'],
                 ['Monitoring', 'Ingestion lag and timely availability, so alerts can be trusted during an outage']])
        + p('Publishing these turns “the platform is reliable” from a promise into a measurable agreement.')
        + h2('What the organisation gets')
        + tiles([('Sublinear scale', 'Without a platform, operational effort grows in step with the number of services. With one, the cost of each capability is paid once and each fix lands everywhere.'),
                 ('Lower cognitive load', 'Reliability stops being a pre-launch checklist and becomes the physics of the environment.'),
                 ('Fast diagnosis', 'The first question in an outage is “what changed?” A platform has one audit trail for binaries, configuration, flags and infrastructure.'),
                 ('Fleet-wide remediation', 'Patch a shared runtime or proxy once and roll it out everywhere. That is the payoff of golden paths.')])
        + p('The contract from the shared-fate lesson applies. Teams that bypass guardrails or go bespoke create debt the platform can’t see, scale or heal, and the burden returns to them. Staying on the standard path keeps a service <i>eligible</i> for automated capacity, failover and fleet-wide fixes.')),
    say='SRE tells you what reliable looks like; the platform is how you get it for every team without each one learning it the hard way. I’d put into the platform anything with a wide blast radius or a catastrophic failure mode: safe rollouts with automated canary analysis, retry budgets, multi-zone placement, capacity, standard telemetry and SLO tracking. I’d tie deployment strictness to each service’s risk profile. And I’d hold the platform itself to tighter SLOs than its tenants, because when it fails everyone fails.',
    aws='Risk profiles map well to CodeDeploy deployment configurations and AppConfig deployment strategies: pick linear or canary steps and bake times by service tier, with CloudWatch alarms for automatic rollback. Abstract infrastructure with EKS or ECS spread across at least three Availability Zones through topology constraints the golden path sets for you. Capacity: predictive and target-tracking Auto Scaling, Karpenter on EKS. Unsafe operations: Service Control Policies, Route 53 ARC safety rules that refuse to turn off too many cells at once, deletion protection and AWS Backup with Vault Lock. Observability: Application Signals for golden signals and SLOs on every service, X-Ray or OpenTelemetry tracing injected by the platform. Break-glass: a dedicated emergency role whose use is logged by CloudTrail and raises an EventBridge alert. For the platform itself, publish SLOs for pipeline success, deploy latency and telemetry lag, and test them with Fault Injection Service.',
    iq=[('How do you decide which reliability features go into the platform and which stay with product teams?',
         ['I use three tests. The first is blast radius: if one team getting it wrong can hurt other teams, it belongs in the platform. Retry behaviour is the classic case. A service that retries hard without backoff can take down a shared database, so the client library should enforce backoff and a retry budget for everyone.',
          'The second is complexity. If doing it well needs rare expertise, such as statistical canary analysis or multi-region failover, building it once and offering it as a service is cheaper than having twenty teams each build a worse version.',
          'The third is the cost of a mistake. If the worst outcome is minor, I leave the team free to choose. If it is catastrophic or irreversible, such as draining all regions or deleting the only copy of data, the platform should make it impossible, with a logged break-glass path for genuine emergencies.',
          'What I keep out is business logic. A platform that knows about one product’s special cases becomes rigid and harder for everyone else to understand.',
          'Then I match strictness to risk. A critical service with little error budget gets slow staged rollouts and long bake times automatically. An internal tool gets a fast path. That keeps the safe default from becoming a tax on low-risk work.']),
        ('Your deployment platform had an outage and nobody could ship or roll back for two hours. What do you change?',
         ['I’d treat it as the most serious kind of incident, because the deployment system is how every other incident gets mitigated. Losing it removes the main tool for recovery everywhere.',
          'First, the platform needs its own SLOs, stricter than its tenants’, and published: pipeline success rate counting only system-caused failures, time from merge to deployed, and availability of the rollback path as its own objective.',
          'Second, I’d separate the rollback path from the rest. Rolling back to a known-good version should depend on as little as possible: no build step, no external registry call that can fail, cached artifacts. I’d test it with fault injection.',
          'Third, the platform should be rolled out more conservatively than anything it deploys: staged across cells or regions with bake time, so a platform bug hits a fraction of teams first.',
          'Fourth, a break-glass route for when the platform is down: a documented, audited manual deployment that responders have practised.',
          'And I’d run the postmortem with the same question we ask of product teams: what made this failure possible, and which default should change so it can’t recur?'])],
    quiz=[['According to the chapter, what is the primary trigger for shifting a reliability capability into the platform?', ['It is fashionable', 'The potential blast radius of getting it wrong', 'A team asks for it', 'It is cheap to build'], 1, 'If one team’s misconfiguration can cascade to others, the platform must enforce a standard. Complexity and the cost of a mistake are the other tests.'],
          ['What makes a break-glass mechanism acceptable?', ['Only senior engineers know about it', 'It bypasses policy silently so responders are fast', 'Every use is logged, alerted on and reviewed afterwards', 'It is disabled in production'], 2, 'Break-glass is a platform feature with accountability. The override is permitted and immediately visible.'],
          ['Roughly how much downtime a year does 99.99% availability allow?', ['8.77 hours', '52.6 minutes', '5.26 minutes', '87.6 hours'], 1, 'Four nines is about 52.6 minutes a year; three nines is 8.77 hours; five nines is 5.26 minutes.']],
    turn='Run <b>POC 16</b>. It turns a service’s tier and remaining error budget into a rollout plan, rejects operations that break an invariant (such as draining too many regions at once), and records a break-glass override with an audit entry. Change a service from tier 1 to tier 3 and compare the plans.',
    take=['SRE is the blueprint; the platform is how every team gets it by default.', 'Shift down what has a wide blast radius, needs rare expertise, or fails catastrophically.', 'Each nine costs far more than the last, so only a shared platform can fund the top ones.', 'The platform needs stricter SLOs than anything it hosts.']))

# ══════════════════════════════════════════════════════════════ 7 DevEx
_api = ''.join(f'<rect class="pn" x="30" y="{20 + i * 58}" width="170" height="44" rx="8"/><text x="115" y="{47 + i * 58}" text-anchor="middle" class="b">{t}</text><line class="ln" x1="200" y1="{42 + i * 58}" x2="296" y2="{103 + i * 18}" marker-end="url(#ah)"/>'
               for i, t in enumerate(['Web console', 'Command line', 'Infrastructure as code', 'AI agents'])) + '''
<rect class="pn" x="300" y="84" width="170" height="92" rx="10" style="stroke:var(--c);stroke-width:3"/><text x="385" y="124" text-anchor="middle" class="b">One platform API</text><text x="385" y="146" text-anchor="middle" class="m">every capability</text>
<line class="ln" x1="470" y1="130" x2="536" y2="130" marker-end="url(#ah)"/>
<rect class="pn" x="540" y="84" width="160" height="92" rx="10"/><text x="620" y="124" text-anchor="middle" class="b">Capabilities</text><text x="620" y="146" text-anchor="middle" class="m">deploy, provision…</text>'''
L.append(dict(
    id='pe-7', dot='7', part='P2', nav='Developer experience', h1='Developer experience: platforms nobody uses are worth nothing',
    final=18, by='Eric Maxwell', poc='POC 18',
    learn=['The platform paradox and the “build it and they will come” fallacy', 'What “broccoli” means in this book', 'Three dimensions and seven pillars of developer experience', 'How to cultivate it, and how to measure it'],
    body=(
        h2('The big picture')
        + p('Organisations spend heavily on internal platforms that are robust, scalable and technically impressive, and then watch adoption stall. Developers keep their old scripts or build unofficial tools around the official one. The platform team is frustrated that nobody appreciates what they built. Developers feel burdened by tools that make their work harder.')
        + p('The chapter calls this the <b>platform paradox</b>. Its explanation is that a platform succeeds or fails less on what it technically provides than on what it is like to use.')
        + h2('“Build it and they will come”')
        + p('This is the belief that a technically superior platform attracts users by itself. It misreads developers in three ways.')
        + tiles([('It ignores their workflow', 'People have tuned how they work. A tool that makes them abandon that feels like an implant, not an extension.', 'red'),
                 ('It costs too much attention', 'If understanding the platform takes more thought than the business problem, people look for an easier route.', 'red'),
                 ('The payoff is too far away', 'Developers are measured on what ships now. A steep learning curve with long-term benefits loses to a simple fix today, and that is a rational choice.', 'red')])
        + note('The broccoli problem', 'An old saying inside Google went roughly: things that should be easy are medium-hard here, and things that should be impossible are also medium-hard. An engineer made a short cartoon, known as the “Broccoli Man” video, in which someone only wants to serve five terabytes of data and is buried in process. In this book, <b>broccoli</b> means paying the setup and running costs of a billion-user system for something small: an internal tool, a prototype, a dashboard. It doesn’t come from incompetence. It comes from putting an application on the wrong kind of platform. The chapter’s example: three days to bring up a “hello world” server because the platform demands cluster names and outdated access settings, for a task that is a one-click form elsewhere.')
        + p('The costs go beyond wasted investment: lower productivity and morale, burnout, less experimentation, and unofficial tooling that adds debt and security risk.')
        + h2('What developer experience is')
        + p('The chapter’s definition, in my words: developer experience is everything a developer encounters, perceives and feels when dealing with a platform, its tools <i>and the team behind it</i>. It is a technical discipline about removing friction, and has little to do with keeping people cheerful.')
        + tiles([('Feedback loops', 'How fast and how clear the response to an action is. Test times, build times, the quality of an error message.', 'magenta'),
                 ('Cognitive load', 'How much thinking a task needs. Driven by complexity, the number of tools, and the quality of abstractions.', 'magenta'),
                 ('Flow state', 'Uninterrupted, absorbed work. Broken by waiting, context switches, external dependencies and toil.', 'magenta')])
        + h3('Seven pillars')
        + table(['Pillar', 'What good looks like'],
                [['Usability and simplicity', 'Interfaces are predictable and easy to learn'],
                 ['Discoverability and onboarding', 'People find what they need. The time to a first “hello world” is short and guided'],
                 ['Fast, clear feedback', 'Builds, tests and deploys are quick. Errors say what went wrong and what to do'],
                 ['Reliability and trust', 'The platform behaves the same way every time'],
                 ['Workflow integration', 'API-first, so every interface has the same abilities (below)'],
                 ['Flexibility and escape hatches', 'Sensible defaults for about 80% of cases, and a supported way out for legitimate special needs. Paved roads shouldn’t be prisons'],
                 ['Documentation and support', 'Accurate, searchable, full of working examples, with responsive help. Research finds documentation quality predicts whether teams can adopt practices like continuous delivery']])
        + pic(730, 262, _api, 'API-first. The console is one client of the API, exactly like the command line, infrastructure-as-code providers and agents. Nothing can be done in one that can’t be done in the others.', 'Four interfaces (web console, command line, infrastructure as code, AI agents) all call one platform API, which exposes the capabilities.')
        + p('This settles the old argument about clicking in a console versus automating. A good console is the best way to explore and understand a system’s state. The API underneath means the same action can be scripted when it becomes routine. People move from exploring by hand to automation without changing tools.')
        + deeper('the business case, how to cultivate it, and what to measure')
        + h2('Why it is a business matter')
        + ul(['<b>Productivity.</b> The best-performing organisations in the DORA research aren’t working longer hours. Their tools remove friction, so lead times are hours, not weeks. One survey cited in the chapter found developers spend more than 15 hours a week on tasks other than writing application code.',
              '<b>People.</b> Satisfaction with tools tracks team performance and lower burnout. An employee recommendation score measures past friction, which makes a falling score an early warning of future productivity loss. Good tooling also helps hiring and retention.',
              '<b>Innovation.</b> If trying an idea takes minutes, people try ideas. That is psychological safety in practical form.',
              '<b>Risk.</b> A service template that arrives with security scanning, structured logging and monitoring already wired makes the right way the easy way. Developers meet complex standards without becoming experts in them. Investing in experience is investing in risk management, which matters most in regulated industries.'])
        + h2('Cultivating it: build with, not for')
        + table(['Practice', 'How'],
                [['Interviews and observation', 'Ask developers to walk you through their work. Watching where they get stuck tells you more than asking what they want'],
                 ['Informal usability tests', 'Have someone try a new feature while sharing their screen and thinking aloud. Minutes, not weeks'],
                 ['Mine the support channels', 'Recurring questions point at gaps in documentation or flaws in design'],
                 ['Personas and journey maps', 'A new hire, a frontend specialist and a principal backend engineer need different things. Check the personas against real work'],
                 ['Close the loop', 'Act on feedback and say what changed. That is what earns more feedback'],
                 ['Value stream mapping', 'Draw every step, hand-off and wait from idea to production. The waits are where flow dies']])
        + p('Then make sure people know. The chapter lists: a public roadmap and clear release notes; documentation treated as a feature; support that behaves like a partner and never like a gatekeeper; a user community; <b>champions</b> in product teams who get previews and a direct line; and published success stories. This has to be in the platform team’s charter, with time allotted.')
        + note('Go as a developer-experience story', 'The Go language began because three senior engineers were suffering with slow builds, tangled dependencies and awkward concurrency in C++. They were their own users. Experience was designed in from the start: a formatter that ended style arguments, simple dependency fetching, built-in testing and a fast compiler. The creators acted as the first champions and worked closely with early adopter teams. It spread from the ground up because the compiler and tooling were treated as a product.')
        + h2('Measuring it')
        + table(['Kind', 'Metric', 'What it tells you'],
                [['Numbers', 'HEART: happiness, engagement, adoption, retention, task success', 'Google’s user-experience framework, applied to an internal platform'],
                 ['Numbers', 'Adoption and retention', 'Active users against those who tried it once and left'],
                 ['Numbers', 'Task time and first-attempt success', 'Friction, directly. How long to deploy a new service? How often without asking for help?'],
                 ['Numbers', 'DORA delivery metrics: lead time, deployment frequency, change failure rate, failed-deployment recovery time, rework rate', 'Compare teams on the platform with teams off it. The strongest proof of value'],
                 ['Opinions', 'Satisfaction and “would you recommend this platform?” scores', 'Sentiment over time'],
                 ['Opinions', 'Themes in interviews, surveys and tickets', 'The reasons behind the numbers']])),
    say='A platform is only worth what its adoption is worth, and adoption depends on how it feels to use. I look at three things: how fast and clear the feedback is, how much a developer has to hold in their head, and how often they’re interrupted. I’d build with the users, watching them work, then measure time to first deploy, first-attempt success, and delivery metrics for teams on the platform against teams off it.',
    aws='Give the platform one API and let every interface sit on it: a Backstage portal or Service Catalog for discovery, the same actions available through the CLI, CDK constructs or Terraform modules, and tool definitions agents can call. Golden-path templates should arrive with a pipeline, IAM roles, alarms, dashboards and tracing already configured, so the first deploy takes minutes. Measure it: emit pipeline events through EventBridge to compute lead time, deployment frequency and failure rate per team, and track time from repository creation to first production deploy. Provide an escape hatch as a documented, supported extension point instead of leaving teams to fork the template.',
    iq=[('Your platform team built a deployment system that is clearly better than what teams use, and adoption is 15%. What do you do?',
         ['I’d assume the problem is the experience, not the users, and go and watch.',
          'I’d sit with three or four teams, some who adopted and some who didn’t, and ask them to deploy something while I observe. I’m looking for where they stop: an unclear error, a concept they have to learn first, a step that needs a ticket, something their current script does that ours doesn’t.',
          'I’d measure the first-run experience. How long from nothing to a first successful deploy, and how often it works on the first attempt without help. If that is days, nothing else matters yet.',
          'I’d check for broccoli: are we making a small internal service fill in the same configuration as our largest product? If so, we need a lighter path with good defaults.',
          'Then I’d fix the top two or three sources of friction, tell people what changed, and recruit a champion in each adopting team. I’d publish one honest success story with numbers.',
          'I would not reach for a mandate first. A mandate without a good product gets compliance on paper and workarounds in practice. If a mandate is eventually needed for security or compliance reasons, it goes much better after the product is something people would choose.'])],
    quiz=[['In this book, what does “broccoli” mean?', ['Unpopular but healthy security rules', 'Paying the setup and running cost of a billion-user system for a small project', 'Legacy code', 'A slow build'], 1, 'It is the mismatch of putting a small application on a platform built for enormous scale. Nobody is being incompetent; the application is in the wrong kind of ecosystem.'],
          ['What does an API-first platform guarantee?', ['The console is the most powerful interface', 'Every interface (console, CLI, infrastructure as code, agents) can do the same things, because all sit on one API', 'There is no console', 'Only automation is supported'], 1, 'Functional parity. People can explore in the console and automate the same action later.']],
    turn='Time your own platform’s first-run experience. Starting from an empty directory, how long does it take a new team member to get a “hello world” service into production, and how many times do they need to ask someone? Then run <b>POC 18</b>, which computes adoption, retention, first-attempt success and delivery metrics for adopters against non-adopters from sample event data.',
    take=['Adoption depends on the experience of use more than on technical merit.', 'Three dimensions: feedback loops, cognitive load, flow.', 'Build with your users, give them a way out for special cases, and measure adopters against non-adopters.']))
