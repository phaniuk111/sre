# Third pass: diagrams redrawn from the book's figures (in my own layout), plus what the
# full re-read of chapters 1-3 and 9 added. PICS[n] goes before "Going deeper"; MORE[n] after it.
from extras import flow, tiles, table, seq

ARROW = ('<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
         '<path d="M0 0L10 5L0 10z" fill="context-stroke"/></marker></defs>')


_n = [0]


def pic(w, h, inner, cap, label):
    _n[0] += 1
    k = f'ah{_n[0]}'  # one marker per figure: a shared id would resolve to a hidden lesson's copy and not paint
    return (f'<figure class="pic"><svg viewBox="0 0 {w} {h}" role="img" aria-label="{label}">{ARROW.replace('id="ah"', f'id="{k}"')}{inner.replace("url(#ah)", f"url(#{k})")}</svg>'
            f'<figcaption>{cap}</figcaption></figure>')


def sec(title, *parts):
    return f'<h2>{title}</h2>' + ''.join(parts)


def p(t):
    return f'<p>{t}</p>'


def ul(items):
    return '<ul>' + ''.join(f'<li>{i}</li>' for i in items) + '</ul>'


PICS, MORE = {}, {}

# ───────────────────────── Chapter 1
PICS[1] = sec(
    'Why the old pyramid was replaced',
    p('The first edition used a pyramid drawn by Mikey Dickerson in 2013, modelled on Maslow. Interviewers who read that edition may still have it in mind, so know both and know what changed.'),
    table(['', 'Dickerson’s hierarchy (2013)', 'Hierarchy of production health (2nd edition)'],
          [['Base', 'Monitoring', 'Sociotechnical foundations: culture and people'],
           ['Then', 'Incident response, postmortems', 'Situational awareness: SLOs, observability, toil tracking, goals'],
           ['Then', 'Testing and release, capacity planning', 'Continuous preparedness: incidents, learning, training'],
           ['Then', 'Development', 'Infrastructure design: delivery, testing, data, capacity'],
           ['Top', 'Product', 'Resilient products, then emergent reliability']]),
    p('The book gives four reasons for the redesign. The lower layers were all reactive. Capacity planning had a layer of its own while data integrity was hidden inside “development”. Culture was assumed, not named. And nothing described the end state, where a platform makes services reliable by default.'),
    '<div class="note"><b>The inverted pyramid</b>You don’t have to finish one layer before starting the next. Grow the pyramid wider and taller at the same time. What you must avoid is a wide top on a narrow base: clever self-healing platforms run by a team with no blameless culture and no SLOs.</div>')

MORE[1] = sec(
    'Details from the full chapter',
    '<h3>SRE is a role, not only a skill set</h3>',
    p('Any team can borrow SRE methods, and DevOps shows that works. The book still argues for a dedicated role, for three reasons.'),
    ul(['<b>It’s hard to do part-time.</b> Feature deadlines always win the week.',
        '<b>It needs depth and breadth.</b> An SRE sees across service boundaries, where most large outages live.',
        '<b>Reliability needs its own voice.</b> It is a long-term investment, and the next launch will override it unless someone is accountable for it.']),
    p('The stance matters as much as the role: SREs are enablers, not gatekeepers.'),
    '<h3>Three advantages of the software mindset</h3>',
    tiles([('Objective understanding', 'Health is measured through SLOs and observability, and processes are derived from first principles: postmortems, STPA, CAST.'),
           ('Automation', 'Efficiency and consistency together. It also gives you a reason to simplify, because simple systems are easier to automate.'),
           ('Dev and ops integrated', 'One shared language and a feedback loop from production back into design.')]),
    p('That is why every SRE is expected to write code, even if on a given day the code is only a monitoring configuration.'),
    '<h3>Three ways to shrink an incident</h3>',
    flow([('Length', 'Detect fast, mitigate fast'), ('Frequency', 'Follow through on postmortem actions'), ('Scope', 'Failure domains and graceful degradation')],
         'Preparedness cuts impact along these three dimensions. On-call is a means to that, not the purpose of the team.'),
    '<h3>What each upper layer contains</h3>',
    table(['Layer', 'What the chapter puts in it'],
          [['Situational awareness', 'SLOs and observability, plus two things people forget: toil tracking (no exact number exists, so use outages, ticket throughput and a rough maintenance estimate) and business alignment through OKRs and feature velocity. Without the last one SRE gets sidelined.'],
           ['Infrastructure design', 'Six areas: release management (changes are the top cause of outages, so use incremental rollouts, trunk-based development and many small releases), configuration management (GitOps, feature flags), data, capacity (load balancing, throttling, DoS protection), production testing (probers, fault injection, load tests) and observability.'],
           ['Resilient products', 'Shrink the blast radius with failure domains, horizontal scaling with failover, and graceful degradation (a page that loads without profile pictures still works). Then simplify, above all by removing circular and unnecessary dependencies.'],
           ['Emergent reliability', 'The platform makes whole classes of failure impossible. Where it can’t enforce, it monitors, for example by spotting a global push in the logs. Teams rarely break rules on purpose, so teach as well as block.']]),
    p('AI is missing from the pyramid on purpose. The authors treat it as something that cuts across every layer, which is why it gets its own part at the end of the book.'))

# ───────────────────────── Chapter 2
PICS[2] = sec(
    'One hour of downtime, counted properly',
    p('The chapter’s most quotable table argues that a major outage costs 100 to 1,000 times its length in engineering time. Roughly, for one hour of serious downtime:'),
    table(['Where the hours go', 'Engineer-hours'],
          [['Operations team managing the outage', '5–10'], ['Post-incident review, timeline and bug tracking', '10–20'], ['Internal communication and presentations', '20–50'],
           ['Remediation: working through the repair items', 'about 100'], ['Customer communication', 'about 100']], cls='num'),
    p('On top of that, rollouts slow down for weeks afterwards because everyone is cautious. The same chapter has a simple worked example for an internal system: a finance outage that idles 400 people for two days at $325 a day is $260,000 before anyone counts the knock-on effects.'),
    '<div class="note"><b>A number worth remembering</b>Google’s research found that 53% of visitors give up on a task when a page takes more than three seconds to load. Slow counts as down.</div>')

MORE[2] = sec(
    'Details from the full chapter',
    '<h3>The startup that deferred everything</h3>',
    p('A sidebar describes a SaaS company growing revenue 200% a year while putting off basic production hygiene. The bill arrived as twelve months of all-hands catch-up work. Uptime went from 99.84% to 99.999%, which is the difference between about an hour of downtime a month and a few seconds. The operations lead joked that the recovery plan had so many phases it ran out of letters.'),
    p('The lesson for an interview: reliability debt compounds, and paying it later costs a year of feature work.'),
    '<h3>What to adopt, by stage</h3>',
    tiles([('Early stage: the cheap five', 'Automated tests, CI/CD (changes are the largest outage trigger at Google), basic observability, a simple incident process, and design reviews.', 'green'),
           ('Mature organisation', 'SLOs as a tool for strategic decisions, managing accumulated complexity, formal incident response with defined roles, and centrally maintained tools.', 'blue')]),
    '<h3>Six questions before you adopt SRE</h3>',
    '<ol><li>What are your biggest operational challenges?</li><li>What resources do you have? That includes skills, and whether the culture will fall back to quick fixes.</li><li>Can you start small?</li><li>What is at stake if you’re unreliable?</li><li>How do users interact with you? If they retry, short outages hurt less than long ones. A flash sale may still sell out during a blip and damage your reputation anyway.</li><li>Is timing a factor, such as a peak season?</li></ol>',
    '<h3>Smaller points that come up</h3>',
    ul(['Not every Google system has SRE support. The mission-critical ones do, and SRE can hand a pager back.',
        'Traditional operations is rewarded for stability, so it resists change. SRE shares an error budget with developers, so both sides own the trade.',
        'The CFO’s argument: machines are fast and cheap, people are slower and far more valuable. One global load-balancing platform serves Search, Maps and YouTube.',
        'Reliability is a company-wide habit. Sales and marketing should warn engineering before a campaign. Google Meet’s growth during COVID is the example of business growth arriving without warning.']))

# ───────────────────────── Chapter 3
PICS[3] = sec(
    'How platforms evolved',
    flow([('About 2010 · Tickets', 'A service desk, days or weeks of waiting, and a “wall of confusion” between dev and ops'),
          ('2016–2026 · Self-service', 'Internal developer platforms and golden paths. A “vending machine”: pick a template and get an instance with monitoring, security logging and backups already on'),
          ('Next · Intent-based', 'You declare a latency target or a budget. The platform picks tiers, isolates, migrates and throttles to meet it')],
         'Governance moved with it: from auditing what humans did, to guardrails built into the system.'),
    p('The book names three things an intent-based platform has to get good at: filtering signals adaptively, carrying regulatory logic inside the platform, and treating energy and sustainability as constraints alongside cost.'),
    '<h3>Google’s production stack, with AWS equivalents</h3>',
    p('The chapter walks through Google’s environment. You won’t be asked to recite it, but being able to translate it shows you understand what each piece is <i>for</i>.'),
    table(['Google', 'What it does', 'Closest on AWS'],
          [['Borg', 'Cluster operating system: runs jobs made of tasks', 'EKS or ECS'],
           ['Colossus', 'Cluster file system under everything else', 'S3 and EBS'],
           ['Spanner', 'Globally consistent relational database', 'Aurora (global database), DynamoDB global tables'],
           ['Bigtable', 'Sorted key-value map at petabyte scale', 'DynamoDB, Keyspaces'],
           ['Blobstore', 'Large immutable objects', 'S3'],
           ['gRPC and Protocol Buffers', 'Typed RPC between services', 'gRPC on ALB or VPC Lattice'],
           ['GSLB', 'Load balancing at three levels: DNS by geography, service, and RPC', 'Route 53, Global Accelerator, ALB, VPC Lattice'],
           ['Piper', 'One repository for code and configuration', 'A monorepo with infrastructure as code (CDK, Terraform)'],
           ['Push-on-green CI', 'Tests run on production clusters; green builds ship', 'CodePipeline with automated gates'],
           ['Monarch', 'Planet-scale time-series monitoring', 'CloudWatch, Managed Service for Prometheus'],
           ['Boq', 'Internal developer platform with conformance rules and built-in overload, retry and caching hooks', 'A platform team’s golden path: Backstage, Service Catalog, shared CDK constructs'],
           ['BeyondCorp', 'Zero trust: access by identity and device, not network', 'Verified Access, IAM Identity Center']]))

MORE[3] = sec(
    'Details from the full chapter',
    '<h3>Capacity became a finance problem</h3>',
    p('On-premises, you bought for the peak and the hardware sat idle 51 weeks a year. In the cloud you rent elasticity for Black Friday. The catch is that capital expense turns into operating expense that can swing wildly if nobody watches it. That is the job FinOps does: commitments for the steady base, spot for work that can be interrupted, and tags so every team sees its own bill.'),
    '<h3>From the 2016 “fortress” to now</h3>',
    p('Ten years ago the unit was a hand-tended VM on a SAN, with configuration drift and a specialist team per layer. Three decouplings changed that. Separating storage from compute removed what the book calls the preallocation tax: you no longer pay for disks sized for a peak that may never come. Networking became software-defined and driven by identity.'),
    p('Two forces shape the next decade. One is <b>digital sovereignty</b>: a single service may need to run under ten sets of national rules. The other is <b>autonomous optimisation</b>, where control loops trade performance against energy and cost on their own. Both push SRE away from allocating resources and towards governing policy.'),
    '<h3>Observability: components to context</h3>',
    ul(['The single pane of glass is a myth. Use open standards so context flows between tools.',
        'Distributed tracing is now a basic primitive, not an advanced extra.',
        'Quality over quantity: SLOs are the primary signal, and cardinality needs discipline.',
        'Access should be open across teams. Telemetry silos are an antipattern.']),
    '<h3>Why RTO and RPO fall short</h3>',
    p('They are binary and reactive, like a stopwatch that only starts after a disaster, and their values often come from history or politics. They can’t describe a gray failure such as “30% slower for 10% of users”. An SLO can.'),
    '<h3>How Google’s own environment changed</h3>',
    ul(['<b>Platformisation.</b> The P2020 programme set standards for CI/CD and observability. Boq gave Borg applications a paved road with conformance requirements.',
        '<b>Compliance shifted left.</b> Rules such as GDPR, the DSA and the DMA are written as policy-as-code and checked before deployment.',
        '<b>AI at scale.</b> More than 3.2 quadrillion tokens a month by mid-2026, accelerator use up fifteen-fold in two years, and machine learning used to predict hardware failures and tune cooling.']),
    flow([('Data ingestion', 'and processing'), ('Training', 'and experimentation'), ('Deployment', 'and serving'), ('Observability', 'Drift, decay, retraining')],
         'The four stages of an AI pipeline. Each one needs its own reliability thinking, which chapter 20 picks up.'))

# ───────────────────────── Chapter 5
_tre = '''
<line class="ln" x1="70" y1="340" x2="610" y2="340" marker-end="url(#ah)"/><line class="ln" x1="70" y1="340" x2="70" y2="30" marker-end="url(#ah)"/>
<text x="340" y="368" text-anchor="middle" class="m">Software engineering skill</text>
<text transform="translate(28 190) rotate(-90)" text-anchor="middle" class="m">Systems engineering skill</text>
<line class="dash" x1="440" y1="40" x2="440" y2="340"/><text x="446" y="56" class="m">SWE hiring bar</text>
<line class="dash" x1="70" y1="120" x2="600" y2="120"/><text x="80" y="112" class="m">SE hiring bar</text>
<path class="hl" d="M110 120Q170 290 440 320"/>
<text x="84" y="310" class="b">No hire</text>
<text x="230" y="205" class="b">Hybrid SRE candidates</text><text x="230" y="225" class="m">strong enough in both together</text>
<text x="200" y="80" class="b">SRE-SE candidates</text>
<text x="456" y="210" class="b">SRE-SWE</text><text x="456" y="230" class="b">candidates</text>'''
PICS[5] = sec(
    'The Treynor curve',
    p('Ben Treynor Sloss drew Google’s hiring bar as a curve, not a line. A candidate who clears the software bar is a fit, and so is one who clears the systems bar. The interesting part is the middle.'),
    pic(640, 380, _tre, 'After Figure 5-1. Someone slightly under both bars can still be a hire if the two skills together land above the curve. Below it, there isn’t enough of either.', 'Chart with software skill across and systems skill up. A curve joins the two hiring bars; candidates above the curve are hybrid SRE hires.'),
    p('This is why the interview loops differ but the job doesn’t. It also explains a line you can use about yourself: “I’m stronger on the systems side, and here is the software I’ve written to automate it.”'),
    '<h3>How scope grows with seniority</h3>',
    flow([('Reactive', 'Handles what arrives'), ('Proactive', 'Prevents the next one'), ('Comprehensive', 'Owns a whole system'), ('Long-term', 'Plans across years'), ('Directional', 'Sets where the organisation goes')],
         'After Figure 5-3. The move is from tactical to strategic. Promotion cases are easier to write when you can say which step you are working at.'))

# ───────────────────────── Chapter 7
PICS[7] = sec(
    'A second worked example: the Azure playbook',
    p('The chapter includes Microsoft’s engagement playbook, which is useful because it attaches a measurable KPI to each phase. A service in phases 1 to 3 is “nascent”; 4 to 6 is “mature”.'),
    table(['Phase', 'What is measured'],
          [['1', 'Compliance with security and quality baselines; security posture score'],
           ['2', 'Share of critical user journeys covered by an SLO; share of outages detected automatically'],
           ['3', '75th-percentile time to mitigate; incident volume and repeat rate; alert noise ratio and routing accuracy'],
           ['4', 'Lead time, change failure rate, deployment frequency'],
           ['5', 'Number of critical risks; age of the last threat model'],
           ['6', 'Capacity plans kept up to date']]),
    p('Notice the order. It follows the hierarchy of production health: see the service first, respond well next, then deliver safely, then manage risk. If an interviewer asks how you would measure an SRE engagement, this table is a ready answer.'))

# ───────────────────────── Chapter 8
_pol = '''
<rect class="pn" x="70" y="30" width="180" height="250"/><rect class="pn" x="250" y="30" width="170" height="250"/><rect class="pn" x="420" y="30" width="180" height="250"/>
<text x="160" y="52" text-anchor="middle" class="b">Business as usual</text><text x="335" y="52" text-anchor="middle" class="b">Growing trade-offs</text><text x="510" y="52" text-anchor="middle" class="b">Feature freeze</text>
<line class="ln" x1="70" y1="280" x2="612" y2="280" marker-end="url(#ah)"/><line class="ln" x1="70" y1="280" x2="70" y2="22" marker-end="url(#ah)"/>
<path class="hl" d="M70 252L250 240C330 235 360 110 420 90L600 82"/>
<text x="160" y="302" text-anchor="middle" class="m">budget healthy</text><text x="335" y="302" text-anchor="middle" class="m">budget near zero</text><text x="510" y="302" text-anchor="middle" class="m">budget overspent</text>
<text transform="translate(30 155) rotate(-90)" text-anchor="middle" class="m">Engineering time on reliability</text>
<text x="80" y="232" class="m">a little</text><text x="590" y="74" text-anchor="end" class="m">nearly all of it</text>'''
PICS[8] = sec(
    'The error budget policy is a ramp, not a cliff',
    p('People often describe the policy as a switch: budget gone, features stop. The book’s figure shows something gentler and more useful.'),
    pic(640, 316, _pol, 'After Figure 8-1. As the remaining budget falls, the share of engineering time spent on reliability rises through three zones.', 'Line chart. Reliability work stays low while the budget is healthy, climbs as the budget nears zero, and takes nearly all engineering time once the budget is overspent.'),
    p('Write your policy with all three zones. In the middle one, name the trade-offs explicitly: slower rollouts, a reliability item in every sprint, a second approver for risky changes. A freeze should be the last step of a ramp everyone saw coming.'),
    '<div class="note"><b>Hyrum’s law and Hidalgo’s corollary</b>Hyrum’s law says every observable behaviour of a system will be depended on by somebody. Alex Hidalgo’s corollary applies it to reliability: the level you actually deliver is an observable behaviour too. Run at 99.99% for a year against a 99.9% SLO and your users will build on 99.99%. That is the argument for controlled budget burn, and for checking in with consumers every quarter or two.</div>',
    '<div class="note"><b>Code Yellow and Code Red</b>Google’s names for an organised emergency. A Code Red is already causing major damage, or will within a day or two. A Code Yellow could cause outages or business problems over the coming quarter: feature work stops and a temporary team forms. An exhausted error budget on a critical journey is a common trigger for a Code Yellow.</div>')

# ───────────────────────── Chapter 9
PICS[9] = sec(
    'From user goal to SLO',
    p('Server SLOs can be green while users can’t finish what they came to do. The book’s example is an email client whose send button is disabled: every API is healthy and nobody can send mail. The fix is to define SLOs from the user’s journey downward.'),
    flow([('Goal', '“Stay in touch with my friends.” Why the user came. You can’t instrument this'), ('Tasks', '“Send an email.” Steps towards the goal'), ('Interactions', 'Click compose, type, click send. The critical ones are very common or essential'),
          ('Instrumentation', 'Server SLI, client SLI, end-to-end SLI'), ('SLOs', 'Availability, latency, client-side success, quality')],
         'After Figure 9-4. A critical user journey (CUJ) is a goal plus its tasks; tasks are built from critical user interactions (CUIs).'),
    ul(['<b>Bad minute.</b> To roll several SLIs up into one journey SLO, call a minute bad if any SLI in the journey was bad in that minute.',
        '<b>The journey is a dimension.</b> A CUJ or CUI identifier travels with the request in trace context, so every metric can be sliced by journey.',
        '<b>Change supervision per journey.</b> Watch each journey across five kinds of change: server binary, server configuration, mobile app release (which can’t be rolled back), feature ramps and data updates.',
        '<b>A central registry</b> of journeys and an SDK give teams a well-lit path.']),
    '<h3>Case study: Maps and the “successful” failure</h3>',
    p('Maps has more than two billion monthly users. A server once returned well-formed responses built from malformed data, so searches “succeeded” with zero results. Server metrics saw nothing. The team wrote an invariant from the user’s side: the customer sees a non-zero number of valid results.'),
    p('Two things followed that are worth telling in an interview. First, better detection looked like <i>more</i> outages for a while, because problems that had always been there became visible. Second, once the signal existed, canary rollouts that raised the zero-results rate paused themselves. The team then sold customer-centric monitoring to product leads as delivery speed: the supervision built during the emergency could now protect every new feature.'),
    '<h3>Client-side telemetry</h3>',
    flow([('Instrumentation', 'In the app or browser'), ('Uploader', 'Batches and sends'), ('Public endpoint', ''), ('Collector service', 'Samples, validates'), ('Storage', '')],
         'Server metrics can’t see failed DNS, an expired certificate, a crash, or retries hiding an error. The client can.'),
    table(['Trade-off', 'What to do about it'],
          [['Batched uploads arrive late, with device clocks that drift', 'Record both device and server time, and expect late events in pipelines'],
           ['On-device storage fills up and events are dropped', 'Dropping the oldest hides the trigger; dropping the newest hides the present. Report counts ingested, uploaded and dropped, with reasons, so you have error bars'],
           ['A crash-looping app turns telemetry into a DDoS on yourself', 'Sample at the collector <i>and</i> push sampling down to clients'],
           ['The collector shares fate with the main service', 'Isolate it, or you lose telemetry exactly when you need it'],
           ['Old builds never update', 'Tag everything with build, release channel and OS or browser']]),
    p('YouTube uploads are the book’s example: server-side API availability looked high, and client-side instrumentation showed a noticeably worse experience.'),
    '<h3>Alerting on evidence, not on a single ratio</h3>',
    p('One error in twenty requests is a 5% error rate, and it is almost certainly noise. The book’s method treats each request as a trial, computes a confidence interval for the true error rate, and pages only when the <b>lower</b> bound is above the SLO threshold. The observed rate can cross the line many times without the alert firing (Figure 9-7 shows exactly this). The Labs station has a calculator for it.'),
    p('For latency, compare against the service’s own past: group requests into cohorts by method, customer and workload shape, keep a 30-day mean and standard deviation, and alert on z-scores. “Slower than usual” is an implicit SLO that works across products.'),
    '<h3>What telemetry costs, and what you keep</h3>',
    p('Data loses value as it ages, so retention is a design decision. Google’s Horizontal Monitoring Data (HMD) collects a common set of series centrally, so a new service gets them without asking.'),
    table(['Data', 'Kept in memory', 'Kept on disk'],
          [['Raw, minute-level', 'Hours', 'Weeks'], ['Precomputed aggregates', 'Hours', 'Full resolution for weeks, then 30-minute resolution for years']]),
    p('Aggregation saves at least ten-fold, series nobody has read for months are phased out, and owners can extend retention if they have quota. On AWS the same thinking gives you CloudWatch metric resolution tiers, log retention per log group, S3 lifecycle rules for traces and logs, and cost allocation tags for chargeback.'),
    '<h3>Four questions before adopting an observability product</h3>',
    '<ol><li>How well supported is it?</li><li>Does it conform to open standards such as those from the CNCF?</li><li>Does it work on every platform you have: backend, mobile, web?</li><li>What happens if you don’t adopt it?</li></ol>',
    p('Waze is the cautionary tale. It moved from an in-house library to OpenCensus to OpenTelemetry, the last migration took over a year, and overlapping systems confused developers. The team calls instrumentation a ten-year decision. Open standards let you keep the agent and swap the backend, but dashboards and alerts still have to be migrated.'),
    '<h3>Also in the chapter</h3>',
    ul(['<b>Universal and horizontal alerts.</b> About a fifth of all SRE alerts at Google are universal ones every service inherits. Component owners also publish alerts for everything that uses their component, such as an auth library.',
        '<b>High-availability telemetry must come back fresh.</b> After a monitoring outage, serve the newest data first and relax completeness before availability. Monitoring must not depend on the services it watches.',
        '<b>eBPF</b> gives logs, profiles, network metrics and traces without code changes, in exchange for kernel-level permissions and less depth than hand instrumentation.',
        '<b>Privacy.</b> “Anonymous” per-region data is not anonymous when one customer is alone in a region. Classify data, minimise and redact, keep it in its locale, set wipe-out periods by type, and use one vetted SDK so teams can’t overshare.',
        '<b>Agents.</b> A trace shows what an agent was asked and what it answered, and says nothing about whether the answer was good. Quality needs its own signal.']))

# ───────────────────────── Chapter 11
_ras = '''
<path class="pn" d="M90 40L90 300L470 300L600 40z"/>
<line class="ln" x1="90" y1="40" x2="90" y2="300"/><line class="ln" x1="90" y1="300" x2="470" y2="300"/><line class="ln" x1="470" y1="300" x2="600" y2="40" style="stroke:var(--red)"/>
<line class="dash" x1="420" y1="300" x2="550" y2="40"/>
<text transform="translate(74 170) rotate(-90)" text-anchor="middle" class="b">Economic failure</text>
<text x="240" y="322" text-anchor="middle" class="b">Unacceptable workload</text>
<text x="612" y="150" class="b" style="fill:var(--red)">Acceptable</text><text x="612" y="170" class="b" style="fill:var(--red)">performance</text><text x="612" y="190" class="m">accidents</text><text x="612" y="208" class="m">lie beyond</text>
<circle class="fc" cx="300" cy="170" r="9"/><text x="318" y="198" class="m">operating point</text>
<line class="ln" x1="110" y1="120" x2="270" y2="160" marker-end="url(#ah)"/><text x="112" y="104" class="m">pressure for efficiency</text>
<line class="ln" x1="230" y1="285" x2="285" y2="195" marker-end="url(#ah)"/><text x="120" y="262" class="m">drift to least effort</text>
<line class="ln" x1="455" y1="120" x2="335" y2="160" marker-end="url(#ah)" style="stroke:var(--green)"/><text x="336" y="104" class="m">safety work pushes back</text>
<text x="446" y="322" text-anchor="middle" class="m">error margin</text>'''
PICS[11] = sec(
    'Rasmussen’s boundaries, drawn',
    p('Of the safety-science models in this chapter, Rasmussen’s is the one that needs a picture. A team works inside a space with three edges. Go past the first and the business fails. Go past the second and people burn out. Go past the third and you have an accident.'),
    pic(720, 340, _ras, 'After Figure 11-1. Two steady pressures move the operating point away from the cost and workload edges, which means towards the accident edge. The margin shrinks without anyone deciding to shrink it.', 'A space bounded by economic failure, unacceptable workload and acceptable performance. Arrows show cost pressure and least effort pushing the operating point towards the performance boundary, and safety culture pushing back.'),
    p('This explains “drift into failure”. Nobody chose to be unsafe. Each shortcut was a sensible answer to cost or workload pressure, and each one that didn’t cause an outage looked like proof it was fine. The counter-force has to be deliberate and continuous: error budgets, game days, postmortem follow-through. A poster campaign after an outage pushes back for a week.'))

# ───────────────────────── Chapter 12
_loop = '''
<rect class="pn" x="170" y="24" width="360" height="78" rx="10" style="stroke:var(--c);stroke-width:2"/><text x="350" y="52" text-anchor="middle" class="b">Controller: the engineers</text><text x="350" y="74" text-anchor="middle" class="m">decision making + a mental model of the service</text>
<rect class="pn" x="200" y="216" width="300" height="70" rx="10" style="stroke:var(--c);stroke-width:2"/><text x="350" y="246" text-anchor="middle" class="b">Controlled process</text><text x="350" y="267" text-anchor="middle" class="m">the production service</text>
<line class="ln" x1="270" y1="102" x2="270" y2="214" marker-end="url(#ah)"/><text x="258" y="150" text-anchor="end" class="b">Control action</text><text x="258" y="170" text-anchor="end" class="m">roll back the release</text>
<line class="ln" x1="430" y1="216" x2="430" y2="104" marker-end="url(#ah)"/><text x="442" y="150" class="b">Feedback</text><text x="442" y="170" class="m">service health,</text><text x="442" y="188" class="m">customer escalations</text>
<line class="ln" x1="90" y1="251" x2="198" y2="251" marker-end="url(#ah)"/><text x="88" y="240" class="m">requests</text>
<line class="ln" x1="500" y1="251" x2="610" y2="251" marker-end="url(#ah)"/><text x="530" y="240" class="m">responses</text>'''
PICS[12] = sec(
    'The control loop, drawn',
    pic(700, 306, _loop, 'After Figure 12-3. Every STPA and CAST analysis is built from loops like this one. Most outages come from the two arrows and the mental model, not from the boxes.', 'A controller box above a controlled-process box. A control action arrow goes down, a feedback arrow goes up, and requests and responses pass through the process.'),
    p('Read the picture as four places to look for trouble: the control action can be wrong or late, the feedback can be missing or misleading, the controller’s mental model can be out of date, and the process can behave in a way nobody modelled.'),
    '<h3>A worked unsafe control action</h3>',
    p('In the Maps example a geospatial data specialist asks for approval, and a review team’s approver consults subject-matter experts before answering. One unsafe control action falls straight out of the diagram: the approver approves when the experts have <i>not</i> approved. Nothing failed. The structure allowed it. The hazard that analysis is protecting against is stated plainly: the published map disagrees with the real world.'),
    '<h3>How CAST layers an incident</h3>',
    flow([('Adverse events', 'Bug introduced, buggy release deployed, not rolled back, service crashed'), ('Controllers’ behaviour', 'What each person or system did, and why it made sense to them'),
          ('Causal factors', 'Global rollouts, missing tests, limited telemetry, time pressure, tool limits'), ('Systemic factors', 'Management of change, safety culture, safety information, communication, environment')],
         'After Figure 12-9. A postmortem that stops at the first box fixes one bug. Recommendations aimed at the last box fix a class of them.'),
    '<div class="note"><b>Why bother before launch</b>The book’s Figure 12-11 makes the economic case in one picture: most design flaws are introduced during design, most are found in testing or production, and fixing them is most expensive by far in production. Ben Treynor Sloss’s summary of STPA is that it is like being told about your outages before they happen, so you can choose which to fix and which to live with.</div>')

# ───────────────────────── Chapter 13
PICS[13] = sec(
    'Where automation fits in the incident loop',
    flow([('Detect', ''), ('Triage', ''), ('Mitigate', ''), ('Resolve', ''), ('Learn', ''), ('Remediate', 'Fix the class, which feeds detection')],
         'After Figure 13-2. Automation can help at every stage. Start where humans are slowest and the action is safest, which is usually detection and generic mitigation.'),
    p('Two footnotes from the chapter are worth carrying into an interview. Static thresholds force a trade between false alarms and missed problems, so the more ambiguous the signal, the more hand-tuning it needs: that is toil with a mathematical cause. And automation has limits of its own. Google’s automatic capacity tool never worked for one large traffic system because the configuration grew big enough to break the solver.'))

# ───────────────────────── Chapter 14
_pyr = '''
<path class="pn" d="M60 250L580 250L520 190L120 190z"/><path class="pn" d="M120 190L520 190L460 130L180 130z"/><path class="pn" d="M180 130L460 130L400 70L240 70z"/><path class="pn" d="M240 70L400 70L320 14z" style="stroke:var(--c);stroke-width:2"/>
<text x="320" y="226" text-anchor="middle" class="b">Unit tests</text><text x="320" y="166" text-anchor="middle" class="b">Integration tests</text><text x="320" y="106" text-anchor="middle" class="b">System tests</text><text x="320" y="56" text-anchor="middle" class="b" style="font-size:12px">Resilience</text>
<text x="600" y="226" class="m">many, fast, cheap</text><text x="600" y="56" class="m">few, slow, realistic</text>'''
PICS[14] = sec(
    'The hierarchy of tests',
    pic(760, 266, _pyr, 'After Figure 14-1. The familiar test pyramid with one more layer on top: resilience testing, where you break things on purpose (fault injection, DiRT, load tests).', 'A four-layer pyramid: unit tests at the base, then integration, system, and resilience tests at the top.'),
    '<h3>A rollout rule of thumb</h3>',
    flow([('0.1%', 'Start here'), ('1%', 'Ramp fast at the low end'), ('10%', 'A day per step'), ('50% → 100%', 'Slow down at the high end')],
         'From a footnote in the chapter: begin at 0.1% of traffic and grow roughly ten-fold every 24 hours, moving across server locations as you go.'),
    p('The reasoning is about exposure. At 0.1% a bad release hurts almost nobody, so move quickly. At 50% a bad release is a major outage, so bake longer. On AWS this is a CodeDeploy or AppConfig deployment strategy with a bake time and a CloudWatch alarm that triggers rollback.'),
    '<div class="note"><b>Client-focused supervision</b>The book’s Figure 14-3 shows why you watch a rollout from the caller’s side. A frontend calls two backend tasks. The one on the new version returns bad data with a success code, and the user sees an error. The backend’s own dashboards look healthy, and only the client-side view shows the failure.</div>',
    p('One more honest detail: the old claim that a bug costs 100 times more to fix in production is more nuanced than the slogan. The chapter notes it is closer to 100 to 1 for severe defects and about 2 to 1 for minor ones. Use the nuanced version and you will sound like you’ve read the source.'))

# ───────────────────────── Chapter 15
_tri = '''
<path class="hl" d="M320 30L560 260L80 260z"/>
<text x="320" y="20" text-anchor="middle" class="b">Performance</text><text x="66" y="284" class="b">Cost</text><text x="574" y="284" text-anchor="end" class="b">Reliability</text>
<circle class="pn" cx="320" cy="186" r="52"/><text x="320" y="182" text-anchor="middle" class="b">Business</text><text x="320" y="202" text-anchor="middle" class="b">goals</text>'''
PICS[15] = sec(
    'The iron triangle of capacity',
    pic(640, 296, _tri, 'After Figure 15-1. Capacity planning is choosing a point inside this triangle on purpose. Pull one corner and the other two move.', 'A triangle with performance, cost and reliability at the corners and business goals in the centre.'),
    p('Spare capacity buys reliability and costs money. Running hot saves money and costs latency under load. There is no free corner, which is why the chapter keeps repeating that the target is a business choice.'),
    '<h3>Making capacity fungible</h3>',
    p('Stranded capacity is capacity you own in a place or shape you can’t use. The chapter’s figures show two ways out. Work that tolerates delay can fill the troughs of local demand, which lowers the global total. And you can make workloads easier to move:'),
    tiles([('Architect for constraints', 'Break a rigid application into services that scale on their own and don’t care which region they run in.'),
           ('Shift work in time', 'Batch, training and backfills run when interactive demand is low.'),
           ('Improve connectivity', 'A better network lets demand in one place use supply in another.')]),
    p('On AWS: Spot and Batch for time-shifted work, Auto Scaling groups with several instance types so you aren’t tied to one, and multi-Region designs so demand can follow supply.'))

# ───────────────────────── Chapter 16
_tl = '''
<line class="ln" x1="40" y1="150" x2="700" y2="150" marker-end="url(#ah)"/>
<g class="m"><circle cx="70" cy="150" r="7" class="fc"/><circle cx="170" cy="150" r="5" class="fc"/><circle cx="260" cy="150" r="5" class="fc"/><circle cx="350" cy="150" r="7" class="fc"/></g>
<text x="70" y="182" text-anchor="middle" class="m">oldest backup</text><text x="70" y="200" text-anchor="middle" class="m">still kept</text>
<text x="215" y="182" text-anchor="middle" class="m">older backups</text>
<text x="350" y="182" text-anchor="middle" class="m">latest good</text><text x="350" y="200" text-anchor="middle" class="m">backup</text>
<path d="M440 132L452 150L440 168L428 150z" style="fill:var(--red)"/><text x="440" y="186" text-anchor="middle" class="b" style="fill:var(--red)">incident</text>
<circle cx="500" cy="150" r="4" class="fc"/><circle cx="550" cy="150" r="4" class="fc"/><circle cx="640" cy="150" r="7" style="fill:var(--green)"/>
<text x="500" y="186" text-anchor="middle" class="m">detect</text><text x="550" y="186" text-anchor="middle" class="m">act</text><text x="640" y="186" text-anchor="middle" class="b" style="fill:var(--green)">restored</text>
<path class="hl" d="M70 104L70 92L350 92L350 104"/><text x="210" y="80" text-anchor="middle" class="b">RWO: how far back you can go</text>
<path class="hl" d="M350 124L350 116L440 116L440 124"/><text x="395" y="108" text-anchor="middle" class="b">RPO</text>
<path class="hl" d="M440 104L440 92L640 92L640 104"/><text x="540" y="80" text-anchor="middle" class="b">RTO: detect + act + restore</text>
<text x="395" y="52" text-anchor="middle" class="m">data written here is lost</text><line class="dash" x1="395" y1="58" x2="395" y2="92"/>'''
PICS[16] = sec(
    'RPO, RTO and RWO on one timeline',
    pic(730, 216, _tl, 'After Figure 16-3. Three objectives, three different stretches of time. RTO is cumulative: the clock starts at the incident, so slow detection spends your recovery time before you’ve begun.', 'A timeline of backups, an incident and a restore. RWO spans from the oldest retained backup to the latest. RPO spans from the latest backup to the incident. RTO spans from the incident to full restoration.'),
    p('The figure also marks a point of no return. If the corruption is older than your oldest retained backup, no restore can help, which is why RWO has to be longer than your worst realistic time to notice a problem. Silent corruption found after 40 days with 30 days of backups is unrecoverable.'),
    '<h3>Incremental or differential?</h3>',
    table(['', 'Incremental', 'Differential'],
          [['Each backup holds', 'Changes since the last backup of any kind', 'Changes since the last <i>full</i> backup'],
           ['To restore Wednesday you need', 'The full backup plus Monday, Tuesday and Wednesday', 'The full backup plus Wednesday'],
           ['Backup size', 'Smallest', 'Grows through the week'], ['Restore', 'More steps, more that can go wrong', 'Faster and simpler']]),
    p('This is an RPO-against-RTO trade in miniature: incrementals are cheap to take often, differentials are quick to restore. AWS Backup takes incremental backups for most services and handles the chain for you, but the trade still shows up in restore time, so measure it with a restore test.'),
    '<div class="note"><b>Integrity outranks recovery</b>The chapter describes Bigtable’s stance: recover as much as possible before declaring data lost, but never at the price of integrity. The team must be able to say that no person compromised user data on the way, and exceptions need senior engineering, customer and legal approval.</div>')

# ───────────────────────── Chapter 17
PICS[17] = sec(
    'Two pictures from the chapter',
    tiles([('Region A · zone 1', '25% of capacity'), ('Region A · zone 2', '25% of capacity'), ('Region B · zone 1', '25% of capacity'), ('Region B · zone 2', '25% of capacity')]),
    p('After Figure 17-1: two regions with two zones each. Lose a zone and you lose a quarter; lose a region and you lose half. So “N+1” is not a number you can state without saying which failure domain you mean. Sized to survive a zone, each remaining zone must take a third more. Sized to survive a region, each region must carry everything.'),
    p('Figure 17-2 shows incident severity growing from normal, to emergency, to disaster, which is the same three-step scale as the incident modes above. The practical point is that the tooling for each step must depend on less than the step before it.'),
    '<div class="note"><b>Risk register</b>For rare, severe risks the chapter suggests a simple register: for each risk, its probability, its impact, an owner and a mitigation. It turns “what if a region disappears?” from a debate into a list someone is accountable for.</div>')

# ───────────────────────── Chapter 18
_zone = '''
<line class="ln" x1="80" y1="290" x2="620" y2="290" marker-end="url(#ah)"/><line class="ln" x1="80" y1="290" x2="80" y2="24" marker-end="url(#ah)"/>
<path d="M80 250L80 190L560 30L620 30L620 70L140 290L80 290z" class="fc" style="opacity:.18"/>
<path class="hl" d="M80 220L620 40"/>
<text x="350" y="318" text-anchor="middle" class="m">How bad is the worst outcome?   minor → catastrophic</text>
<text transform="translate(36 160) rotate(-90)" text-anchor="middle" class="m">Strength of control   hint → block</text>
<text x="330" y="150" text-anchor="middle" class="b" transform="rotate(-18.4 330 150)">Effective zone</text>
<text x="100" y="64" class="b">Too restrictive</text><text x="100" y="84" class="m">hurts velocity and goodwill</text>
<text x="610" y="232" text-anchor="end" class="b">Too little control</text><text x="610" y="252" text-anchor="end" class="m">relies on humans never slipping</text>'''
PICS[18] = sec(
    'The effectiveness zone',
    pic(660, 330, _zone, 'After Figure 18-2. Match the strength of a guardrail to the cost of getting it wrong. Controls are effective along the diagonal.', 'Chart with consequence severity across and control strength up. A diagonal band is the effective zone. Above it controls are too restrictive; below it there is too little control.'),
    p('A hard block on a typo-level risk teaches people to route around the platform. A gentle hint on an action that can delete production data relies on nobody ever having a bad day. When a team complains that a guardrail is annoying, place it on this chart before arguing.'),
    '<h3>How far has a practice been built into the platform?</h3>',
    flow([('0 · YOLO', 'Nothing in place'), ('1 · Ad hoc', 'Each team does it its own way'), ('2 · Guided', 'Documented best practice'), ('3 · Engineered', 'Built into the paved path'), ('4 · Assured', 'Enforced and verified by the platform')],
         'After Figure 18-3. A typology for any one quality attribute, such as “safe rollouts” or “backups”.'),
    p('“Shift down” means moving a practice from type 2, where every feature team has to know and do it, to type 3 or 4, where the platform does it. The chapter’s first figure draws this as a line: assurance moves from above the line (feature teams) to below it (the platform).'),
    '<div class="note"><b>Build horizon</b>One of Google’s quieter guardrails: binaries older than roughly six months are not allowed to run. Nobody has to chase teams to pick up security fixes, because standing still stops being an option. It is a good example of changing the game so the safe choice is the easy one.</div>')

# ───────────────────────── Chapter 20
_pow = '''
<line class="ln" x1="70" y1="250" x2="600" y2="250" marker-end="url(#ah)"/><line class="ln" x1="70" y1="250" x2="70" y2="24" marker-end="url(#ah)"/>
<path class="hl" d="M70 170C170 90 330 62 580 54"/>
<line class="dash" x1="70" y1="170" x2="250" y2="170"/><text x="84" y="192" class="m">idle power: a machine at 0% still draws a lot</text>
<text x="335" y="278" text-anchor="middle" class="m">Machine utilisation   0% → 100%</text><text transform="translate(34 140) rotate(-90)" text-anchor="middle" class="m">Power drawn</text>
<text x="150" y="88" class="b">steep</text><text x="470" y="44" class="b">nearly flat</text>'''
PICS[20] = sec(
    'Three pictures from the chapter',
    '<h3>The model release pipeline</h3>',
    flow([('Develop and version', 'Model, prompt and config together'), ('Qualify automatically', 'Platform checks, then model evals, then simulated user journeys'), ('Readiness gate', 'Fail and it goes back', 'red'),
          ('Progressive rollout', 'Canary'), ('Serve and monitor', 'Feedback returns to development')],
         'After Figure 20-2. The same shape as a software release, with one extra kind of test: does the model still give good answers?'),
    p('The qualification step has three layers on purpose. Infrastructure checks ask whether the model runs at all on this hardware. Evals ask whether its answers are good. Journey simulation asks whether the product built on it still works. A model can pass the first two and fail the third.'),
    '<h3>Why idle accelerators are expensive twice</h3>',
    pic(640, 290, _pow, 'After Figure 20-4. Power rises steeply at low utilisation and flattens at the top. Going from 30% to 35% costs far more power than going from 75% to 80%.', 'Curve of power against machine utilisation, starting well above zero, rising steeply, then flattening.'),
    p('So a half-idle fleet wastes the hardware and still pays most of the power bill. Run fewer machines hotter, and turn the rest off, since shutting down is the only way to remove idle draw.'),
    '<h3>Securing agents: two layers and a test loop</h3>',
    tiles([('Runtime policy enforcement', 'Hard limits on what the agent is allowed to do, checked outside the model. Dependable, because it doesn’t rely on the model behaving.', 'blue'),
           ('Reasoning-based defences', 'A hardened base model, classifiers and safety fine-tuning. Flexible, but probabilistic.', 'purple'),
           ('Continuous assurance', 'Regression tests, variant analysis, red teams and human reviewers keep both layers honest.', 'green')]),
    p('After Figure 20-5. The interview line: never let the model be its own only guardrail. On AWS that means IAM policies and service control policies as the hard layer, Bedrock Guardrails as the reasoning layer, and evaluation jobs as the test loop.'),
    '<div class="note"><b>Isolation is more than memory</b>A footnote warns that sharing accelerators between models needs isolation of high-bandwidth memory, interconnect bandwidth and duty cycle. Otherwise one model’s prefill phase can starve another model’s decoding, and a noisy neighbour shows up as someone else’s latency.</div>')

# ───────────────────────── Chapter 21
_safe = '''
<g style="--s:var(--c)">
<rect class="pn" x="20" y="96" width="130" height="68" rx="10" style="stroke:var(--c);stroke-width:2"/><text x="85" y="124" text-anchor="middle" class="b">AI agent</text><text x="85" y="144" text-anchor="middle" class="m">action + reason</text>
<rect class="pn" x="200" y="96" width="150" height="68" rx="10" style="stroke:var(--c);stroke-width:2"/><text x="275" y="124" text-anchor="middle" class="b">Risk assessment</text><text x="275" y="144" text-anchor="middle" class="m">knows the context</text>
<rect class="pn" x="410" y="20" width="170" height="68" rx="10" style="stroke:var(--red);stroke-width:2"/><text x="495" y="48" text-anchor="middle" class="b">Human approval</text><text x="495" y="68" text-anchor="middle" class="m">high risk</text>
<rect class="pn" x="410" y="172" width="170" height="68" rx="10" style="stroke:var(--green);stroke-width:2"/><text x="495" y="200" text-anchor="middle" class="b">Atomic execution</text><text x="495" y="220" text-anchor="middle" class="m">act, validate, or undo</text>
<rect class="pn" x="630" y="96" width="120" height="68" rx="10" style="stroke:var(--c);stroke-width:2"/><text x="690" y="124" text-anchor="middle" class="b">Outcome</text><text x="690" y="144" text-anchor="middle" class="m">and telemetry</text>
<line class="ln" x1="150" y1="130" x2="198" y2="130" marker-end="url(#ah)"/>
<line class="ln" x1="350" y1="116" x2="408" y2="62" marker-end="url(#ah)"/><line class="ln" x1="350" y1="144" x2="408" y2="198" marker-end="url(#ah)"/>
<line class="ln" x1="495" y1="88" x2="495" y2="170" marker-end="url(#ah)"/><text x="503" y="134" class="m">approved</text>
<line class="ln" x1="580" y1="206" x2="640" y2="166" marker-end="url(#ah)"/>
<path class="dash" d="M690 164L690 268L85 268L85 166" marker-end="url(#ah)"/><text x="388" y="260" text-anchor="middle" class="m">feedback: retraining and better prompts</text>
</g>'''
PICS[21] = sec(
    'The safety loop for an agent with production access',
    pic(770, 284, _safe, 'After Figure 21-1. Every proposed action is scored for risk before anything runs. Low-risk actions go straight to an executor that can undo them; high-risk ones wait for a person.', 'Flow: an AI agent proposes an action, a risk assessment engine routes it either to a human approval queue or to an atomic execution manager, and the outcome feeds back to improve the agent.'),
    ul(['The agent sends its <b>reason</b> with the action, so a reviewer or an audit can check the thinking, not only the command.',
        '<b>Progressive authorisation</b>: as a class of action proves safe, it moves from the approval queue to automatic execution.',
        'The executor treats each action as a <b>transaction</b>: do it, validate the result, roll back if validation fails. Destructive migrations need extra design work to be reversible at all.',
        'Below a confidence threshold, the system should not show the suggested mitigation to the on-caller. A weak suggestion during an incident is worse than none.']),
    '<h3>What an investigation agent actually does</h3>',
    flow([('Plan', ''), ('Read server errors', ''), ('Fetch job details', ''), ('Check for anomalies', 'Is this transient?'), ('Is an incident open?', ''), ('Find the owner', ''), ('Escalate', 'To the right developer')],
         'After Figure 21-4, shortened. Each step is a tool call a human on-caller would also make. The value is doing all of them in seconds, in the same order every time.'))


CSS = '''
.pic{margin:22px 0;border:1px solid var(--rule);border-radius:12px;padding:14px 14px 10px;overflow-x:auto}
.pic svg{display:block;width:100%;min-width:560px;height:auto;font-family:inherit;color:var(--ink)}
.pic text{fill:currentColor;font-size:14px}
.pic text.m{fill:var(--mute)}.pic text.b{font-weight:800}
.pic .ln{stroke:currentColor;stroke-width:2;fill:none}
.pic .dash{stroke:var(--mute);stroke-width:2;stroke-dasharray:6 5;fill:none}
.pic .pn{fill:var(--panel);stroke:var(--rule);stroke-width:1.5}
.pic .hl{stroke:var(--c);stroke-width:3.5;fill:none;stroke-linecap:round;stroke-linejoin:round}
.pic .fc{fill:var(--c)}
.pic figcaption{font-size:14px;color:var(--mute);margin-top:8px;max-width:70ch;line-height:1.5}
table.num td:last-child,table.num th:last-child{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
'''

# ───────────────────────── second batch of figures
PICS[3] += (
    '<h3>How the storage layers stack</h3>'
    + flow([('Spanner · Bigtable · Blobstore', 'Three services with different data models'), ('Colossus', 'One cluster file system under all of them'), ('Byte storage', 'Disks and flash')],
           'After Figure 3-1. Blobstore even splits its own work: small objects go into Bigtable, large ones straight to Colossus.')
    + p('The design lesson is layering. Each service solves one problem and builds on the one below, so an improvement in Colossus reaches everything above it. The risk is the mirror image: a Colossus problem is everybody’s problem, which is why the lower a layer sits, the stricter its SLO has to be.'))

PICS[5] += (
    '<h3>Growing your own hiring pipeline</h3>'
    + p('Figure 5-2 charts a university outreach programme Google ran in Ireland over seven years. Internships and placements grow first, and full-time hires follow a few years later as interns return. Two points to take from it: get students in early, in their first or second year, because the bar for an internship is lower and it lets both sides try the job. And report short-term wins, such as applicant numbers and interns hired, because a seven-year payoff needs sponsors who stay interested. Much of the benefit showed up in under three years.'))

PICS[9] += sec(
    'The knowledge graph, drawn',
    flow([('Product A', 'Where users notice'), ('Service', ''), ('Service', ''), ('Shared dependency', 'Where it started', 'red')],
         'After Figures 9-1 and 9-5, simplified. The book’s versions show whole product areas as nodes, with normal call paths in one colour and the path of a performance problem in another.'),
    p('This is what “product-focused observability” looks like in practice. An investigator sees which products are affected and where the degradation entered, without needing to be an expert in every service in between. It is also the structure an AI assistant needs: a graph it can walk is far more useful to it than a wall of dashboards.'),
    p('On AWS you can get part of the way with X-Ray or Application Signals service maps, and resource tags that name the product each service belongs to. The tags are the part teams skip, and the part that makes the graph answer product questions.'),
    '<div class="note"><b>What the Maps failure looked like</b>Figure 9-6 is a screenshot worth picturing: a search for “coffee” in the middle of San Francisco, and Maps replying that it can’t find any. Every server returned success. That one image is the argument for measuring from the user’s side.</div>')

PICS[12] = PICS[12].replace('<h3>A worked unsafe control action</h3>', sec(
    'Two ways to explain the same outage',
    flow([('A change with a bug is submitted', 'Fix: add a test'), ('The release includes it', 'Fix: run tests on every build'), ('It rolls out to production', 'Fix: progressive rollout'), ('Services crash', 'Fix: crash alerts')],
         'After Figure 12-1. The chain-of-events view. Each link gets a patch, and each patch is reasonable.'),
    p('The trouble is that the chain only describes this bug. The systems view in Figure 12-2 asks a different question at each step: what <i>influenced</i> the decision?'),
    table(['Controller', 'Factors that shaped its decisions', 'What followed'],
          [['Engineers', 'Missing tests, time pressure, tool limits, code complexity, skills', 'The change was submitted, rolled out, and not rolled back'],
           ['Build system', 'Missing tests, flaky or skipped tests, no QA acceptance step', 'The bug was included in the release'],
           ['Deployment system', 'Global rollouts, limited telemetry, complex production configuration', 'Production crashed']]),
    p('Notice that software systems are treated as decision-makers too. Fixing “time pressure” or “global rollouts” prevents many future outages, including ones with entirely different bugs.')) + '<h3>A worked unsafe control action</h3>')

PICS[12] += (
    '<h3>The misnamed cities, in one picture</h3>'
    + flow([('Census dataset arrives', ''), ('Evaluated', 'By sampling'), ('Published to Maps', ''), ('Users report wrong names', ''), ('Data rolled back', ''), ('Fixed', '')])
    + p('The data was too large to review by hand, so the specialists checked four states where they had local knowledge: Washington, California, Texas and New York. The six states with wrong city names were Montana, Kansas, Indiana, Kentucky, Tennessee and Georgia. Figure 12-7 puts both sets on a map and they don’t overlap at all.')
    + p('A classic postmortem calls that imperfect sampling and stops. CAST asks why sampling four states seemed sufficient, who knew the sample wasn’t representative, and what feedback would have shown it. That is how the same incident produced 22 recommendations where the postmortem had 8.')
    + p('The final figure in the chapter repeats the design-flaw grid with one arrow added, labelled STPA, pointing from production back to design. The whole method is that arrow: find the flaw where fixing it is cheap.'))

PICS[13] += (
    '<h3>Is it worth the time?</h3>'
    + p('For the pure time-saving case, the chapter points to the well-known xkcd chart (number 1205) that tells you how long you can spend automating a task before you lose more time than you save, counted over five years. The sum behind it is simple enough to do in an interview: time saved per run × runs per day × 1,825 days.')
    + table(['You save', 'How often', 'Break-even over five years'],
            [['30 seconds', '50 times a day', 'about 760 hours'], ['5 minutes', 'once a day', 'about 150 hours'], ['1 hour', 'once a month', '60 hours'], ['5 minutes', 'once a year', '25 minutes']], cls='num')
    + p('Then say why the chart is not the whole answer, because the book does. Time is only one of four reasons to automate. A task you run once a year in an emergency fails the chart and may still be the most valuable thing to automate, because consistency under stress and scale matter more than minutes.'))

PICS[15] += sec(
    'Case study: the Google Meet loop',
    p('When COVID lockdowns began, demand for Meet grew faster than any forecast. Figure 15-7 shows the process the team ran every day. It is the best single diagram in the chapter for an interview, because it turns “we scaled” into a method.'),
    flow([('Review the inputs', 'Customer onboarding and promotions, lockdown trends, forecast models, usage trends'), ('One question', 'Do we have enough for the load we expect a week from now?'), ('Yes', 'Wait a day and ask again', 'green'), ('No', 'Start the four workstreams', 'red')]),
    tiles([('Capacity', 'Are there more raw resources we can turn into capacity? If not, find some.'),
           ('Dependencies', 'Can every system we depend on take the extra load? If not, find workarounds.'),
           ('Bottlenecks', 'Can we remove artificial limits to use what we have better? Then find the next limit.'),
           ('Control knobs', 'Can we change the system quickly to head off a large outage? If not, build more escape hatches.')]),
    p('Everything the four workstreams produce goes through a fifth, production changes, whose only job is to deploy safely. Then the loop starts again. The one-week horizon is the detail to remember: short enough to forecast, long enough to act.'),
    '<h3>Why pooling works</h3>',
    p('Figure 15-4 plots resource use for four regions over three days. Each has a daily peak, and the peaks fall at different hours. That is the whole reason a shared pool needs less than the sum of its parts. Figure 15-3 shows how Google layers it: physical CPU, memory and drives feed foundational pooled services (compute and memory in Borg, disk in Colossus), and those feed composite services built on top, such as Bigtable.'))

PICS[16] += (
    '<h3>Legal is not the same as right</h3>'
    + table(['', 'Lawful good', 'Lawful neutral', 'Lawful evil'],
            [['With users’ data', 'Follows the law and puts the user’s interest first, even at a cost', 'Follows the law, makes no sacrifices for users', 'Follows the law and uses every permitted advantage for itself']])
    + p('The chapter borrows the alignment grid from Dungeons &amp; Dragons (Figure 16-1) to make one point: all three columns obey the law. Aim for the first. Its test is practical: if you use data in a way the user didn’t ask for and only you benefit, think about how they would react on finding out.'))

PICS[20] += (
    '<h3>Planning accelerator capacity</h3>'
    + flow([('Demand', 'Organic growth plus inorganic: launches, model changes, new hardware generations'), ('Forecast', ''), ('Order or rebalance', 'Periodic orders, or move supply across the fleet'), ('Allocate', 'A footprint and sizing matrix, with redundancy and location rules'), ('Deploy', 'Moves and resizes'), ('Monitor', '7-day 95th-percentile occupancy against targets')],
           'After Figure 20-3. Monitoring feeds the next forecast. The loop is the ordinary capacity loop from chapter 15; what changes is that supply takes months to arrive and can’t be bought on demand.'))

PICS[21] += (
    '<h3>Why anomaly detection is harder than the slide suggests</h3>'
    + tiles([('The ideal', 'A flat, predictable baseline and one clean spike. Any threshold finds it.', 'green'),
             ('The reality', 'A noisy line shaped by a feature launch, a viral search topic, a local ISP outage and a regional traffic migration, all in the same window.', 'red')])
    + p('After Figure 21-2. This is why the chapter argues for models that take context as input. A threshold can’t tell a launch from an outage. A system that knows a launch was scheduled can.')
    + '<h3>Grading the agent: LLM as judge</h3>'
    + p('Figure 21-5 shows how Google evaluates its investigation agent. A second model scores each run against labelled incidents on two questions, was the <b>diagnosis</b> right and was the <b>mitigation</b> right, and writes a critique. A failed run also records the failure mode, the step where it went wrong, and why.')
    + p('The example failure is instructive: the agent had a tool for correlating failures with recent rollouts, didn’t call it, and followed a log line about an old bug instead. It missed the chance to roll back. That is exactly the mistake a tired human makes, and having it written down per step is what lets you fix the prompt or the tool order.')
    + p('On AWS the equivalent is a Bedrock evaluation job with a judge model, run against a set of past incidents every time you change the agent’s prompt, tools or model.'))

NEWCARDS = [
    ['Why did the 2nd edition replace Dickerson’s pyramid?', 'Its lower layers were all reactive, capacity had its own layer while data integrity was buried, culture was only implied, and it had no “reliable by default” end state.'],
    ['Three dimensions along which preparedness cuts incident impact', 'Length (detect and mitigate fast), frequency (follow through on postmortem actions) and scope (failure domains, graceful degradation).'],
    ['How many engineer-hours does one hour of major downtime cost?', 'Roughly 100 to 1,000: managing the outage, the review, internal comms, about 100 hours of remediation and about 100 of customer communication.'],
    ['Six questions before adopting SRE', 'Biggest operational challenges? Resources and skills? Can you start small? What is at stake? How do users interact (do they retry)? Is timing a factor?'],
    ['Why are RTO and RPO not enough on their own?', 'They are binary and reactive. They can’t describe gray failures such as “30% slower for 10% of users”, which SLOs can.'],
    ['What is the Treynor curve?', 'Google’s SRE hiring bar drawn as a curve between the software bar and the systems bar. A candidate just under both can still be a hire if the combination lands above the curve.'],
    ['Three zones of an error budget policy', 'Business as usual, growing trade-offs as the budget nears zero, and feature freeze once it is overspent. A ramp, not a switch.'],
    ['Hidalgo’s corollary to Hyrum’s law', 'The reliability you actually deliver is an observable behaviour, so users come to depend on it, even when it is better than your SLO.'],
    ['CUJ hierarchy, top to bottom', 'Goal (not instrumentable), tasks, critical user interactions, instrumentation (server, client, end-to-end SLIs), SLOs.'],
    ['What is a “bad minute”?', 'A way to roll several SLIs into one journey SLO: the minute counts as bad if any SLI in the journey was bad during it.'],
    ['Two drop policies for client telemetry, and the cost of each', 'Drop the oldest and you lose the trigger of the problem. Drop the newest and you lose the present. Either way, report how much was dropped and why.'],
    ['Rasmussen’s three boundaries', 'Economic failure, unacceptable workload, and acceptable performance. Cost pressure and least effort push the operating point towards the third.'],
    ['Four parts of an STPA control loop', 'Controller (with a mental model), control action going down, feedback coming up, controlled process.'],
    ['What does RTO include?', 'It is cumulative: time to detect, time to act and time to restore, counted from the incident.'],
    ['Incremental vs differential backup', 'Incremental stores changes since the last backup of any kind: small, but restore needs the whole chain. Differential stores changes since the last full: larger, faster restore.'],
    ['The effectiveness zone', 'Match guardrail strength to consequence. Strong control on minor risk is restrictive; weak control on catastrophic risk relies on humans never slipping.'],
    ['Platform typology, 0 to 4', 'YOLO, ad hoc, guided, engineered, assured. Shift down means moving a practice from guided to engineered or assured.'],
    ['The Google Meet capacity loop', 'Daily: do we have enough for the load expected a week from now? If not, four workstreams (capacity, dependencies, bottlenecks, control knobs) feed one safe-deploy stream.'],
    ['Rollout rule of thumb from chapter 14', 'Start at 0.1% of traffic and grow about ten-fold every 24 hours, ramping fast at the low end and slowly at the high end.'],
    ['Two layers of agent security', 'Runtime policy enforcement outside the model (dependable) and reasoning-based defences inside it (flexible, probabilistic), kept honest by regression tests and red teams.'],
    ['How is an investigation agent evaluated?', 'LLM as judge against labelled incidents: pass or fail on diagnosis and on mitigation, plus the failure mode, the failing step and a critique.'],
]

# chapter -> extra quiz question (also added to the big quiz)
NEWQUIZ = {
    8: ['A team has run at 99.99% for a year against a 99.9% SLO. What does Hidalgo’s corollary predict?', ['Nothing: only the SLO matters', 'Users now depend on 99.99%, so a drop to the SLO will feel like an outage', 'The SLO should be removed', 'The error budget doubles'], 1, 'The level you deliver is an observable behaviour, and people build on what they observe. Check in with consumers, or burn budget on purpose.'],
    9: ['Every server metric is green, but users searching for “coffee” get zero results. Which practice catches this?', ['A lower latency threshold', 'An SLO defined on the user journey, with an invariant such as “the customer sees non-zero, valid results”', 'More CPU alarms', 'A longer retention period'], 1, 'The Maps case. The server “successfully” returned empty answers, so only a customer-centric signal could see it.'],
    11: ['In Rasmussen’s model, why does a system drift towards the accident boundary?', ['Engineers are careless', 'Cost pressure and the pull towards least effort both push away from the other two boundaries', 'Monitoring is missing', 'Hardware ages'], 1, 'Each shortcut is a rational response to pressure, and each one that doesn’t fail looks like proof it was safe.'],
    12: ['Reviewers sampled four states and the errors were in six other states. What would CAST ask that a classic postmortem might not?', ['Who chose the sample?', 'Why did a four-state sample seem sufficient, and what feedback would have shown it was not?', 'How many cities were wrong?', 'When was the rollback?'], 1, 'CAST looks for why the decision made sense at the time and how the control structure allowed it.'],
    16: ['Detection took 3 hours, the decision took 1 hour, and the restore took 4. What was the achieved recovery time?', ['4 hours', '5 hours', '8 hours', '3 hours'], 2, 'RTO is cumulative: detect, act and restore. Slow detection spends recovery time before the restore begins.'],
    18: ['A hard block is placed on a mistake whose worst outcome is a cosmetic glitch. Where does this sit on the effectiveness chart?', ['In the effective zone', 'Too restrictive: it costs velocity and goodwill', 'Too little control', 'It depends on the team'], 1, 'Strength of control should match severity. Heavy controls on minor risks teach people to work around the platform.'],
    21: ['An agent proposes a low-risk action. In the book’s safety loop, what happens next?', ['It waits for human approval', 'It runs through an atomic executor that validates the result and rolls back on failure', 'It is logged and dropped', 'It retrains the model'], 1, 'Risk assessment routes high-risk actions to people and low-risk ones to an executor that can undo them.'],
}

NEWDRILLS = [
    ['Your server-side SLOs are all green, and support tickets say the product is broken. Walk me through what you do.',
     '<p>I treat the tickets as the truth and the dashboards as incomplete. Server SLOs measure what the server saw, and a lot can fail outside that: DNS, certificates, a client release, or a response that is well-formed and wrong.</p>'
     '<p>In the moment I look for a user-side signal: client telemetry if we have it, synthetic probes of the journey, support volume by build and region. I check recent changes across all five vectors, not only server deploys: config, app releases, feature ramps and data pushes.</p>'
     '<p>Afterwards I define the journey properly. The goal can’t be instrumented, so I break it into tasks and critical interactions, add client and end-to-end SLIs, and write an invariant from the user’s side, like the Maps team’s “the customer sees non-zero, valid results”. Then I wire that signal into rollout supervision so a canary that breaks it pauses itself.</p>'
     '<p>I’d warn leadership that better detection will look like more incidents for a while. On AWS I would use CloudWatch RUM and Synthetics for the client and journey view, and Application Signals for the SLOs.</p>'],
    ['Draw RPO, RTO and RWO on a timeline and tell me where teams usually get them wrong.',
     '<p>I draw a line with backups along it, then the incident, then detection, action and full restoration. RWO runs from the oldest backup I still keep to the latest. RPO runs from the latest good backup to the incident: that is the data I lose. RTO runs from the incident to full restoration.</p>'
     '<p>The first mistake is treating RTO as restore time only. It is cumulative, so three hours to notice plus an hour to decide have already spent four hours before the restore starts. The second is an RWO shorter than the time it takes to notice silent corruption, which makes the data unrecoverable however good the backups are. The third is setting all three from what the current storage can do instead of asking the business first.</p>'
     '<p>Then I say how I would prove the numbers: automated restore tests that measure the real restore time, and a fleet-level SLO such as “backups for 99% of data sources are within RPO 99% of the time”. On AWS that is AWS Backup with restore testing, point-in-time recovery for bad writes, and Vault Lock so an operator mistake can’t delete the backups.</p>'],
]
