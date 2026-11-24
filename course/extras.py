# Hand-written lesson furniture: titles, learning goals, diagrams, exercises, takeaways.

def flow(items, note=None):
    out = ['<div class="flow">']
    for i, it in enumerate(items):
        t, s = it[0], it[1]
        c = f' style="--c:var(--{it[2]})"' if len(it) > 2 else ''
        if i:
            out.append('<div class="arr" aria-hidden="true">→</div>')
        out.append(f'<div class="box"{c}><b>{t}</b><span>{s}</span></div>')
    out.append('</div>')
    if note:
        out.append(f'<p class="loopnote">{note}</p>')
    return ''.join(out)


def tiles(items):
    return '<div class="tiles">' + ''.join(
        f'<div class="tile"' + (f' style="--c:var(--{it[2]})"' if len(it) > 2 else '') + f'><b>{it[0]}</b><span>{it[1]}</span></div>'
        for it in items) + '</div>'


def table(head, rows, cls=''):
    return (f'<div class="scroll"><table class="{cls}"><thead><tr>' + ''.join(f'<th>{h}</th>' for h in head) + '</tr></thead><tbody>'
            + ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows) + '</tbody></table></div>')


def seq(rows):
    return '<ol class="seq">' + ''.join(f'<li><span class="who">{a}</span><span>{b}</span></li>' for a, b in rows) + '</ol>'


PARTS = {
    1: ('SRE in context', 'green'),
    2: ('Sociotechnical foundations', 'red'),
    3: ('Awareness and preparedness', 'blue'),
    4: ('Infrastructure design', 'orange'),
    5: ('Resilient products', 'purple'),
    6: ('Outlook', 'teal'),
    7: ('Practice', 'inkline'),
}
PART_OF = {**{n: 1 for n in (1, 2, 3)}, **{n: 2 for n in (4, 5, 6, 7)}, **{n: 3 for n in (8, 9, 10, 11, 12)},
           **{n: 4 for n in (13, 14, 15, 16)}, **{n: 5 for n in (17, 18)}, **{n: 6 for n in (19, 20, 21, 22, 23)}}

# quick-check questions that did not exist in the big quiz
NEWQ = {
    1: ['In the hierarchy of production health, what sits at the base?', ['Monitoring and alerting', 'Sociotechnical foundations: culture, people and how they work together', 'Capacity planning', 'Emergent reliability'], 1, 'Culture and people come first. Emergent reliability, where the platform makes systems reliable by default, is the top.'],
    2: ['What does “sublinear scaling” mean for an SRE team?', ['Headcount grows faster than the service', 'Operating cost and effort grow more slowly than the service does', 'The service is scaled down at night', 'Every new service needs a new SRE'], 1, 'Automation and shared platforms let the same team run far more, which is the core of the business case.'],
    3: ['A cloud-hosted service starts failing. What does the book say is the first question?', ['Who deployed last?', 'Is it us or the provider?', 'What is the RTO?', 'Can we add capacity?'], 1, 'You share state with your provider, so you first work out whose side the fault is on, using account-specific health dashboards and integrated telemetry.'],
    5: ['In Google’s hiring experience, which predicts SRE success better?', ['Depth in one technical field', 'Breadth of technical knowledge and experience', 'A computer science degree', 'A previous SRE job title'], 1, 'Breadth beats depth, which is why committees look for strengths rather than gaps. Most Google SRE hires have no previous SRE experience.'],
    23: ['Why does the book call availability a trailing indicator?', ['It is hard to measure', 'It only moves after something has already gone wrong', 'It ignores latency', 'It is averaged over 30 days'], 1, 'Availability shows risk that has already turned into failure. Cataloguing risks from postmortems, STPA and design reviews gives you leading indicators.'],
}
# chapter -> indexes into the existing 38-question quiz (at most two are shown inline)
QUIZ_OF = {4: [19], 6: [22, 34], 7: [20, 21], 8: [0, 1], 9: [3, 15], 10: [5, 6], 11: [23, 24], 12: [7, 25], 13: [9, 32],
           14: [10, 11], 15: [12], 16: [4, 28], 17: [13, 31], 18: [16], 19: [33], 20: [18, 27], 21: [17], 22: [37]}

L = {}

L[1] = dict(
    nav='What SRE is', h1='What SRE is, and the model behind it', poc='',
    learn=['what each word in “Site Reliability Engineering” commits you to', 'the hierarchy of production health and why it replaced the old pyramid', 'a crisp answer to “how is SRE different from DevOps?”'],
    top=flow([('1 · Sociotechnical foundations', 'Culture, people, how teams work'), ('2 · Situational awareness', 'SLOs and observability'), ('3 · Continuous preparedness', 'Incidents, learning, safety analysis'),
              ('4 · Infrastructure design', 'Automation, testing, capacity, data'), ('5 · Resilient products', 'Reliability designed in'), ('6 · Emergent reliability', 'Reliable by default')],
             'The hierarchy of production health, base first. Grow it wider and taller together: don’t build the top before the base can hold it.'),
    turn='Pick a project you finished recently and run the three-part test on it. Did it help the business? Did it improve reliability? Did it use an engineering approach rather than heroics? Write one sentence for each.',
    take=['SRE treats operations as a software problem, with reliability as the one thing it owns.', 'The hierarchy of production health starts with culture and ends with platforms that make systems reliable by default.', 'The 50% toil ceiling is a limit, not a target. Good teams sit far below it.'])

L[2] = dict(
    nav='The value of reliability', h1='The value of reliability', poc='',
    learn=['how to present SRE as an investment with a return', 'what each stakeholder gets from it', 'the full cost of unreliability, beyond lost sales'],
    top=tiles([('Customers', 'Reliability is the feature every other feature depends on. Not 100%, though: that is always the wrong target.'),
               ('The CFO', 'Software leverage. Code runs again and again at almost no extra cost, and shared platforms spread the gain.'),
               ('Product teams', 'Objective targets and less cognitive load.'),
               ('The SRE team', 'Protection from burnout, including the right to hand a pager back.')]),
    turn='Estimate what one hour of downtime costs for a service you know: lost revenue, engineer-hours for the response and the reviews afterwards, SLA credits, and churn. Which number surprised you?',
    take=['The headline benefit is sublinear scaling: cost grows more slowly than the service.', 'The error budget turns stability versus velocity into a deliberate, shared trade.', 'Unreliability costs far more than lost sales, and systems atrophy without investment.'])

L[3] = dict(
    nav='Trends in production', h1='Trends in production: what the cloud changed', poc='',
    learn=['why capacity planning became financial engineering', 'the three decouplings behind modern architecture', 'why RTO and RPO alone can’t describe reliability'],
    top=flow([('Compute from location', 'Orchestrators place workloads; VMs stop being pets'), ('Storage from compute', 'Warehouses and query engines over object storage'), ('Network from hardware', 'Defined by software and identity')],
             'Three decouplings. Platforms followed the same path: from tickets, to self-service golden paths, towards intent-based systems where you declare a target and the platform reconciles it.'),
    turn='List the managed services one of your systems depends on. For each, where would you look to answer “is it us or the provider?” within two minutes?',
    take=['The cloud swapped physical limits for financial and logical ones (FinOps).', 'Treat providers as partners and their SLA as a floor, not a promise about your service.', 'RTO and RPO see the world as up or down. SLOs capture the partial failures that are far more common.'])

L[4] = dict(
    nav='Culture', h1='The cultural context of SRE', poc='',
    learn=['the two foundations and seven elements of a reliability culture', 'blame awareness, just culture and Westrum’s three culture types', 'how to change culture through behaviour, in brownfield and greenfield'],
    top=flow([('Learning', 'Training builds skill'), ('Confidence', 'People believe they can do it'), ('Behaviour', 'They do it, repeatedly'), ('Culture', 'It becomes how things are done')],
             'You change culture by changing what people do. Their thinking follows.'),
    after={'DORA and Westrum': table(['', 'Pathological', 'Bureaucratic', 'Generative'],
                                     [['Messengers are', 'punished', 'neglected', 'trained'], ['Failure leads to', 'scapegoating', 'justice', 'inquiry'],
                                      ['New ideas are', 'crushed', 'a source of problems', 'implemented'], ['Responsibilities are', 'shirked', 'narrow', 'shared risks'],
                                      ['Bridging between teams is', 'discouraged', 'tolerated', 'encouraged']])},
    turn='Rate yourself on the grounded scale (no idea, with help, from docs, from memory, could teach it) for “explain the benefits of a blameless postmortem culture”. Then rewrite this question without judgement: “Why did you think it was OK to deploy on a Friday?”',
    take=['Two foundations: focus on the user, and reliability as a core value. Seven elements sit on top.', 'Blameless is not accountability-free. Just culture reserves discipline for reckless or criminal acts.', 'Learning builds confidence, confidence changes behaviour, and repeated behaviour becomes culture.'])

L[5] = dict(
    nav='Hiring and careers', h1='Hiring, training and career management', poc='',
    learn=['what Google looks for when hiring SREs, and the two hiring profiles', 'how to design onboarding that gets people on call with confidence', 'the three keys to an SRE career, and why retention matters so much'],
    top=flow([('Checklist and starter project', 'Learn the systems with a mentor'), ('Breakage labs', 'Fix simulated outages in a private stack'), ('Shadow', 'Watch a real on-call shift'), ('Reverse shadow', 'Hold the pager with a mentor watching'), ('On-call', 'With confidence')],
             'An onboarding ramp built from the chapter’s methods.'),
    after={'Two hiring profiles': table(['', 'SRE-SWE', 'SRE-SE'], [['Background', 'Software development', 'Systems engineering'], ['Interview focus', 'Data structures, algorithms, API design', 'Non-abstract large system design with real numbers'], ['Day job', 'The same duties', 'The same duties']])},
    turn='Give a whiteboard talk to yourself: draw one system you support from memory, name each component’s purpose and trace one critical request through it. Where did you get stuck? That is your on-call learning checklist.',
    take=['Breadth predicts SRE success better than depth, so hire for strengths.', 'Training should build confidence through practice, and can be run like a production service.', 'Careers grow along breadth, initiative and teamwork. On-call is the top reason people leave, so make it flexible.'])

L[6] = dict(
    nav='Org structures', h1='Organisational structures for SRE', poc='',
    learn=['the trade-offs between centralised, decentralised and hybrid SRE', 'the team-size and on-call numbers Google uses', 'the five maturity phases, and how to use scorecards without harm'],
    top=table(['', 'Centralised', 'Decentralised'],
              [['Strength', 'Concentrated expertise, consistent practice', 'Deep product context, fast feedback, real ownership'],
               ['Risk', 'A transactional “IT services” mindset, slow onboarding', 'Us-versus-them, or the role being quietly dropped'],
               ['Fits', 'Low-trust, high-control organisations starting out', 'High-trust organisations with strong product teams']]),
    after={'Maturity matrix': flow([('Absent', 'Only features count'), ('Reactive', 'Fixing the latest outage'), ('Proactive', 'Joint risk reviews. The floor for critical services'), ('Strategic', 'Classes of risk designed out. 4+ years'), ('Visionary', 'Self-healing. Rare')])},
    turn='Write this week’s production-meeting agenda for your team using the five headings: outages and pages, postmortems, SLOs and trends, non-paging alerts and tickets, upcoming changes. What had no owner?',
    take=['Most organisations end up hybrid: central standards and community, with dedicated teams for critical products.', 'Limits to remember: at least 50% engineering, at most 25% on-call, six engineers per site across two sites or eight at one.', 'Scorecards are proxies. Use them to coach, never to rank.'])

L[7] = dict(
    nav='Engagement models', h1='SRE engagement models', poc='',
    learn=['the difference between an org structure and an engagement model', 'the scoping archetypes, and how consumer and enterprise SRE differ', 'why Google moved from launch reviews, to tiers, to outcomes'],
    top=flow([('1 · PRR gate', 'Supported or not. Thorough, but sticky and late'), ('2 · Tiers', 'Baseline, assisted, full. Still about who holds the pager'), ('3 · Outcomes (2025)', 'Foundational offerings for all, plus time-boxed engineering efforts')],
             'How Google’s engagement model evolved.'),
    after={'Consumer vs enterprise': table(['', 'Consumer', 'Enterprise'],
                                           [['Buyer', 'The user', 'A CTO or committee, under contract'], ['What you lean on', 'Metrics, SLOs, error budgets', 'Relationships and customer-specific context'],
                                            ['Extra detection signal', 'Sentiment from search and social', 'Support cases'], ['Incident stance', 'Mitigate first', 'Communicate first, mitigate second'],
                                            ['Design', 'Sharding and graceful degradation, hidden from users', 'Customer-facing failure domains, isolation of large customers']])},
    turn='Describe your current team as one of the archetypes (kitchen sink, embedded, product, infrastructure, tools, consulting, blended). Then write two foundational offerings and two time-boxed outcomes you would propose instead of “SRE holds the pager”.',
    take=['The engagement model is the contract of work, separate from who reports to whom.', 'Building an engagement around on-call is an antipattern. On-call exists to inform engineering.', 'Consumer SRE mitigates first. Enterprise SRE communicates first.'])

L[8] = dict(nav='SLOs and error budgets', h1='SLOs, error budgets and burn rate', poc='POC 01',
            learn=['the vocabulary: SLI, SLO, SLA, error budget, burn rate, CUJ', 'the numbers to know cold, and how to derive them on a whiteboard', 'how to alert on burn rate, including for low-traffic services', 'what the second edition adds, and where SLOs fall short'],
            turn='Open <code>poc-01-slo-error-budget</code> in the repo. Before running the tests, work out by hand the burn-rate thresholds for a 99.95% SLO, then check them against <code>slo/alerting.py</code>. Finish in the Labs station: slide the 5-minute error rate to zero and explain why the page clears.',
            take=['An SLI is good events over valid events. The SLO is the target, and the error budget is what’s left over.', '99.9% over 30 days is 43.2 minutes. Page at 14.4× burn, confirmed by a short window.', 'The target is a business decision made by a cross-functional group, written down with an error budget policy.'])

L[9] = dict(nav='Observability', h1='Observability and monitoring', poc='POC 02',
            learn=['the difference between monitoring and observability', 'Google’s three strategies for observability at microservice scale', 'why alerting telemetry and analytics telemetry are separate systems', 'how OpenTelemetry correlates signals'],
            turn='Run <code>poc-02-observability-otel</code> locally with Docker Compose. Send a few requests, then find one request’s trace ID in the JSON logs and follow it. Which three things let you join the log line, the metric and the trace?<details><summary>Show the answer</summary><p>1. The <b>trace ID</b> (and span ID), written into the log line, so a log entry points at exactly one request’s trace. 2. The same <b>resource attributes</b> on all three signals: service name, version, environment, region. They tell you which service and deployment produced each one. 3. The <b>time</b>: a metric is an aggregate with no trace ID, so you join it to traces and logs through the same service tags and the same time window. Metrics can also carry exemplars, sample trace IDs attached to a data point, which link a spike straight to example requests.</p></details>',
            take=['Observability lets someone without tribal knowledge test and reject hypotheses quickly.', 'The metric that matters most is time to mitigate.', 'Keep the alerting path fast and simple, the analytics path complete and cheap, and one SDK in front of both.'])

L[10] = dict(
    nav='Incidents and on-call', h1='Incident management and on-call', poc='POC 03',
    learn=['the IMAG roles and how an incident moves through its lifecycle', 'why you mitigate before you understand, and the five generic mitigations', 'how to design on-call that people can sustain', 'what to measure instead of MTTR'],
    top=tiles([('Incident Commander', 'Holds every role until they delegate it. Directs, and in big incidents takes no hands-on tasks.', 'red'),
               ('Communications Lead', 'Keeps stakeholders and customers informed on a fixed cadence. May split into internal and external.', 'blue'),
               ('Operations Lead', 'Runs the hands-on response: investigating and applying mitigations.', 'green')]),
    after={'Triage and mitigation': flow([('Drain', 'Move traffic away'), ('Roll back', 'Undo the last change'), ('Upsize', 'Add capacity'), ('Degrade', 'Shed features or quality'), ('Block', 'Stop the bad input')],
                                         'The five generic mitigations. None of them needs a root cause.')},
    turn='Open <code>poc-03-incident-management/playbooks/slo-burn.md</code> and role-play it aloud as Incident Commander for a checkout outage: declare, assign roles, pick the first mitigation and give two status updates. Time yourself.',
    take=['Clear roles first. The Incident Commander directs and delegates.', 'Mitigate before you understand: drain, roll back, upsize, degrade or block.', 'Risk tolerance for a mitigation scales with impact, and a reasonable mitigation that fails is never blameworthy.'])

L[11] = dict(
    nav='Learning from incidents', h1='Learning from incidents', poc='POC 03',
    learn=['what a good postmortem contains and who should write it', 'the safety-science models interviewers expect you to know', 'the Paris data centre outage, start to finish, and what it changed'],
    after={'Case study: Paris, April 2023': seq([('16:46', 'A cooling pipe starts leaking above one zone.'), ('17:25', 'First automated alert. Engineers respond within minutes.'), ('18:30', 'VMs in the affected cluster are brought down in a controlled way.'),
                                                 ('19:17', 'A product communications lead is paged in. Updates get specific.'), ('20:00', 'The fire brigade takes command of a battery-room fire.'),
                                                 ('23:04', 'Power is cut to one building. A regional database loses quorum, and a design flaw spreads that to some global APIs.'),
                                                 ('23:46', 'A known mitigation has failed. Three new ones are built in parallel.'), ('03:38', 'The first new mitigation works. Impact is regional again.'),
                                                 ('19:00', 'Next day: control plane restored across the region.')])},
    turn='Take an incident you were part of and add the two sections most postmortems lack: what went right, and where you got lucky. Then use <code>poc-03-incident-management/templates/postmortem-cast.md</code> to restate one “human error” as a question about the system.',
    take=['An independent lead, several contributing factors, and what went right as well as what went wrong.', 'Know one line each on Swiss cheese, Rasmussen, Safety-II, Cook, Woods and STAMP.', 'Paris led to product-level incident commanders and auto-paged comms leads, and the next similar outage took about half the time.'])

L[12] = dict(
    nav='STPA and CAST', h1='Safety engineering with STPA and CAST', poc='POC 03',
    learn=['why “no component failed” outages need a different model', 'the four steps of STPA and the parts of a control loop', 'how CAST analyses an incident without blame', 'how to get a team to try it'],
    top=flow([('1 · Losses and hazards', 'What must never happen, and the states that lead there'), ('2 · Control structure', 'Who controls what, and what feedback they get'), ('3 · Unsafe control actions', 'Missing, wrong, mistimed, or too long or short'), ('4 · Causal scenarios', 'Why a controller would do that')],
             'STPA looks forward at a design. CAST uses the same model to look back at an incident.'),
    after={'Maps in Japan': table(['', 'Postmortem', 'Systems analysis'], [['Maps in Japan (STPA)', '7 recommendations', '56 causal scenarios, 34 recommendations'], ['Misnamed cities (CAST)', '3 people, 16 hours, 8 recommendations', '5 people, 81 hours, 22 recommendations']])},
    turn='Fill in <code>poc-03-incident-management/templates/stpa-worksheet.md</code> for a deploy pipeline you know. Name one controller, its control actions and its feedback, then write one unsafe control action of each of the four types.',
    take=['Safety is an emergent property of the whole system. You can’t read it from one component.', 'Model functional controllers, their process models and their feedback.', 'Blame is the enemy of safety. Ask why the action made sense, then fix the system.'])

L[13] = dict(
    nav='Automation and toil', h1='Automation, tooling and toil', poc='POC 09',
    learn=['the four reasons to automate and the levels of automation', 'the ironies and pitfalls of automation', 'how to decide what to automate, and how to do it incrementally', 'what toil is, when it is acceptable, and what doesn’t fix it'],
    top=flow([('Detect and alert', 'The automation only tells humans'), ('Suggest', 'It proposes an action; a human does it'), ('Act and notify', 'It acts and reports what it did')],
             'The safety ladder for new automation. Move up one rung at a time, and the whole team can follow along.'),
    turn='Run <code>poc-09-toil-automation/toil_report.py</code> against the sample tickets. Which class of toil would you automate first if you prioritised the fastest win instead of the biggest return? Why might that be the better choice?',
    take=['Automate for emergencies, consistency and scale, not only to save time.', 'Automation creates new work and erodes skills, so keep it observable, limited and reversible.', 'Toil is defined by its properties. Fix whole classes of it, and keep engineering above 50%.'])

L[14] = dict(
    nav='Testing', h1='Testing for reliability', poc='POC 05, 06',
    learn=['why configuration needs the same testing discipline as code', 'the VOIS properties and the layers of config tests', 'what canaries, DiRT and fault injection each prove', 'where formal methods and agent testing fit'],
    top=tiles([('Versioned', 'There is always a known version to roll back to.'), ('Observable', 'You can tell whether a change is live.'), ('Independent', 'Config can change, and soft-launch, separately from code.'), ('Safe', 'There is an explicit safe default for emergencies.')]),
    after={'Configuration is the sharpest edge': flow([('Syntax', 'Does it parse? Kept even for emergency pushes'), ('Semantic', 'Zeroed values, 300× jumps, new ports'), ('Dynamic', 'Dry runs and hermetic launches with probes'), ('Canary', 'Compare new against old in production')])},
    turn='Read <code>poc-05-progressive-delivery/canary_analysis.py</code> and predict its verdict for a canary that saw 20 requests and no errors. Then open <code>poc-06-chaos-fis</code> and write one test as “X is resilient to Y, measured by Z”.',
    take=['Testing measures how wrong your mental model is.', 'Config must be versioned, observable, independent and safe, and checked in layers.', 'A canary is an A/B comparison and the first integration test of production config with new code.'])

L[15] = dict(
    nav='Capacity planning', h1='Capacity planning', poc='POC 07',
    learn=['when capacity planning is worth doing at all', 'the three kinds of demand and how to forecast each', 'how traffic tags, failure domains and pooling change the sums', 'the Google Meet and AI-era case studies'],
    top=tiles([('Organic', 'Steady growth. Forecast it from trends.', 'green'), ('Planned inorganic', 'Launches, Black Friday, the Olympics. Plan it with the launch.', 'orange'), ('Unplanned inorganic', 'Going viral. Handle it with buffers, autoscaling and demand shaping.', 'red')]),
    after={'Peak of sums and Flex': tiles([('Sum of peaks: 60 units', 'Each service provisioned separately for its own peak.'), ('Peak of sums: 48 units', 'One pool sized for the combined peak. Same demand, 20% less capacity.')])},
    turn='Run <code>poc-07-capacity-planning/capacity.py</code>. Then work this by hand: peak 9,000 QPS, 100 QPS per instance, 70% target utilisation, three zones, survive the loss of one. How many instances in total? (The quiz has the answer.)',
    take=['Planning for every edge case is like targeting 100%. Choose your risk.', 'Latency and availability needs belong to traffic, not to services. Tag requests and shed by criticality.', 'Pooling works because peaks rarely coincide, but pooled services must survive a stockout.'])

L[16] = dict(
    nav='Data management', h1='Data management', poc='POC 08',
    learn=['the legal and ethical constraints that come before any design', 'the hierarchy of data needs', 'RPO, RTO and RWO, and what each mechanism does and doesn’t protect', 'how to plan, test and govern backups and recovery'],
    top=flow([('1 · Integrity', 'What you read is what you wrote'), ('2 · Security', 'You, and only you'), ('3 · Availability', 'There when you need it'), ('4 · Efficiency', 'At a cost you can sustain')],
             'The hierarchy of data needs. Each layer rests on the one before.'),
    after={'RPO, RTO, RWO': tiles([('RPO', 'Recovery point: how much recent data you can afford to lose.'), ('RTO', 'Restore time: how long until it’s back. The clock starts at the incident, so it includes time to detect, time to act and time to restore.'), ('RWO', 'Restore window: how far back in time you can go.')]),
           'Backups': table(['Mechanism', 'Good for', 'Blind spot'],
                            [['Replication', 'Hardware, zone and region loss', 'Copies corruption and deletes everywhere'], ['Snapshot', 'A fast rollback before a risky change', 'Shares fate with the live data'],
                             ['Backup', 'Almost everything, including storage bugs', 'Slow and costly; loses changes since the last run'], ['Point-in-time recovery', 'Bad writes, with a tiny RPO', 'Storing every write; slow replay']])},
    turn='Run <code>poc-08-data-resilience/backup_slo.py</code> on the sample recovery points. Then pick one datastore you own and write its RPO, RTO and RWO in one line each. Who in the business agreed to those numbers?',
    take=['Law and ethics first, then integrity, security, availability, efficiency.', 'Replication is not a backup. Set RPO, RTO and RWO first and let them drive the design.', 'A backup you haven’t restored is a hope. Test restores automatically and validate the data.'])

L[17] = dict(
    nav='Designing for resilience', h1='Designing for resilience', poc='POC 04',
    learn=['how reliability and resilience differ, and how to prioritise rare risks', 'the rules for safe change, dependencies and failure domains', 'how to survive overload and bad input', 'incident modes and the response journeys to practise'],
    top=tiles([('Normal', 'Rich tools, many dependencies, used by everyone.', 'green'), ('Emergency', 'Low-dependency fallbacks with the same interfaces. Most responders, little training. Invest here first.', 'orange'), ('Disaster', 'Zero-dependency command-line tools and direct access, for small trained teams.', 'red')]),
    turn='Run <code>poc-04-resilience-patterns/simulate_cascade.py</code>. The naive client never recovers after the spike; the protected one does. Remove one protection at a time (jittered backoff, retry budget, shedding) and see which one matters most.',
    take=['A complex plan might work. Resilience has to work every time, so enforce it through the platform.', 'Sized for X and receiving 10X, serve about X and recover without humans.', 'Practise the emergency mode: fallbacks for comms, access, docs and reaching people.'])

L[18] = dict(
    nav='Platform engineering', h1='Platform engineering in SRE', poc='POC 10',
    learn=['what a platform is, and why curated solutions beat requirements alone', 'golden paths, guardrails, exceptions and incentives', 'shifting down, legibility, and handling brownfield systems'],
    top=flow([('Golden path', 'The easy, supported route'), ('Hint', 'A nudge in the editor'), ('Warning', 'Flagged, but allowed'), ('Error', 'Blocked, with a break-glass path')],
             'Guardrails from gentle to firm. Use the gentlest one that achieves the goal.'),
    after={'Shift down, effectiveness zones, frameworks': tiles([('Shift left', 'Deal with reliability earlier in the lifecycle. Every team needs the expertise.'), ('Shift down', 'Build it into the platform once. Every team gets it by default.')])},
    turn='Run <code>poc-10-platform-policy/policy_check.py</code> against the example catalogue. Add an exemption with an expiry date and a reason for one failing service, then decide which of the four convergence options you would apply to it.',
    take=['A good platform makes the reliable way the easy way.', 'Golden paths over mandates: change the game so the good outcome is the rational one.', 'Block new violations, exempt old ones explicitly with an expiry, and make the remaining risk visible.'])

L[19] = dict(
    nav='The tipping point', h1='SRE at the tipping point', poc='',
    learn=['what changes when writing code becomes nearly free', 'the chapter’s predictions for rollouts, debugging and incidents', 'what “strategic incoherence” means and how to counter it'],
    top=flow([('Plan', ''), ('Analyse', ''), ('Design', ''), ('Build', ''), ('Test', ''), ('Deploy', 'The hard boundary stays'), ('Maintain', '')],
             'The phases stay, but AI compresses and blends the ones before deployment. Production doesn’t care how the code was written.'),
    turn='Take a feature you shipped with AI help. Write the three-line specification you wish had existed first: the invariant it must keep, how you would know in production that it broke, and how you would undo it.',
    take=['Faster delivery without other changes means proportionally more incidents.', 'Agents generate technical debt tirelessly unless specifications keep the design coherent.', 'Humans stay the understanders of last resort, so keep skills sharp.'])

L[20] = dict(
    nav='SRE for AI systems', h1='How SRE supports AI', poc='',
    learn=['the four SLO pillars for AI systems, with quality as the new one', 'how models and accelerators are qualified for production', 'the six losses that explain idle accelerators', 'power as a first-class constraint, and the new security risks'],
    top=tiles([('Availability', 'Hardware, the training control plane, attestation.'), ('Throughput', 'ML goodput: the share of allocated time doing useful work.'), ('Latency', 'Time to first token, scheduling delay, data staleness.'), ('Quality', 'Is the answer right? The defining pillar for AI.', 'red')]),
    after={'Power': flow([('Throttle accelerators', 'Takes milliseconds, easy to undo'), ('Terminate tasks', 'By priority band, if it lasts past about 5 s'), ('Shut machines down', 'The only way to remove idle draw')], 'Shedding power before a breaker trips.')},
    turn='Write SLOs for an LLM chat feature: one per pillar. What is your quality SLI, how is it sampled, and does a fallback to a smaller model count as good, degraded or bad?',
    take=['A successful response with a wrong answer is still a failure, so quality needs an SLO.', 'Qualify hardware, models and prompts continuously, and canary all three.', 'Accelerators are scarce. Explain idle capacity with the six losses before buying more.'])

L[21] = dict(
    nav='AI for SRE', h1='How AI supports SRE', poc='POC 11',
    learn=['the safety architecture for agents with production access', 'how AI finds outages that metrics miss', 'the five levels of autonomy, with a real example at each', 'where the real value lies beyond toil reduction'],
    top=table(['Level', 'Monitor', 'Investigate', 'Approve', 'Actuate', 'Self-direct'],
              [['L0 Manual', 'Auto', 'Human', 'Human', 'Human', 'Human'], ['L1 Assisted', 'Auto', 'Auto', 'Human', 'Human', 'Human'], ['L2 Partial', 'Auto', 'Auto', 'Human', 'Auto', 'Human'],
               ['L3 High', 'Auto', 'Auto', 'Auto', 'Auto', 'Human'], ['L4 Full', 'Auto', 'Auto', 'Auto', 'Auto', 'Auto']], cls='auto'),
    after={'Situational awareness: Detectr': flow([('Augment', 'Attach system state'), ('Filter', 'LLM drops irrelevant posts'), ('Cluster', 'Embeddings, then an LLM'), ('Report', 'A structured outage report'), ('Notify', 'Email, ticket or page')])},
    turn='Run the tests in <code>poc-11-ai-ops-guardrails</code> and read <code>agent_guardrails.py</code>. Which checks stop an agent at L2 from acting alone? Add one action you would never allow above L2, and say why.',
    take=['Trust is earned: read-only, then proposing, then acting on narrow, reversible tasks.', 'An agent may only do what it knows how to undo, as one validated transaction.', 'Not every system should reach full autonomy. Match the level to the risk.'])

L[22] = dict(
    nav='Diverse environments', h1='SRE in diverse environments', poc='',
    learn=['what to do first as the only SRE at a company', 'how to apply SRE with legacy systems, silos and regulation', 'lessons from a startup, a bank, a lender and Waymo', 'how SRE skills carry over to security and privacy'],
    top=flow([('P0 · Stop the bleeding', 'Fix the outage that keeps repeating', 'red'), ('P1 · Visibility', 'Metrics, symptom alerts, structured logs', 'orange'), ('P2 · Automate the scariest task', 'Usually deploys. Rollback first', 'blue'), ('P3 · Self-service', 'Tools and docs so developers don’t need you', 'green')],
             'The solo SRE’s priority stack.'),
    turn='You join a 20-person startup tomorrow as its first SRE. Write your priority stack with one concrete target and date for each level, and the four questions your first dashboard will answer.',
    take=['Alone, prioritise ruthlessly: stop the bleeding, see, make deploys safe, enable developers.', 'With closed or legacy systems, stabilise what surrounds them and standardise the layer above.', 'Adapt the principles to your constraints. Don’t try to copy Google.'])

L[23] = dict(
    nav='Future and appendices', h1='The future of SRE, and the appendices', poc='',
    learn=['what the book expects to stay the same', 'the three shifts under way: shift down, risk as a leading indicator, agentic operations', 'what each appendix is for'],
    top=flow([('Trailing', 'Availability: tells you after it broke'), ('Leading', 'Catalogued risk: tells you what could break')], 'From measuring failure to measuring risk.'),
    turn='Take your most recent postmortem and list the risks it revealed, not just the action items. Group them. Is there one class of risk a platform change could remove for everyone?',
    take=['Reliability matters more each year, and humans stay in the loop for novel problems.', 'Shift down: put reliability into platforms so it’s the default.', 'Treat risk as the leading indicator, and use AI to find and remove whole classes of it.'])

# ---------------------------------------------------------------- hand-written lessons
CH8 = '''
<h2>Four terms, each built on the last</h2>
''' + flow([('SLI', 'An indicator: good events ÷ valid events'), ('SLO', 'An objective: a target for that ratio over a window'), ('Error budget', '1 − SLO: the failure you are allowed'), ('Burn rate', 'How fast you spend it. At 1× it lasts exactly the window')]) + '''
<p>An <b>SLA</b> is different. It is the agreement about what happens, usually money, when a target is missed, and it is normally looser than the internal SLO.</p>
<p>A <b>critical user journey</b> (CUJ) is a task the user cares about, such as logging in or checking out. It usually spans several services, which is why SLOs written only by backend teams miss things.</p>

<h2>The numbers to know cold</h2>
''' + table(['SLO', 'Error budget', 'Full downtime allowed in 30 days'], [['99%', '1%', '7.2 hours'], ['99.5%', '0.5%', '3.6 hours'], ['99.9%', '0.1%', '<b>43.2 minutes</b>'], ['99.95%', '0.05%', '21.6 minutes'], ['99.99%', '0.01%', '4.32 minutes']], cls='num') + '''
<p>The sum for 99.9% is 0.001 × 30 days × 1,440 minutes a day = 43.2 minutes. Be ready to do it on a whiteboard.</p>

<h2>Choosing your first SLO</h2>
<ul>
<li><b>Measure the happy path at the load balancer.</b> It is the simplest place to see what users see.</li>
<li><b>Pick an availability target.</b> 99% is relaxed, 99.9% is the common choice and 99.99% is demanding.</li>
<li><b>Pick a goodness threshold</b>, usually latency. Around 100 ms feels instant; over a second feels clunky. A latency SLO is the <i>percentage of requests</i> faster than the threshold.</li>
<li><b>Set the target as a group.</b> Business, product, engineering and operations decide together, because the target is a business decision about user experience.</li>
<li><b>Keep it small.</b> Fewer than five high-level SLOs usually describe a service.</li>
</ul>
<div class="warn"><b>Don’t just codify today’s performance</b>It skips the conversation that matters: what <i>should</i> it be?</div>
''' + table(['Kind of system', 'SLIs to choose from'], [['Request and response services', 'Availability, latency, quality'], ['Data pipelines', 'Coverage, correctness, freshness, throughput'], ['Storage', 'Throughput, latency, durability']]) + '''

<h2>Alerting on burn rate</h2>
<p>Alert on how fast the budget is burning, not on a raw error threshold. A long window proves the burn is significant. A short window proves it is still happening, so the page clears soon after you recover.</p>
''' + table(['Budget spent', 'Over', 'Confirmed by', 'Burn rate', 'Action'], [['2%', '1 hour', '5 minutes', '14.4×', 'Page'], ['5%', '6 hours', '30 minutes', '6×', 'Page'], ['10%', '3 days', '6 hours', '1×', 'Ticket']], cls='num') + '''
<p>Where 14.4 comes from: 2% of a 30-day budget in one hour is 0.02 × 720 hours ÷ 1 hour = 14.4 times the sustainable rate. At that pace the whole budget is gone in about 50 hours.</p>
<div class="note"><b>Low traffic needs statistics</b>With 200 requests in an hour, a handful of errors proves nothing. Page only when the lower bound of a confidence interval (a Wilson score) is above the error rate you care about. With a 99% SLO, a 14.4× burn means a 14.4% error rate. To be 99% confident the true rate is above that (Wilson, z = 2.576) takes 173 failures in 1,000 requests, 42 in 200, or 24 in 100: 24 of 100 gives a lower bound of 14.8%, 23 only 14.0%. Try it in the Labs station.</div>

<h2>What the second edition adds</h2>
<ul>
<li><b>Adoption pitfalls.</b> Tie the programme to a business reason, iterate, share credit, and give teams templates and SRE help instead of bare mandates. “Eat from both ends”: start with end-user SLOs and core components.</li>
<li><b>Critical user journeys.</b> A synthetic probe must exercise the whole journey. In one case a single 99.99% probe stayed green while small combinations of protocol and destination were completely broken.</li>
<li><b>Per-customer SLOs</b> for B2B, where revenue follows a Pareto curve. An aggregate burn of 10× could be one customer at 100× and nine at zero.</li>
<li><b>Implicit SLOs.</b> Users depend on whatever you have actually delivered (Hyrum’s law). Raising the level wastes the workarounds they built and invites more load; lowering it pushes your costs onto them. Be explicit and over-communicate.</li>
<li><b>Client-side SLOs</b> have a high noise floor. Use <b>bad minutes</b>: a minute is bad if its error rate is above, say, 6% when the noise is 5%. Use sessionised SLIs where there is no denominator.</li>
<li><b>Tooling.</b> Pick one SLO tool and generate the alerts from it automatically.</li>
<li><b>Labels</b> record ownership and lifecycle: experimental, aspirational, committed, deprecated.</li>
<li><b>Failure concentration.</b> Use entropy or decision trees to find the cohort that a single number hides.</li>
</ul>

<h2>Where SLOs fall short</h2>
<ul>
<li>They assume countable success and failure events.</li>
<li>Nines aren’t intuitive to people.</li>
<li>The response is binary: in budget or out.</li>
<li>A budget blown in January still needs a monthly refresh, plus a longer programme to fix the cause.</li>
</ul>
'''

CH9 = '''
<h2>Monitoring versus observability</h2>
<p>Traditional monitoring depended on tribal knowledge and on engineers correlating dashboards by hand. It answers questions you already knew to ask.</p>
<p><b>Observability</b> combines time series, logs (including wide structured events), traces and continuous profiles so that someone <i>without</i> deep prior knowledge can test and reject hypotheses quickly, without shipping new code.</p>
''' + tiles([('Latency', 'How long requests take'), ('Traffic', 'How much demand there is'), ('Errors', 'How many requests fail'), ('Saturation', 'How full the system is')]) + '''
<p class="loopnote">The four golden signals are the starting point. RED (rate, errors, duration) suits services; USE (utilisation, saturation, errors) suits resources.</p>
<p>The metric that matters most is <b>time to mitigate</b>, from customer-centric detection to containment, followed by time to detect. The trend is towards knowledge graphs of assets and dependencies, AI-assisted investigation and views centred on customers instead of services.</p>

<h2>Google’s three strategies at microservice scale</h2>
''' + flow([('Out-of-the-box dashboards', 'Shared libraries export the same metrics everywhere'), ('Intelligent alerting', 'Statistical or ML baselines instead of one static threshold'), ('Automatic mitigation', 'Pre-checked symptoms, then rollback, scale-up or drain')]) + '''
<ul>
<li>Universal, horizontal alerts now make up nearly a fifth of all SRE alerts.</li>
<li>When an alert fires, a dashboard is generated with the common symptoms already checked.</li>
<li>Generic mitigations then run automatically: roll back on a statistically significant regression, scale up, or drain a failing cluster.</li>
</ul>

<h2>Two kinds of telemetry</h2>
''' + table(['', 'High-availability telemetry', 'Analytics telemetry'], [['Used for', 'Alerting, control loops, probers', 'Trends, capacity, investigations'], ['Speed', 'Sub-second, freshest data first', 'Minutes are fine'], ['Dependencies', 'As few as possible', 'Can be many'], ['Completeness', 'Can be sacrificed', 'Must be complete'], ['Cardinality and storage', 'Low, short-lived', 'High, cheap and long-lived']]) + '''
<p>Give users one SDK, one config and one query endpoint across both. Keep the alerting path independent of the systems it watches.</p>

<h2>OpenTelemetry</h2>
<p>OpenTelemetry grew out of Google’s Census. Its principles are open, extensible, correlatable, universal and loosely coupled. Its parts are the OTLP protocol, the Collector, the APIs and zero-code instrumentation. It joins signals together in three ways:</p>
''' + tiles([('Resource', '<i>Where</i> it ran: service, zone, instance.'), ('Context propagation', '<i>Which request</i>: trace IDs and baggage passed along each call.'), ('Instrumentation scope', '<i>Which code</i>: the library, plus stack traces.')]) + '''
<div class="note"><b>A ten-year decision</b>Treat the choice of an observability product as something you will live with for a decade; the chapter’s Waze migration story shows why. eBPF lets you observe without changing the application at all.</div>

<h2>What only clients can see</h2>
<p>Client telemetry reveals what backends can’t: DNS and load-balancer problems, expired certificates, failures hidden by retries, and crashes. It has to respect battery, network and privacy, and it must count the data it loses.</p>
<p>Customer-centric monitoring builds critical user journeys out of critical user interactions, and passes the journey ID through the RPC side channel so every hop can label its metrics.</p>

<h2>Change, retention and privacy</h2>
<ul>
<li><b>Change supervision</b> covers binaries, config, mobile releases, feature ramps and data pushes, not just code deploys.</li>
<li><b>Retention follows value.</b> Google keeps minute-level data in memory for hours, on disk for weeks, and as 30-minute rollups for years.</li>
<li><b>Privacy</b> needs data classification, minimisation, regional locality, deletion, fine-grained access control and customer-managed keys. Keep user IDs out of metric labels.</li>
</ul>

<h2>The statistics worth knowing</h2>
<ul>
<li><b>Paging on low traffic:</b> page when the lower confidence bound is above the SLO’s error rate.</li>
<li><b>Composing dependencies:</b> in series, success multiplies (80% × 90% = 72%). With hedging, failure multiplies (1 − 0.2 × 0.1 = 98%). Both assume the failures are independent.</li>
<li><b>Latency regressions:</b> build per-cohort baselines, compute z-scores and watch the share of requests above 2. A jump means a regression.</li>
</ul>
'''
