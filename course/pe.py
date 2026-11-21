# Second track: "Platform Engineering at Google" (O'Reilly early release). Hand-written lessons, my own words.
from extras import flow, tiles, table, seq
from extras2 import pic, p, ul

BOOK = 'Platform Engineering at Google'


def h2(t):
    return f'<h2>{t}</h2>'


def h3(t):
    return f'<h3>{t}</h3>'


def note(title, text, cls=''):
    return f'<div class="note{" " + cls if cls else ""}"><b>{title}</b>{text}</div>'


def deeper(t):
    return f'<div class="deeper"><span>Going deeper</span> {t}</div>'


def code(src):
    esc = src.strip('\n').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return f'<pre><code>{esc}</code></pre>'


def ol(items):
    return '<ol>' + ''.join(f'<li>{i}</li>' for i in items) + '</ol>'


L = []

# ══════════════════════════════════════════════════════════════ intro
L.append(dict(
    id='pe', dot='P', part='P1', nav='About this book', h1='Platform engineering: the second book on the map',
    meta='<span class="chip">Platform Engineering at Google</span>O’Reilly early release · 10 of a planned 31 chapters',
    learn=['What this book argues, in one paragraph', 'Which chapters exist today and where they sit in the final book', 'How it connects to the SRE lessons you have already done'],
    body=(
        h2('The argument in one paragraph')
        + p('Every engineering organisation wants the same things from its software: secure, reliable, efficient, compliant. The usual way to get them is to ask every developer to remember every rule. That fails at scale, because developers are human and there are never enough experts to check their work.')
        + p('Platform engineering takes the opposite route. It moves those responsibilities <b>down</b> into the things developers already build on: languages, libraries, frameworks, build systems, deployment pipelines, runtime infrastructure. Experts solve a problem once, inside the platform, and every team inherits the answer. The book calls this <b>shifting down</b>. It is different from shifting left, which moves the same work earlier but leaves it with the developer.')
        + flow([('Shift left', 'Find the problem earlier. The developer still has to find it', 'orange'), ('Shift down', 'Make the problem impossible, or handled by default, in the platform', 'green')],
               'Shift left reduces the cost of each mistake. Shift down reduces the number of mistakes that can be made.')
        + p('If you finished the SRE lessons, you met this idea in <a href="#ch-18">chapter 18</a>, with its 0-to-4 scale from YOLO to Assured. This book is the long version, written by the people who built Google’s internal platforms.')
        + h2('What is in the early release')
        + p('The book is still being written. O’Reilly publishes chapters as they are drafted, so the numbering you see online is temporary. Ten chapters are available. I read all ten in full, and all five figures. The other twenty-one are listed in the table of contents and can’t be read yet, so they are not in this course.')
        + table(['Lesson', 'Topic', 'Final chapter', 'Author'],
                [['<a href="#pe-1">1</a>', 'Coupling', '9', 'Michelle Brush'], ['<a href="#pe-2">2</a>', 'Layers', '10', 'Kaan Kivilcim'], ['<a href="#pe-3">3</a>', 'Shared fate and responsibility', '12', 'Andy Qin'],
                 ['<a href="#pe-4">4</a>', 'Deep dive: efficiency', '14', 'Chris Kennelly'], ['<a href="#pe-5">5</a>', 'Deep dive: security', '15', 'Christoph Kern'], ['<a href="#pe-6">6</a>', 'Deep dive: reliability', '16', 'Bharath Modhipalli and Michelle Brush'],
                 ['<a href="#pe-7">7</a>', 'Why developer experience matters', '18', 'Eric Maxwell'], ['<a href="#pe-8">8</a>', 'Platform as a product', '19', 'Eric Maxwell'], ['<a href="#pe-9">9</a>', 'AI with platform engineering', '22', 'Isaac Albarran with Konrad Dryja'], ['<a href="#pe-10">10</a>', 'Education and platform engineering', '24', 'Titus Winters']])
        + note('What you can’t read yet', 'Chapters on what platform engineering is, ecosystem types, modular abstractions, quality attributes, shifting down, golden paths, platform ROI, measuring success, migrations and getting started are planned and not published. Several of the available chapters refer to them. Where a lesson leans on one of those, I say so.')
        + h2('Five words the whole book uses')
        + table(['Term', 'Meaning'],
                [['Developer ecosystem', 'Everything an organisation could build with: languages, libraries, frameworks, build tools, runtimes, practices. A marketplace of parts.'],
                 ['Developer platform', 'An opinionated selection from that marketplace, integrated and configured for one kind of application, so that quality comes by design and by default.'],
                 ['Quality attributes', 'The “ilities”: security, reliability, efficiency, compliance, maintainability. What a platform is meant to guarantee.'],
                 ['Golden path / well-lit path / paved road', 'The supported, documented, easiest way to do a common task. Three names for one idea.'],
                 ['Ecosystem type', 'How tightly integrated an ecosystem is. Type 2 is guided, type 3 engineered, type 4 assured. The more integrated, the more the platform can promise.']])
        + h2('How to study this track')
        + tiles([('Architecture first', 'Lessons 1 to 6: coupling, layers, shared fate, then the three deep dives. These are design questions.', 'magenta'),
                 ('Then execution', 'Lessons 7 to 10: developer experience, product management, AI, education. These are leadership questions.', 'lime'),
                 ('Then the code', 'POCs 12 to 19 in the repo turn each idea into something you can run, mapped to AWS.')])),
    take=['Shift down means the platform takes the responsibility; shift left only moves it earlier.', 'A platform is an opinionated assembly from an ecosystem, built for one kind of application.', 'Ten chapters are published. The lessons cover those and nothing else.']))

# ══════════════════════════════════════════════════════════════ 1 Coupling
_cpl = '''
<line class="ln" x1="320" y1="190" x2="320" y2="30" marker-end="url(#ah)"/><line class="ln" x1="320" y1="190" x2="530" y2="305" marker-end="url(#ah)"/><line class="ln" x1="320" y1="190" x2="110" y2="305" marker-end="url(#ah)"/>
<text x="332" y="38" class="b">Efficiency</text><text x="540" y="322" text-anchor="end" class="b">Performance</text><text x="100" y="322" class="b">Retargetability</text>
<path d="M320 55L490 283L270 217z" class="fc" style="opacity:.16"/><path class="hl" d="M320 55L490 283L270 217z"/>
<path class="dash" d="M320 122L420 245L140 289z"/>
<text x="446" y="130" class="b">Tightly coupled</text><text x="446" y="150" class="m">cheap to run, fast,</text><text x="446" y="168" class="m">hard to reuse elsewhere</text>
<text x="30" y="170" class="b">Loosely coupled</text><text x="30" y="190" class="m">flexible, costs more</text>'''
L.append(dict(
    id='pe-1', dot='1', part='P1', nav='Coupling', h1='Coupling: decide what depends on what',
    final=9, by='Michelle Brush', poc='POC 12',
    learn=['Explicit and implicit coupling, tight and loose, and how cohesion relates', 'Four reasons to couple on purpose and four costs of doing it', 'Five patterns that loosen coupling and four antipatterns that tighten it by accident', 'Four ways to find coupling nobody intended'],
    body=(
        h2('The big picture')
        + p('Coupling is how much the parts of a system depend on each other. It is usually talked about as a defect. This chapter’s position is more useful: some coupling is unavoidable, some is valuable, and the real failure is coupling nobody chose.')
        + p('Two distinctions set up everything else.')
        + table(['', 'Meaning', 'Example'],
                [['Explicit', 'One part calls another directly', 'A service makes an RPC to another service'],
                 ['Implicit', 'No direct interaction, but one part assumes the other exists or behaves a certain way', 'A producer writes to a queue. It has never heard of the consumer, and a change to the message format still breaks it'],
                 ['Tight', 'Parts know each other’s internals', 'A service reads another team’s database tables'],
                 ['Loose', 'Parts know only each other’s interfaces', 'A service calls a versioned API']])
        + p('<b>Cohesion</b> is the mirror image: how closely related the things inside one module are. A module with low cohesion does many unrelated jobs, so either it depends on many things or many things depend on it. Low cohesion and high coupling tend to arrive together.')
        + h2('When coupling pays')
        + tiles([('Efficiency', 'One safe path for everyone. Google’s tooling is coupled to its issue tracker, so every change has a tracked reason and bugs close themselves when the fix is fully rolled out.', 'green'),
                 ('Performance', 'Fewer layers and hops. Spanner can interleave child rows with their parent. Maths lives in libraries, not services, because an RPC would cost more than the sum.', 'green'),
                 ('Atomicity', 'All-or-nothing changes. Deleting a cloud project must also delete its VMs and disks, or resources leak.', 'green'),
                 ('Traceability', 'Follow data end to end. Google’s tracing works everywhere because every service uses the same RPC layer, which gives one place to instrument.', 'green')])
        + p('Google has a name for what you give up: <b>retargetability</b>, the ability to reuse a part of the system for a different purpose. The trade is engineering efficiency against retargetability.')
        + p('One warning on performance. Couple for speed only after other options are exhausted. Tight coupling can block later optimisation, because speeding up one module may break a timing assumption in another.')
        + h2('When coupling costs')
        + tiles([('Reuse', 'Coupled parts can’t be used alone. And reuse itself creates coupling: when the tiny left-pad package was unpublished in 2016, thousands of builds broke.', 'red'),
                 ('Extensibility', 'A change in one place has side effects elsewhere, and isolated tests are hard to write.', 'red'),
                 ('Robustness', 'Hyrum’s law: with enough users, every observable behaviour is depended on by someone. Failures cascade.', 'red'),
                 ('Freedom of choice', 'Lock-in. Teams can’t adopt something better without engineering work, and can’t self-serve.', 'red')])
        + h2('Finding the balance')
        + pic(640, 340, _cpl, 'After Figure 1-1, redrawn. A coupling decision picks a shape in this space. You can stretch towards one corner only by pulling back from another.', 'Three axes: efficiency, performance and retargetability. A tightly coupled design reaches far on efficiency and performance and little on retargetability; a loosely coupled design does the reverse.')
        + p('No platform can be the best on every axis. A tool that does one job will eventually beat the platform at that job, and users will want to leave for it. Leaving needs loose coupling. Meeting expectations across several axes needs tight coupling. The chapter’s answer is to look for the design that gets the most benefit from the least coupling, which is Pareto efficiency: a point where you can’t improve one dimension without giving up another.')
        + p('How do you choose the point? Ask what your users value most. If they need raw performance, couple. If they need to extend and customise, don’t.')
        + note('Google’s own trade', 'Source control, code review, build and deployment are tightly coupled at Google. That lets them mark one change as bad so it can never ship, even by accident. When Log4Shell appeared, a central profiler wired into the build and scheduling systems showed quickly that exposure was small. The price was that every team had to use the same tools, whatever they were missing.')
        + deeper('types, patterns, antipatterns and how to find hidden coupling')
        + h2('Five kinds of coupling')
        + p('The chapter borrows Kruchten’s “4+1” architectural views and asks, for each one, how two components can be tied together.')
        + table(['View', 'Coupled when…', 'How restrictive'],
                [['Logical', 'Code in one calls functions or classes in the other', 'Most'], ['Development', 'One package needs the other to be deployed with it, like a shared library', 'High'],
                 ['Process', 'They talk at runtime through RPCs or messages', 'Lower: each can be updated on its own'], ['Physical', 'They must share a machine, rack or data centre to work', 'Deceptive: hidden assumptions about latency and failure domains'],
                 ['Scenario', 'Nothing technical links them, and a real-world event does', 'Invisible until it happens']])
        + p('The scenario examples are memorable. A shark bit one of Google’s undersea cables. When many people left Twitter in 2022, they overwhelmed Mastodon’s servers. Neither pair of systems shared a line of code.')
        + h2('Patterns that loosen coupling')
        + table(['Pattern', 'How it decouples', 'On AWS'],
                [['Layers', 'Each layer knows only the one beneath it', 'VPC, then EKS, then your services'],
                 ['Pipe and filter', 'Independent steps joined by a channel. Extend by adding a step', 'Kinesis or MSK with Lambda or Flink stages; Step Functions for batch'],
                 ['Publish and subscribe', 'Publishers don’t know who is listening', 'SNS, EventBridge, MSK'],
                 ['Federation', 'Interchangeable parts behind a strict contract. Each owns its data and behaviour', 'IAM Identity Center with an external identity provider; a deletion workflow that asks each service to clean up its own resources'],
                 ['Fail open', 'When a dependency fails, degrade, use a default or fall back', 'Cached responses, AppConfig defaults, circuit breakers']])
        + p('Fail open deserves care. It removes runtime coupling, since the caller survives, while logical coupling remains, since the call is still in the code. The opposite, fail closed, is correct when the dependency is a security or correctness check.')
        + h2('Antipatterns that tighten it by accident')
        + tiles([('Shared database', 'Several services read and write the same tables. The schema becomes the interface, so every schema change needs a coordinated release. Fix: a store per service behind an API, and let the platform provide backup and replication.', 'red'),
                 ('Distributed monolith', 'Services look separate and aren’t. Signs: releases must be orchestrated in order, they must sit in the same rack, or one failing takes all down. The costs of microservices with the constraints of a monolith.', 'red'),
                 ('Megamorphic artifact', 'A config file or object that grew into a junk drawer. Nobody knows who reads which part, so every edit is risky.', 'red'),
                 ('Control coupling', 'A flag lets the caller steer the callee’s internal behaviour. The caller now knows how the callee works. Fix: split into separate operations.', 'red')])
        + p('Data warehouses and lakes are not the shared-database antipattern. Their consumers expect schemas to change and use registries and ETL tools to cope.')
        + note('The megamorphic file at Compute Engine', 'One large configuration file started as infrastructure as code. Because it was easy to extend, it collected per-customer preferences and behaviour flags. Almost every service read a piece of it and none needed all of it. Small edits began causing rollbacks and minor incidents. The team split it into smaller, cohesive files, audited every consumer, and removed access nobody needed. Dependencies became visible and the blast radius of a bad edit shrank.')
        + h3('The odd one: workflow engines')
        + p('A workflow engine runs a process as a state machine and retries each step until the whole thing finishes. That decouples steps nicely, provided every step is idempotent and has no side effects beyond its output. Data pipelines usually qualify. Elsewhere, three problems appear.')
        + ul(['<b>Stuck flows.</b> A step that can never succeed is retried forever. Someone must detect it and decide whether to roll back or leave things half done.',
              '<b>Orphaned state.</b> Early steps wrote data that the failed workflow never used. You need compensating actions (the saga pattern) or a janitor job, and both are coupled to the business logic of the steps.',
              '<b>Version skew.</b> A step is redeployed while workflows are in flight, and later steps depended on its old behaviour.'])
        + h2('Finding coupling nobody intended')
        + table(['Method', 'Finds', 'Cost', 'On AWS'],
                [['Static analysis', 'Logical coupling: imports, shared data structures, global state', 'Low', 'Dependency graphs in CI; Amazon Q Developer or Inspector code scans'],
                 ['Tracing', 'Runtime calls, including through queues if messages carry trace context', 'Low once instrumented', 'X-Ray, Application Signals service map, OpenTelemetry'],
                 ['Log correlation', 'Two services touching the same state or the same request', 'Medium', 'CloudWatch Logs Insights joined on request IDs; CloudTrail data events'],
                 ['Chaos engineering', 'Physical and scenario coupling. Turn off a whole failure domain and see what else breaks', 'Highest', 'Fault Injection Service, ARC zonal shift']])
        + p('When you find an accidental dependency, weigh it like a deliberate one. Does it buy efficiency, performance, atomicity or traceability? If not, migrate to one of the loose patterns.')),
    say='I don’t treat coupling as good or bad. I ask what it buys and what it costs. It buys efficiency, performance, atomicity and traceability, and it costs reuse, extensibility, robustness and freedom of choice. So I decide which of those my users care about, couple deliberately for that, and then go looking for the coupling nobody chose, with dependency analysis, tracing and fault injection.',
    aws='The loose patterns map directly: SNS and EventBridge for publish-subscribe, Kinesis and Step Functions for pipelines, API Gateway and versioned APIs between services, IAM Identity Center for federation. For the shared-database antipattern, give each service its own DynamoDB table or Aurora cluster behind an API and let AWS Backup carry the common concerns. To discover hidden coupling, use the X-Ray or Application Signals service map for runtime calls, CloudTrail to see who touches which table or bucket, and Fault Injection Service to remove an Availability Zone and watch what fails.',
    iq=[('Your team has thirty microservices and every release needs a spreadsheet to coordinate the deploy order. What is wrong, and what do you do?',
         ['That is a distributed monolith. The services are separate in the code and coupled somewhere else, and the release spreadsheet is the evidence. I’d say so plainly, because the team is paying the operational cost of microservices and getting none of the independence.',
          'First I’d find where the coupling lives. Shared database tables are the usual cause: I’d check which services read or write the same tables, using CloudTrail or database audit logs. Then implicit contracts: message formats on queues, and shared configuration that many services read. Tracing gives the runtime call graph, and the deploy history shows which services always ship together.',
          'Then I’d fix the worst edge first, not everything. For a shared table, one service becomes the owner and exposes an API; the others migrate to it one at a time. For message formats, a schema registry with compatibility checks in CI. For a junk-drawer config file, split it by consumer.',
          'I’d also ask whether some of those services should be merged. If two services always change together, they are one module with a network call in the middle, and merging them is a legitimate answer.',
          'The measure of success is simple: the percentage of releases that ship one service alone, with no coordination.'])],
    quiz=[['A producer writes events to a queue and has no knowledge of the consumer. The producer renames a field and the consumer breaks. What kind of coupling is this?', ['Explicit and tight', 'Implicit', 'Physical', 'None, because they never call each other'], 1, 'There is no direct interaction, yet one side assumes how the other behaves. That is implicit coupling, and it is why message schemas need contracts.'],
          ['Which method is best at finding physical and scenario coupling?', ['Static analysis', 'Tracing', 'Log correlation', 'Chaos engineering'], 3, 'Only removing a real failure domain shows which components silently assumed it would be there. It is also the most expensive method.']],
    turn='Run <b>POC 12</b>. It builds a dependency graph from sample traces, table-access logs and deploy history, then reports shared databases, services that always deploy together, and config keys read by too many services. Add a service that reads another team’s table and watch the report change.',
    take=['Coupling should be a decision. The dangerous kind is the kind nobody chose.', 'It buys efficiency, performance, atomicity and traceability, and costs reuse, extensibility, robustness and choice.', 'Shared databases, distributed monoliths, junk-drawer configs and behaviour flags are how it sneaks in.']))

# ══════════════════════════════════════════════════════════════ 2 Layers
_rows = [('Prototypes and experiments', 'days to weeks', 380), ('Products', 'months', 300), ('Infrastructure', 'quarters or longer', 230),
         ('Technical directives', 'quarters to years', 170), ('Business culture', 'years', 110), ('Regulatory and legal', 'slow, with sudden shocks', 56)]
_pace = ''.join(
    f'<rect class="pn" x="10" y="{14 + i * 50}" width="700" height="44" rx="8"/>'
    f'<text x="24" y="{33 + i * 50}" class="b">{n}</text><text x="24" y="{51 + i * 50}" class="m" style="font-size:13px">{t}</text>'
    f'<line class="hl" x1="300" y1="{36 + i * 50}" x2="{300 + w}" y2="{36 + i * 50}" marker-end="url(#ah)"/>'
    for i, (n, t, w) in enumerate(_rows)) + '<text x="700" y="330" text-anchor="end" class="m">arrow length = how fast the layer changes</text>'
L.append(dict(
    id='pe-2', dot='2', part='P1', nav='Layers', h1='Layers: parts of a platform change at different speeds',
    final=10, by='Kaan Kivilcim', poc='',
    learn=['What the OSI model, shearing layers and pace layers each teach about platforms', 'The six-layer framework for platform engineering, from fastest to slowest', 'How the layers push on each other, told through one internal tool'],
    body=(
        h2('The big picture')
        + p('Abstractions give you reusable components. Coupling describes how they connect. Layers add time: which parts of a platform change quickly, which change slowly, and how they influence each other.')
        + p('That matters because a platform team is always balancing two speeds. Product teams want to ship this week. Governance, security and compliance move on a scale of quarters and years. A layered view tells you which speed belongs where, so the fast parts can move without shaking the slow ones.')
        + h2('Three earlier ideas about layers')
        + table(['Model', 'From', 'What it gives platform engineers'],
                [['OSI model', 'Zimmermann, 1980', 'Three benefits of strict layering: each layer adds value to those below, the problem is divided into manageable pieces, and a layer can change inside as long as it offers the same service upward. It is prescriptive, and real systems bend it.'],
                 ['Shearing layers', 'Frank Duffy; Stewart Brand, 1994', 'A building is six layers that age at different rates: site, structure, skin, services, space plan, stuff. The site is forever and the furniture moves weekly. It is descriptive, which suits platforms, since they mirror their organisation and resist forced standards.'],
                 ['Pace layers', 'Stewart Brand, 1999', 'Civilisation as six layers by speed: fashion, commerce, infrastructure, governance, culture, nature. Health comes from the tension between them.']])
        + p('Brand’s summary of how fast and slow layers relate is the line to remember. The fast layers learn and propose. The slow layers remember and decide. Shocks are absorbed by the fast layers at the top, and stability comes from each layer respecting the pace of its neighbours.')
        + h2('Six layers of platform engineering')
        + pic(720, 340, _pace, 'After Figure 2-4, redrawn as bands. The top layer turns over in days. The bottom one barely moves, until a court ruling or a new law moves it all at once.', 'Six stacked layers from prototypes and experiments at the top to regulatory and legal at the bottom, with shorter arrows for slower layers.')
        + table(['Layer', 'What lives here', 'Pace'],
                [['1 · Prototypes and experiments', 'Building to learn. Most of it is thrown away, and the lessons decide what moves down. Rust experiments at Google eventually shaped company-wide directives.', 'Days to weeks'],
                 ['2 · Products', 'The marketplace. Proven ideas become features with requirements and stability. Product teams think about what, not how.', 'Months'],
                 ['3 · Infrastructure', 'The paved road: runtimes, server frameworks, networking, CI/CD. Convergence here saves each team tens or hundreds of person-years, and every improvement reaches everyone.', 'Quarters or longer'],
                 ['4 · Technical directives', 'The law of the engineering organisation: binding cross-company decisions, such as safety expectations for AI agents or converging on a set of server frameworks.', 'Quarters to years'],
                 ['5 · Business culture', 'Why the company does what it does. Durable system health over short-term gain; protecting users by default.', 'Years'],
                 ['6 · Regulatory and legal', 'The outside world. Everything above must eventually comply. A change here cascades upward through culture, directives and infrastructure.', 'Slow, then sudden']])
        + h2('One tool, six layers')
        + p('The chapter follows an internal screenshot tool called SnipIt through every layer. It is a good story to retell because it shows the layers pushing on each other in both directions.')
        + seq([('Prototype', 'Started in 2009 as a 20% project. Nobody would have funded a screenshot tool if asked.'),
               ('Product', 'For more than 15 years a tiny team, often one person part-time, kept it running. By 2024 it was the third most used internal application at Google.'),
               ('Infrastructure', 'It reached 8 billion screenshots with no major rework, because it ran on App Engine. The leverage was so complete it was invisible.'),
               ('Directive', 'Security standards moved on, and the tool needed finer-grained access controls. The first decision was to shut it down.'),
               ('Culture', 'Employees pushed back hard: testimonials, petitions, memes. Shutting down something this useful was called “ungoogley”.'),
               ('Legal', 'The obligation to protect internal data could not be argued with. So the only remaining answer was to invest and bring the tool up to standard.')])
        + p('Read it as two forces. A fast layer proposed something and it worked. A slow layer said no. A slower layer overruled that no, and the slowest layer set the terms of the yes.')
        + deeper('how to use the model')
        + h2('Using the layers in practice')
        + ul(['<b>Place every decision on a layer before arguing about it.</b> A choice of library is layer 1 or 2 and should be cheap to reverse. A choice of deployment framework is layer 3. A mandate is layer 4 and needs an owner and a reason.',
              '<b>Let ideas move down only when proven.</b> The top layers are where you learn cheaply. Promote what works; don’t standardise an experiment.',
              '<b>Don’t make slow layers move at the speed of fast ones.</b> Rewriting your deployment platform every quarter to follow a trend is how platforms lose trust.',
              '<b>Expect shocks from the bottom.</b> When regulation changes, plan the cascade: what the policy becomes, which directive it turns into, which platform component enforces it.'])
        + p('The AI chapter later uses the same picture: AI applications are the fast layer, and the platform is the slow layer that absorbs shocks and gradually takes on whatever has proven itself.')
        + note('Connection to the SRE track', 'Chapter 3 of the SRE book describes compliance being written as policy-as-code and checked before deployment. In this model that is a layer 6 requirement, turned into a layer 4 directive, implemented at layer 3.')),
    say='I think about a platform as layers that change at different speeds. Experiments and products at the top change in days or months. Infrastructure, technical directives, culture and regulation below them change over quarters and years. The fast layers are where we learn; the slow layers are where we keep what we learned. Most platform arguments get easier once you agree which layer a decision belongs to.',
    aws='A workable mapping: sandbox accounts for experiments (layer 1), product accounts and services (layer 2), the shared platform of landing zone, EKS or ECS base, pipelines and golden-path templates (layer 3), Service Control Policies, Config conformance packs and tagging standards as technical directives (layer 4), and compliance frameworks tracked in Audit Manager and Security Hub standards at the bottom (layer 6). Use AWS Organizations to give the layers different rates of change: sandbox OUs with loose guardrails, production OUs with strict ones.',
    iq=[('A team wants to use a new language that the platform doesn’t support. How do you decide?',
         ['I’d start by asking which layer the request sits on. Trying a language in a prototype is a top-layer activity. It should be cheap and allowed, in a sandbox, without platform guarantees, and the team should know they own everything the platform would normally give them.',
          'Putting it into a product that pages someone is a different request. Now it touches the infrastructure layer: build, dependency management, security scanning, observability and deployment all need to work for that language. That is a real cost, paid by the platform team for years.',
          'So I’d set a path. Experiment freely. If the experiment shows a clear advantage for a class of workloads, write that up, and decide at the directive level whether to add the language to the paved road. Google’s Rust adoption followed that route: exploration first, then a company-wide direction, then investment in tooling.',
          'What I’d avoid is the middle state, where a production service runs on a stack nobody supports. That gives the team the freedom of a low-integration ecosystem while they still expect the guarantees of a high-integration one.'])],
    quiz=[['In the pace-layer view, what is the job of the slow layers?', ['To block change', 'To remember and decide, giving stability to what the fast layers propose', 'To experiment', 'To follow the fast layers as quickly as possible'], 1, 'Fast layers learn and propose; slow layers remember and decide. Stability comes from each respecting the other’s pace.']],
    turn='Take three decisions your team made this year (a library, a pipeline change, a policy) and place each on one of the six layers. For each, write how long it should take to reverse. If a top-layer decision would take a quarter to undo, you have found accidental coupling.',
    take=['Layers describe rates of change. Match each decision to the layer it belongs on.', 'Fast layers learn and propose; slow layers remember and decide.', 'Changes at the bottom cascade upward, so plan how a new rule becomes a directive and then a platform feature.']))

# ══════════════════════════════════════════════════════════════ 3 Shared fate
_sf = ''.join(
    f'<rect class="pn" x="{x}" y="60" width="150" height="190" rx="6"/>'
    f'<rect class="fc" x="{x}" y="{250 - h}" width="150" height="{h}" rx="6" style="opacity:.75"/>'
    f'<text x="{x + 75}" y="36" text-anchor="middle" class="b">{a}</text><text x="{x + 75}" y="54" text-anchor="middle" class="m" style="font-size:13px">{b}</text>'
    f'<text x="{x + 75}" y="{250 - h + 22 if h > 40 else 240}" text-anchor="middle" class="b" style="fill:var(--bg)">{"platform" if h > 40 else ""}</text>'
    f'<text x="{x + 75}" y="{(60 + 250 - h) / 2 + 5}" text-anchor="middle" class="m">{"developer" if h < 150 else ""}</text>'
    for x, h, a, b in [(60, 38, 'Type 2 · Guided', 'the frontier'), (285, 95, 'Type 3 · Engineered', 'typical cloud setup'), (510, 160, 'Type 4 · Assured', 'the walled garden')]) + (
    '<line class="ln" x1="60" y1="282" x2="660" y2="282" marker-end="url(#ah)" marker-start="url(#ah)"/>'
    '<text x="60" y="304" class="m">more architectural choice</text><text x="660" y="304" text-anchor="end" class="m">more liability carried by the platform</text>')
L.append(dict(
    id='pe-3', dot='3', part='P1', nav='Shared fate', h1='Shared fate and shared responsibility',
    final=12, by='Andy Qin', poc='POC 14',
    learn=['What shared fate means and why it needs shared responsibility', 'The economic trade: architectural choice for platform liability', 'Resources, rights and responsibilities: the three Rs of the social contract', 'Why guardrails matter even more when AI agents write the code'],
    body=(
        h2('The big picture')
        + p('In a mature engineering ecosystem, components are connected on purpose. One team’s library update, security patch or shortcut reaches everyone who builds on it. The book calls this <b>shared fate</b>. It is what makes fleet-wide improvements possible, and it is also what makes fleet-wide failures possible.')
        + p('Shared fate without <b>shared responsibility</b> ends in a tragedy of the commons. Each team does what is locally sensible, such as adding a risky dependency or ignoring a deprecation notice, and the common ground everyone depends on gets worse.')
        + h2('The economics: choice for liability')
        + p('The whole chapter rests on one equation. <b>The more an ecosystem limits a developer’s architectural choices, the more liability it can take on for that developer.</b>')
        + pic(720, 316, _sf, 'My drawing of the chapter’s spectrum. The filled part is how much of safety, reliability, efficiency and compliance the platform carries. The types come from a chapter that is not published yet; the names match the 0-to-4 scale in the SRE book.', 'Three bars for ecosystem types 2, 3 and 4. The share of responsibility carried by the platform grows from small to most of the bar, while architectural choice shrinks.')
        + table(['', 'Type 4 · highly integrated', 'Type 2 or 3 · loosely integrated'],
                [['You get', 'Leverage. The platform owns security, reliability, efficiency and compliance', 'Flexibility and a fast start. Any language, library or toolchain'],
                 ['You pay', 'Conformity. Standard build system, languages and tools. The head of every library must always build and pass tests', 'The operational load comes back to you. You are your own security engineer and compliance officer'],
                 ['Good for', 'Most production software at scale', 'Acquisitions, special projects, early experiments']])
        + p('Two of Google’s numbers show the dividend. A central improvement to the C++ memory allocator reached every team at once and saved a significant share of fleet CPU, with no team changing a line. And safe-by-design query APIs produced zero SQL injection in more than a decade in one ecosystem. Neither result came from training thousands of engineers.')
        + h3('One example across the types: third-party packages')
        + table(['Ecosystem', 'What the platform does', 'What is left to you'],
                [['Type 2', 'Stores packages in a registry', 'Reviewing updates, licences, freshness, patching. Everything'],
                 ['Type 3', 'Handles ingestion and gives you scan data', 'Choosing versions and deciding how to mitigate each vulnerability'],
                 ['Type 4', 'Ingests, scans for malware, enforces freshness and licences, blocks bad packages', 'Almost nothing, and almost no choice']])
        + p('The chapter separates a <b>resource</b> from a <b>guardrail</b> with this example. A registry is a resource: it helps, and the easiest thing to do with it is ignore updates. A managed dependency system is a guardrail: the safe package is the only one you can get.')
        + h2('Governance: from policing to stewardship')
        + p('Central enforcement works in a uniform ecosystem, where it can be automated until developers no longer notice it. It does not work across mixed environments, where a central team can’t enforce what it can’t see.')
        + p('There the platform’s job changes to stewardship. It provides tools, data and guidance, including coverage metrics that let each team lead see how well they meet their own obligations. Accountability for accepting risk sits with the local team. The shift is from enforcement to enablement, and it keeps the central team from becoming a bottleneck.')
        + h2('Guardrails: the path of least resistance')
        + p('You can’t run a large system on willpower. The safest action has to be the easiest one.')
        + flow([('Type 2', 'Find defects after the commit: static analysis, fuzzing. The developer must triage and fix', 'orange'), ('Type 4', 'Assurance by design: safe-by-default frameworks, and raw risky APIs locked away from everyone except reviewed code', 'green')],
               'The chapter calls this the hierarchy of assurance. Enforcement is mechanical, through build visibility rules, and never by convention alone.')
        + p('A useful phrase from the chapter: <b>friction is a directive</b>. People do what is easy. Remove friction from safe behaviour and add it to risky behaviour, and the system steers itself.')
        + p('Uniformity also pays in maintenance. With one compiler and build chain, the platform team can make a <b>large-scale change</b> across thousands of projects quickly, for example to respond to a new security threat. In a mixed environment every team patches by hand.')
        + deeper('the social contract, its edges, and AI agents')
        + h2('The three Rs')
        + tiles([('Resources', 'What the ecosystem gives the developer: compute, storage, safe APIs, managed dependencies.'),
                 ('Rights', 'What the developer is allowed. In a loose ecosystem, unlimited choice. In an integrated one, that right is given up in exchange for the right to assured safety.'),
                 ('Responsibilities', 'What the developer puts in to keep the ecosystem healthy.')])
        + p('The contract is most often broken in one specific way: a team wants the rights of a loose ecosystem and the resources of an integrated one. Free choice of stack, and automatic security. Those two can’t be had together, and saying so explicitly is most of the work.')
        + table(['', 'Walled garden (type 4)', 'Frontier (types 2 and 3)'],
                [['The deal', 'Conformity for leverage', 'Autonomy for accountability'],
                 ['Platform’s obligation', 'Full support for security, reliability and compliance', 'Resources, tools and visibility. No assurances'],
                 ['Team’s obligation', 'Sustainability: don’t add debt that blocks the automated machinery', 'Be the primary guardian. You are the security team'],
                 ['The image', 'A passenger on a high-speed train. You don’t drive, and you don’t pull the emergency brake', 'A settler. Nobody is coming to save you'],
                 ['Typical failure', 'A team quietly diverges and blocks a fleet-wide change', 'A team imports a malicious library, assuming central security would catch it']])
        + h3('Where the contract strains')
        + p('The friction shows at the edges. An acquired company arrives with a very different ecosystem. A team spinning out a special project tries to take the big machinery with it and finds it can’t run it alone. The chapter asks for <b>permeability</b>: moving between ecosystems is a renegotiation of the contract, and it goes better when framed as a trade the team is making, not a mandate imposed on them.')
        + h2('Why this matters more with AI agents')
        + p('An agent writes code faster than people can review it. In a loose ecosystem, where safety depends on human vigilance and manual glue, that speed multiplies mistakes. In a tightly integrated one, the platform’s constraints act as a containment field: an agent can’t commit code that breaks a safety rule, because that code doesn’t build.')
        + p('Agents also do better when there is less to get right. If the platform handles build flags, dependencies and safety properties, the agent only has to express the business intent. The human’s role moves to being a <b>guardian of intent</b>: define the goal and the success criteria precisely, trust the fast generation, and verify deliberately.')
        + note('Not everything belongs in the walled garden', 'The chapter ends on a menu of deliberate trade-offs. Start experiments where friction is low. Let acquisitions integrate gradually. What matters is that each team knows which contract it has signed.')
        + h3('Learning loops')
        + p('Incidents, audit findings and red-team results are raw material for shared learning. To use them you need two kinds of metrics: team-level delivery metrics in the DORA style, and ecosystem-level ones such as toolchain effectiveness and governance coverage.')),
    say='Shared fate means one team’s choices land on everyone, so it has to come with shared responsibility. I frame it as a trade: the more a platform limits your choices, the more liability it can carry for you. I make that explicit with three Rs: what resources the platform gives, what rights the team has, and what responsibilities they keep. The failure I watch for is a team wanting free choice of stack and automatic guarantees at the same time.',
    aws='AWS publishes its own shared responsibility model, and your internal platform needs one too. A type 2 account gets raw services and a registry (ECR, CodeArtifact) and owns everything else. A type 3 landing zone adds Control Tower guardrails, Config rules, Inspector scan results and Security Hub scores that teams must act on. A type 4 golden path makes the safe choice the only one: Service Control Policies block the risky APIs, CodeArtifact serves only vetted packages, pipelines are the sole route to production, and Lambda code signing or an EKS admission policy refuses unsigned artifacts. Publish a coverage dashboard so every team lead can see their own posture.',
    iq=[('A team asks for an exemption from the standard pipeline because it slows them down. How do you respond?',
         ['I’d treat it as a conversation about which contract they want, not as a yes or no.',
          'First I’d find out what is slow, because that may be a platform bug. If the pipeline takes forty minutes or blocks on a flaky check, that is our problem to fix, and their complaint is useful. Friction on the safe path pushes people off it.',
          'If they need something the path really can’t do, I’d lay out the trade. On the standard path, the platform carries security scanning, signed artifacts, canary analysis, rollback and compliance evidence. Off it, they carry all of that, and they’re no longer eligible for fleet-wide fixes. I’d put that in writing: the resources they give up and the responsibilities they take on.',
          'Then I’d make the exemption safe and visible: time-limited, with an owner, tracked as debt, and contained so a mistake can’t spread, for example in its own account with its own blast radius.',
          'Finally I’d treat the request as product feedback. One exemption is a special case. Five for the same reason is a gap in the platform.'])],
    quiz=[['What is the core economic equation of shared fate?', ['More services mean more cost', 'The more an ecosystem limits architectural choice, the more liability it can take on for the developer', 'Central teams should own all risk', 'Flexibility and assurance grow together'], 1, 'Conformity is the price of leverage. A platform can only guarantee what it controls.'],
          ['A package registry that stores dependencies and leaves updates to each team is best described as…', ['A guardrail', 'A resource', 'An assurance', 'A directive'], 1, 'A resource helps and enforces nothing. A guardrail makes the safe choice the only available one.']],
    turn='Write a one-page contract for your own platform using the three Rs. For each of security patching, dependency updates, backups and deployment safety, say what the platform provides, what teams may choose, and what teams must do. The repo has a template in <code>docs/platform/shared-fate-contract.md</code>.',
    take=['Limit choice and the platform can carry liability. That is the trade.', 'Make it explicit with resources, rights and responsibilities.', 'Guardrails must make the safe path the easy one, and that matters most when agents write the code.']))
