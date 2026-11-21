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


def _refs(refs):
    s, pch = set(), set()
    for book, a, b in re.findall(r'\b([SP])(\d+)(?:–[SP]?(\d+))?', refs):
        nums = range(int(a), int(b or a) + 1)
        (s if book == 'S' else pch).update(nums)
    return s, pch


def connections(lesson_id, MAP):
    """Concepts from the knowledge map that this lesson shares with the other book."""
    if lesson_id.startswith('ch-'):
        mine, other_book = int(lesson_id[3:]), 'P'
    else:
        mine, other_book = PE_FINAL[lesson_id], 'S'
    rows = []
    for theme, _, concepts in MAP:
        for concept, definition, refs, poc in concepts:
            s, pch = _refs(refs)
            here = mine in (s if other_book == 'P' else pch)
            there = pch if other_book == 'P' else s
            if here and there:
                links = ', '.join(f'<a href="#{PE_LESSON[n]}">platform ch {n}</a>' if other_book == 'P' else f'<a href="#ch-{n}">SRE ch {n}</a>' for n in sorted(there) if other_book == 'S' or n in PE_LESSON)
                if links:
                    rows.append(f'<li><b>{concept}</b>: {definition}. See {links}.</li>')
    if not rows:
        return ''
    other = 'the platform engineering book' if other_book == 'P' else 'the SRE book'
    return f'<div class="note"><b>Across both books</b>Ideas in this lesson that {other} also covers, from the <a href="#map">knowledge map</a>:<ul>{"".join(rows)}</ul></div>'
