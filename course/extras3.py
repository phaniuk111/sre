# Pass 3 findings: a gap check of the raw reading notes against the course found ideas that
# never reached a lesson, and Google system names the platform lessons described without naming.
# Also: links between the two books, generated from the knowledge map in synthesis.py.
import re

from extras2 import p, ul


def note(title, text):
    return f'<div class="note"><b>{title}</b>{text}</div>'


def names(rows):
    """Google names an interviewer may use, with what each one is and the nearest AWS idea."""
    return ('<h2>Names to recognise</h2><p>The lesson above describes these in plain words. An interviewer who has read the book may use the names, so know what each one refers to.</p>'
            '<div class="scroll"><table><thead><tr><th>Name</th><th>What it is</th><th>Closest on AWS</th></tr></thead><tbody>'
            + ''.join(f'<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td></tr>' for a, b, c in rows) + '</tbody></table></div>')


# ───────────────────────────────────────────────── SRE lessons: ideas that were missing
SRE_ADD = {
    4: note('Three lines worth quoting from the chapter',
            '<ul><li>“The fifth nine is people”, from Google SRE manager Trisha Weir. Reaching 99.999% depends on culture as much as on technology.</li>'
            '<li>John Shook’s point that you change culture by changing what people <i>do</i>, not first what they think. It is easier to act your way into a new way of thinking than to think your way into a new way of acting. That is why the chapter’s chain runs learning, confidence, behaviour, culture.</li>'
            '<li>DORA’s findings echo Google’s Project Aristotle, which found psychological safety to be the most important factor in high-performing teams.</li></ul>'),
    5: note('What to do when someone breaks something',
            'Every new Google SRE is given a short passage from Tanya Reilly. Paraphrased: when someone breaks something or finds it hard to debug, you say thank you. Thank them for the edge case, the overcomplicated part, the gap in the docs. Then make sure nobody can break it the same way again. It is the hiring chapter’s emphasis on helpfulness in one practice, and a good answer to “how do you respond when a junior engineer causes an outage?”'),
    6: note('When scorecards go wrong',
            'The chapter names two failure modes. Leaders who manage by numbers without understanding a team’s situation spread fear and undermine psychological safety; it quotes Jeff Bezos’s view that when data and anecdotes disagree, the anecdotes are usually right. And teams not committed to the spirit of a metric game it: measure deployment frequency and someone deploys the same binary every hour. Hence the rule in this lesson: scorecards are for coaching, never ranking.'),
    7: note('Where security fits in the Azure playbook',
            'The first phase of Microsoft’s engagement playbook, service fundamentals, is defined by two company programmes: the Secure Future Initiative and the Quality Excellence Initiative. Security posture is checked before SLOs and safe deployment, not after. Useful if you are asked how SRE and security engagement fit together.'),
    9: note('Instrumenting agents',
            'OpenTelemetry has semantic conventions for generative AI, covering model calls, agents, and agent-to-tool and agent-to-agent protocols such as MCP and A2A. Using them means agent traces look the same in every backend. The chapter’s caveat still holds: a trace shows what the agent did, not whether the answer was good.'),
    17: note('The overload error has to say whether to retry',
             'When a server sheds load, its error must tell the client two things: that it is overloaded, and whether retrying is appropriate (“overloaded” or “overloaded, don’t retry”). Without that, well-behaved clients retry into the overload. On AWS, think of a throttling error carrying a retry hint (HTTP 429 or 503 with <code>Retry-After</code>), which the SDK’s adaptive retry mode respects. Pair it with criticality labels on requests so the server knows what to drop first.'),
    20: note('Security for AI systems',
             'The chapter frames AI security with Google’s Secure AI Framework (SAIF). The risks it lists for SREs: model weights as a theft target, supply-chain risk in pretrained models and datasets, trust boundaries around agent tools such as MCP servers, and dynamic code execution. Its advice is to converge on one common AI platform so these controls are built once. On AWS: Bedrock Guardrails, model access through IAM, signed artifacts, and confidential compute for weights.'),
    21: note('Playbooks that tune themselves',
             'One worked example in the chapter: agents learn playbooks from the actions humans took to resolve tickets, then execute them within guardrails and hand back to a person when the situation is novel. If a human reopens a ticket the agent resolved, the case goes to evaluation and the playbook is retuned. Where toil can’t be automated, the agent enriches the ticket first, for example by asking the submitter for missing information, because much resolution time is spent searching for it.'),
    23: note('“What got us here won’t get us there”',
             'The authors borrow Marshall Goldsmith’s line for the shift from human-centric to human-supervised operations. If agents produce orders of magnitude more code, today’s release process would pack more changes into each release, making releases riskier and rollbacks harder. The answer is a heavily pipelined flow of many smaller changes, and SREs moving from specialists to generalists who direct agents. They close optimistically: SREs are not automating themselves out of jobs but “into jobs”, with less toil, less on-call and more autonomy.'),
}

# ───────────────────────────────────────────────── platform lessons: names to recognise
PE_NAMES = {
    'pe-1': [('Buganizer', 'Google’s issue tracker, coupled to its tooling so every change has a tracked reason', 'Jira or GitHub Issues linked to CodePipeline'),
             ('Dapper', 'Google’s always-on distributed tracing, built into the RPC layer', 'X-Ray, OpenTelemetry'),
             ('Stubby / gRPC', 'Google’s internal RPC framework, and its public descendant', 'gRPC on ALB or VPC Lattice'),
             ('Forge, Borg', 'The distributed build system and the cluster scheduler', 'CodeBuild; EKS or ECS'),
             ('Kruchten’s 4+1 views', 'Logical, development, process, physical, plus scenarios', '')],
    'pe-2': [('SnipIt', 'The internal screenshot tool followed through all six layers', ''),
             ('App Engine', 'The managed platform that let it reach 8 billion screenshots without rework', 'App Runner, Elastic Beanstalk'),
             ('Pace layers', 'Stewart Brand’s six layers of civilisation by speed of change', ''),
             ('Shearing layers', 'Frank Duffy and Stewart Brand: a building’s layers age at different rates', '')],
    'pe-3': [('google3', 'Google’s main monorepo ecosystem; the book’s example of a type 4 (assured) ecosystem', ''),
             ('Green-at-head', 'The latest version of every library must always build and pass its tests', 'Trunk-based development with required CI'),
             ('Large-scale change (LSC)', 'A change applied across thousands of projects at once by a central team', 'Automated PRs (Renovate, Amazon Q Developer transformations)'),
             ('TrustedSqlString', 'The safe query type that kept SQL injection at zero for a decade', 'A typed wrapper over the RDS Data API (POC 13)'),
             ('3Rs', 'Resources, rights, responsibilities', 'Your internal version of the AWS shared responsibility model')],
    'pe-4': [('Google-Wide Profiling (GWP)', 'A profiler on every machine, aggregated into one fleet view', 'CodeGuru Profiler, an eBPF continuous profiler'),
             ('AutoFDO', 'Profile-guided optimisation with profiles synthesised from the fleet, adopted with a one-line change', 'Compiler PGO in the shared build image'),
             ('TCMalloc', 'Google’s memory allocator; about 8% of fleet usage in 2015', ''),
             ('Temeraire', 'A TCMalloc improvement whose one long-standing opt-out led to two further gains', ''),
             ('SwissMap (Abseil)', 'The hash table rolled out across the monorepo, with randomised iteration order', ''),
             ('Application productivity metric (APM)', 'Useful work per unit of resource', 'CloudWatch metric math (POC 17)'),
             ('Streetlamp effect', 'Optimising the best-understood workloads instead of the biggest opportunities', '')],
    'pe-5': [('Safe Coding', 'Google’s name for the safe-abstraction discipline', ''),
             ('TrustedSqlString, SafeHtml, TrustedResourceUrl', 'Types whose existence proves a value is safe for its sink', 'A typed query layer; Trusted Types in the browser'),
             ('Error Prone @CompileTimeConstant', 'A Java check that an argument is a literal', 'A CI conformance check (POC 13)'),
             ('Tink', 'Google’s intent-based cryptography library', 'AWS Encryption SDK, KMS'),
             ('Zanzibar', 'Google’s global relationship-based authorisation service', 'Amazon Verified Permissions'),
             ('Binary Authorization for Borg', 'The internal deploy gate that verifies signed attestations', 'Lambda code signing, signature checks at EKS admission (POC 14)'),
             ('Zero Touch Production', 'Changes reach production only through automation with policy checks', 'Pipelines as the only deploy path; SCPs denying console changes'),
             ('Security Signals', 'Per-request security telemetry emitted by frameworks', 'Structured logs plus CSP violation reports'),
             ('SLSA', 'Supply-chain Levels for Software Artifacts', 'CodeBuild provenance, AWS Signer'),
             ('Site Isolation, COOP, CORP, Fetch Metadata', 'Browser isolation and cross-origin controls', 'CloudFront response headers policy')],
    'pe-6': [('CAS', 'Automated Canary Analysis Service: a statistical gate in the deploy platform', 'CodeDeploy with CloudWatch alarms (POC 05)'),
             ('Rollouts', 'Google’s central progressive-deployment platform', 'CodeDeploy, AppConfig, CodePipeline'),
             ('Autocap', 'Long-term capacity planner: forecasts and places capacity', 'Predictive scaling'),
             ('Autopilot', 'Real-time horizontal and vertical autoscaling inside Borg', 'Target tracking, Karpenter, VPA'),
             ('Monarch', 'Planet-scale time-series monitoring', 'CloudWatch, Managed Service for Prometheus'),
             ('TrueTime', 'GPS and atomic-clock time that gives Spanner global consistency', 'Amazon Time Sync Service (precision clocks)'),
             ('Spanner', 'Globally consistent database offered at five nines for multi-region', 'Aurora DSQL, DynamoDB global tables'),
             ('Break-glass (Binary Authorization)', 'An emergency annotation that permits a blocked deploy and logs it', 'An emergency role watched by CloudTrail and EventBridge')],
    'pe-7': [('Broccoli Man', 'An internal cartoon about how hard it was to “serve five terabytes”', ''),
             ('DevEx framework', 'Feedback loops, cognitive load, flow state', ''),
             ('HEART', 'Happiness, engagement, adoption, retention, task success', '')],
    'pe-8': [('JTBD', 'Jobs to be done', ''), ('TTFHW', 'Time to first “hello world”', 'Repo created to first production deploy'),
             ('COGS', 'Cost of goods sold: infrastructure cost per active user, service or build', 'CUR with cost allocation tags'),
             ('Golden path', 'Spotify’s term for the supported, easiest way', 'Backstage templates, Service Catalog'),
             ('Brownout', 'Breaking an old service briefly, on purpose, to find its users', '')],
    'pe-9': [('Agent Platform', 'The book’s name for Google Cloud’s managed AI platform', 'SageMaker, Bedrock'),
             ('Feature Store, Model Registry, Pipelines', 'The well-lit path for ML', 'SageMaker Feature Store, Model Registry, Pipelines'),
             ('TPU', 'Google’s AI accelerator', 'Trainium, Inferentia')],
    'pe-10': [('Surgical Team, Pilot System', 'Two essays by Fred Brooks the chapter uses', ''),
              ('Learning debt, brittle productivity', 'Cat Hicks’s terms for what happens without a learning culture', ''),
              ('Generative culture', 'Westrum’s performance-oriented culture, where information flows', '')],
}

# ───────────────────────────────────────────────── practice material from the findings
CARDS = [
    ['“The fifth nine is people”', 'Trisha Weir’s line in the SRE culture chapter: the last step to 99.999% depends on culture, not only technology.'],
    ['How do you change culture, according to John Shook?', 'Change what people do first. It is easier to act your way into a new way of thinking than to think your way into a new way of acting.'],
    ['What should an overloaded server’s error say?', 'That it is overloaded, and whether the client should retry. Otherwise good clients retry into the overload.'],
    ['What is SAIF?', 'Google’s Secure AI Framework, used in the SRE book to frame risks such as weight theft, poisoned models or data, agent tool trust boundaries and dynamic code execution.'],
    ['What makes an AI playbook self-tuning?', 'If a person reopens a ticket the agent resolved, the case is evaluated and the playbook retuned.'],
    ['Google-Wide Profiling', 'A profiler on every machine, aggregated into one view of the fleet. It showed the memory allocator was about 8% of fleet usage.'],
    ['Zanzibar', 'Google’s global, relationship-based authorisation service. On AWS the nearest is Amazon Verified Permissions.'],
    ['Autocap and Autopilot', 'Google’s long-term capacity planner and its real-time horizontal and vertical autoscaler.'],
    ['Zero Touch Production', 'People don’t change production directly; changes flow through automation with policy checks.'],
    ['Streetlamp effect', 'Optimising the workloads you can see best, not the ones with the biggest opportunity. Fleet-wide data avoids it.'],
]
QUIZ = [
    ['A junior engineer’s change caused an outage that exposed a confusing part of the system. What does the SRE book suggest you say first?', ['“Who approved this?”', '“Thank you”, then make it impossible to break the same way again', '“Please be more careful”', 'Nothing until the postmortem'], 1, 'Tanya Reilly’s advice, given to every new Google SRE: thank them for the edge case, then fix the system.'],
    ['Which Google system is closest to Amazon Verified Permissions?', ['Monarch', 'Zanzibar', 'Borg', 'Dapper'], 1, 'Zanzibar stores relationships such as “user X is an editor of document Y” and answers authorisation checks consistently across services.'],
]


# ───────────────────────────────────────────────── links between the books, from the knowledge map
PE_LESSON = {9: 'pe-1', 10: 'pe-2', 12: 'pe-3', 14: 'pe-4', 15: 'pe-5', 16: 'pe-6', 18: 'pe-7', 19: 'pe-8', 22: 'pe-9', 24: 'pe-10'}
PE_FINAL = {v: k for k, v in PE_LESSON.items()}


BOOK_NAME = {'S': 'the SRE book', 'P': 'the platform book', 'M': 'Mastering Prometheus', 'G': 'Observability with Grafana'}


def _lesson_maps():
    import synthesis as SY
    return {'S': {n: f'ch-{n}' for n in range(1, 24)}, 'P': PE_LESSON, 'M': SY.M_LESSON, 'G': SY.G_LESSON}


def _refs(refs):
    """'S8, P15, M3–M5' -> {'S': {8}, 'P': {15}, 'M': {3, 4, 5}}"""
    out = {}
    for book, a, b in re.findall(r'\b([SPMG])(\d+)(?:–[SPMG]?(\d+))?', refs):
        out.setdefault(book, set()).update(range(int(a), int(b or a) + 1))
    return out


def _home(lesson_id):
    """Which book and chapters a lesson teaches."""
    if lesson_id == 'm-3q':
        return 'M', {3}
    maps = _lesson_maps()
    for book, m in maps.items():
        chs = {n for n, lid in m.items() if lid == lesson_id}
        if chs:
            return book, chs
    return None, set()


def _label(book, n):
    return {'S': f'SRE ch {n}', 'P': f'platform ch {n}', 'M': f'Prometheus ch {n}', 'G': f'Grafana ch {n}'}[book]


def connections(lesson_id, MAP):
    """Concepts from the knowledge map that this lesson shares with the other books."""
    mine_book, mine = _home(lesson_id)
    if not mine_book:
        return ''
    maps = _lesson_maps()
    rows, others = [], set()
    for theme, _, concepts in MAP:
        for concept, definition, refs, poc in concepts:
            r = _refs(refs)
            if not (r.get(mine_book, set()) & mine):
                continue
            links, seen = [], set()
            for book in 'SPMG':
                if book == mine_book:
                    continue
                for n in sorted(r.get(book, ())):
                    lid = maps[book].get(n)
                    if lid and lid not in seen:
                        seen.add(lid)
                        links.append(f'<a href="#{lid}">{_label(book, n)}</a>')
                        others.add(book)
            if links:
                rows.append(f'<li><b>{concept}</b>: {definition}. See {", ".join(links)}.</li>')
    if not rows:
        return ''
    names = [BOOK_NAME[b] for b in 'SPMG' if b in others]
    other = names[0] if len(names) == 1 else ', '.join(names[:-1]) + ' and ' + names[-1]
    return f'<div class="note"><b>Across the books</b>Ideas in this lesson that {other} also cover{"s" if len(names) == 1 else ""}, from the <a href="#map">knowledge map</a>:<ul>{"".join(rows)}</ul></div>'


# ───────────────────────────────────────────────── pass 4 fold-back: what the observability books add to SRE chapters
OBS_BRIDGE = {
    8: note('Implementing this in Prometheus',
            '<p>This chapter explains multiwindow burn-rate alerting as a concept. <a href="#m-13">Mastering Prometheus chapter 13</a> turns it into rules: recording rules for the error ratio over 5 minutes, 30 minutes, 1, 2 and 6 hours, 1 and 3 days, and alert expressions that join a long and a short window with <code>and</code>, so a page needs a sustained burn that is still happening. Tools such as Sloth and Pyrra generate the whole set from a short spec, which is safer than writing them by hand.</p>'
            '<p>For low-traffic services the Prometheus book offers a window-based SLO: count good and bad time windows instead of requests, so one failed request in a quiet hour doesn’t swamp the ratio. It is a practical alternative to the confidence-interval approach described here. One trap the book itself falls into: burn rate must be computed from the <i>error</i> ratio, not the success ratio. <a href="https://github.com/phaniuk111/sre">POC 24</a> generates and simulates these rules.</p>'),
    9: note('Doing it with the Prometheus and Grafana stack',
            '<p>Testing hypotheses quickly depends on moving between signals. The Grafana book’s answer is correlation by design: <b>exemplars</b> attach a trace ID to a metric sample, Loki <b>derived fields</b> turn a trace ID in a log line into a link, and <b>span metrics</b> give RED metrics for every operation from the traces themselves (<a href="#g-5">Grafana ch 5</a>, <a href="#g-6">ch 6</a>).</p>'
            '<p>Each signal stores what it is good at: numbers in metrics with few labels, events in logs indexed only by a handful of labels, and high-cardinality context such as customer IDs in spans. The customer-centric invariant in this chapter is a black-box probe (the blackbox exporter, or CloudWatch Synthetics) plus real user monitoring (<a href="#g-12">Grafana ch 12</a>), and the universal alerts every service inherits are what monitoring mixins package (<a href="#m-11">Prometheus ch 11</a>).</p>'),
    10: note('Two additions from the Grafana book',
             '<p>The Grafana book adds a <b>gold–silver–bronze</b> structure above the incident roles here: responders work at bronze, managers own the tactical plan at silver, and senior leaders own strategy, legal and media at gold. Agreeing those levels in advance is what lets a serious incident escalate cleanly (<a href="#g-9">Grafana ch 9</a>).</p>'
             '<p>Tooling matters for the communications role too. Alertmanager grouping and inhibition stop one failure from producing a hundred pages (<a href="#m-5">Prometheus ch 5</a>), and incident tools such as Grafana Incident or AWS Systems Manager Incident Manager record the timeline automatically, so the postmortem starts from facts.</p>'),
    14: note('Testing monitoring itself',
             '<p>Alert and recording rules are configuration and deserve the same tests. <code>promtool test rules</code> runs unit tests with synthetic series and checks exactly when an alert fires and with which labels; Pint lints rules against a live Prometheus and comments on pull requests (<a href="#m-12">Prometheus ch 12</a>). Load tests belong in the release pipeline with thresholds taken from SLOs (<a href="#g-12">Grafana ch 13</a>), and after deploy, verification queries can trigger the automatic rollback this chapter calls for (<a href="#g-14">Grafana ch 14</a>).</p>'),
    15: note('Capacity tests and the capacity of monitoring',
             '<p>The Grafana book’s load test types map onto capacity questions: stress for a sustained peak, spike for a surge, breakpoint for where the service breaks, soak for slow leaks (<a href="#g-12">Grafana ch 13</a>). And monitoring has its own capacity limit: every new label value is a new series, so scrape limits and cardinality reviews are capacity planning for Prometheus (<a href="#m-7">Prometheus ch 7</a>).</p>'),
}
for _k, _v in OBS_BRIDGE.items():
    SRE_ADD[_k] = SRE_ADD.get(_k, '') + _v
