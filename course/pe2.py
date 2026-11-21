# Platform track, lessons 4-7.
from extras import flow, tiles, table, seq
from extras2 import pic, p, ul
from pe import L, h2, h3, note, deeper, code, ol

# ══════════════════════════════════════════════════════════════ 4 Efficiency
L.append(dict(
    id='pe-4', dot='4', part='P1', nav='Efficiency', h1='Efficiency: one optimisation, every team',
    final=14, by='Chris Kennelly', poc='POC 17',
    learn=['Why a common platform turns performance work into leverage', 'On by default, absorbed regressions and opt-outs', 'Application productivity metrics: telling “busier” from “slower”', 'Three lessons: take the long view, the platform is not fixed, build levers'],
    body=(
        h2('The big picture')
        + p('When every team runs on the same foundations, two things become possible. You can see where resources go across the whole fleet. And when you improve a shared component, everyone gets faster at once. Seeing leads to improving, and improving pays for more seeing. The chapter calls it a virtuous cycle.')
        + flow([('Common infrastructure', 'Same scheduler, RPC layer and libraries'), ('Fleet-wide observability', 'A profiler on every machine'), ('Central optimisation', 'Fix the shared thing once'), ('Savings', 'Which fund more observability', 'green')],
               'Each new measurement rides on rails that already exist, so the next insight is cheaper than the last.')
        + h3('How Google got there')
        + ul(['<b>The scheduler hides placement.</b> Borg decides which jobs share a machine. A CPU-heavy team and a memory-heavy team fit together, and spare capacity for failures is pooled across the data centre, not held by each team.',
              '<b>The same agents run on every machine.</b> That made it possible to profile everything: Google-Wide Profiling gives each team a debugging tool and gives the company one aggregated picture.',
              '<b>The aggregate showed surprises.</b> In 2015 the memory allocator accounted for about 8% of fleet usage, more than any single application. Nobody would have found that by looking at one service.'])
        + note('Profile-guided optimisation, made automatic', 'Compilers can optimise better with a profile of real usage. Getting one used to mean each team building a load test, an instrumented binary and a second build step, so few did. Google used the fleet profiler to synthesise a profile for every team automatically, and adoption became a one-line change. In its first year this doubled the share of the fleet using the technique. The lesson: effort deters adoption more than doubt does.')
        + h2('Shifting optimisations down')
        + h3('On by default')
        + p('The platform team prototypes an optimisation, canaries it on major workloads, evaluates it, and then turns it on for everyone. Teams pick it up at their next normal release and do nothing. This avoids the trap of building something and waiting for teams to discover it, and it keeps the decision with the people who understand the change.')
        + p('Not every workload gets faster. The chapter is candid about how regressions are handled.')
        + table(['Regression', 'What they do', 'Why'],
                [['Small, for a few', 'Absorb it', 'Per-application tuning adds options, and every option enlarges the set of states each future change must be tested against'],
                 ['Large, for a few', 'Offer an opt-out per application, and work to remove it', 'An opt-out is information: it shows which edge cases truly matter. One long-standing opt-out led to two further improvements'],
                 ['Large, for many', 'Don’t ship', '']])
        + p('The judgement behind this: an imperceptible slowdown or a little opt-out work for one team can be better than not shipping a major win for hundreds.')
        + h3('Spread the best local idea')
        + p('A better hash table began as a collaboration between the core C++ library team and two engineers on the search index. The index team could have swapped their hottest tables and stopped. Instead the platform team rolled the new table out across the whole codebase with automated refactoring, and CPU and memory needs fell substantially.')
        + p('A detail worth knowing: the designers made the table’s iteration order <b>random on purpose</b>. Earlier attempts to optimise hash tables had been blocked because code quietly relied on the order (Hyrum’s law again). Randomising it stopped that dependency from forming, which kept the door open for later improvements. Teams sometimes ask to switch it off. Saying yes would help them today and hurt everyone, including them, later.')
        + h3('Work further up the stack')
        + p('A low-level copy routine can only be made so fast, because it must do the copy. Higher up, analysis of the code may show the copy was never needed. The fastest copy is the one you don’t make. Tools from linters to language models find these recurring patterns, and the central team sends ready-made changes to owners for review.')
        + h3('Shift left for performance too')
        + ul(['Fleet telemetry raises alerts when a function, application or library regresses after a rollout.', 'Canaries pause for automated performance checks against the old version, not only reliability checks.', 'Benchmarks run periodically and on proposed changes.', 'Code-review tooling flags known slow patterns and proposes the fix.', 'Well-designed libraries make the efficient way the obvious way.'])
        + deeper('measuring what matters')
        + h2('Connect efficiency to business value')
        + p('Nobody buys servers in order to allocate memory. Low-level numbers are easy to measure and say little about value. What matters is how much useful work you get for what you buy.')
        + p('The problem: a service’s CPU use went up 20%. Is that a regression, or is it handling more traffic? You can’t tell by looking.')
        + p('Google’s answer is the <b>application productivity metric</b> (APM). Each service reports how much useful work it does, and the platform divides by resources used: videos processed per CPU-second, records per byte-second of memory, queries per accelerator-hour.')
        + table(['CPU used', 'Useful work', 'Work per CPU-second', 'Verdict'],
                [['+20%', '+20%', 'Flat', 'Busier. Nothing is wrong'], ['+20%', 'Flat', 'Down 17%', 'A regression. Find the change'], ['Flat', '+15%', 'Up 15%', 'An optimisation landed']], cls='num')
        + ul(['<b>Defaults make it practical.</b> RPC servers report requests; pipelines report records. Most services need no setup.',
              '<b>Outliers reveal bad metrics.</b> A batch service should count items, not batches. A service whose work metric doesn’t track its resource use at all is probably misconfigured.',
              '<b>They catch what component metrics hide.</b> Work on the allocator’s layout decisions made applications faster and made the allocator <i>look</i> more expensive in relative terms. Only a work-based metric showed the win. The team’s joke was that the allocator had become faster than light.'])
        + h3('Not all work is equally valuable')
        + p('Some resource use serves no user directly and is still necessary: monitoring probes, hedged requests, load tests, load balancing and shedding. Some serves nobody: a video still playing to an empty room, or a backend finishing a request whose caller has already given up. Deadline propagation stops the second kind. Knowing the criticality of each kind lets you shed the non-essential during a disruption and push background work off-peak, which means less idle capacity held in reserve.')
        + note('Proxies and Goodhart', 'Measuring precisely costs something too. Use proxies that track the business goal closely, and remember Goodhart’s law: a measure that becomes a target stops being a good measure.')
        + h2('Three lessons')
        + tiles([('Take the long view', 'The cost of an opinionated platform is visible. The cost of flexibility is not: every option must be discoverable, tested and carried forward, and it becomes a tax on every later change.'),
                 ('Don’t assume the platform is fixed', 'Application teams work around platform problems. If everyone works around the same one, it looks rare. Report it; the platform can change when the value is there.'),
                 ('Create leverage and use it', 'Improve something already widely used. Or migrate ten implementations to one, so every later improvement lands on everybody.')])),
    say='Efficiency at scale comes from leverage. If every team shares the same libraries and runtime, I can profile the whole fleet, find that some shared component is the biggest consumer, fix it once, and ship it on by default. I’d measure with useful work per unit of resource, because raw CPU can’t tell me whether a service got slower or just busier.',
    aws='Start with visibility: Cost and Usage Reports with cost allocation tags, Compute Optimizer, and a continuous profiler across the fleet (CodeGuru Profiler or an open-source eBPF profiler). Build an application productivity metric in CloudWatch with metric math: a business counter from your service divided by vCPU-seconds from Container Insights. Shift down with shared base images, a common runtime and Graviton as the default, delivered through the golden-path pipeline so teams get improvements at their next deploy. For criticality, use Spot and scheduled scaling for work that can wait.',
    iq=[('Your cloud bill for a service rose 30% in a quarter. How do you find out whether that is a problem?',
         ['I wouldn’t start from the bill. I’d start from what the service did for that money.',
          'First I’d define useful work for this service: requests served, orders processed, records transformed. Then I’d plot work per vCPU-second and per gigabyte-hour over the quarter. If work also rose about 30%, the service is busier and the cost is growth. If work is flat, efficiency dropped and I have a regression to find.',
          'For a regression I’d line the productivity curve up against deploys and config changes, and use profiles from before and after to see which functions grew. Common culprits are a new serialisation step, a logging change, a retry storm, or a dependency upgrade.',
          'I’d also check criticality. Some growth is work nobody needs: retries against a failing dependency, requests that continue after the caller timed out, a batch job running at peak. Deadline propagation and moving batch off-peak fix those without touching the code path.',
          'Finally I’d ask whether the fix belongs in the service or in the platform. If the cause is a shared library or base image, fixing it centrally helps every team that has the same problem and hasn’t noticed.'])],
    quiz=[['A service uses 20% more CPU than last month and processes the same number of requests. What does its application productivity metric say?', ['Nothing has changed', 'The service is busier', 'Efficiency regressed', 'The metric is misconfigured'], 2, 'Same work for more resources means work per CPU-second fell. That is a regression, not growth.'],
          ['Why did the hash-table designers make iteration order random?', ['To make it faster', 'To stop code depending on the order, which would block future optimisations', 'For security', 'To simplify testing'], 1, 'Hyrum’s law: any observable behaviour gets depended on. Removing the stable order kept the implementation free to change.']],
    turn='Run <b>POC 17</b>. It computes work per CPU-second for a set of sample services, labels each change as growth, regression or optimisation, flags services whose work metric doesn’t track their usage, and decides whether an optimisation should ship on by default given who it helps and who it hurts.',
    take=['Shared foundations turn one optimisation into a fleet-wide saving.', 'Ship on by default, absorb small regressions, and treat opt-outs as information.', 'Measure useful work per unit of resource, or you can’t tell slower from busier.']))

# ══════════════════════════════════════════════════════════════ 5 Security
_risk = '''
<text x="20" y="34" class="b">Before</text><text x="20" y="54" class="m" style="font-size:13px">a string-based API</text>
<text x="20" y="174" class="b">After</text><text x="20" y="194" class="m" style="font-size:13px">a safe abstraction</text>
''' + ''.join(f'<rect x="{170 + c * 34}" y="{20 + r * 34}" width="26" height="26" rx="5" class="pn" style="stroke:{"var(--red)" if (r, c) in [(0, 2), (1, 5), (2, 0)] else "var(--rule)"};stroke-width:{"3" if (r, c) in [(0, 2), (1, 5), (2, 0)] else "1.5"}"/>' for r in range(3) for c in range(6)) + '''
<line class="ln" x1="384" y1="66" x2="470" y2="66" marker-end="url(#ah)"/>
<rect class="pn" x="474" y="38" width="216" height="56" rx="8" style="stroke:var(--red);stroke-width:2"/><text x="582" y="62" text-anchor="middle" class="b">risky operation</text><text x="582" y="82" text-anchor="middle" class="m">runs whatever string arrives</text>
<text x="170" y="134" class="m">every call site must be right, every time; some won’t be</text>
''' + ''.join(f'<rect x="{170 + c * 34}" y="{160 + r * 34}" width="26" height="26" rx="5" class="pn"/>' for r in range(3) for c in range(6)) + '''
<line class="ln" x1="384" y1="206" x2="412" y2="206" marker-end="url(#ah)"/>
<rect class="pn" x="416" y="178" width="130" height="56" rx="8" style="stroke:var(--green);stroke-width:3"/><text x="481" y="202" text-anchor="middle" class="b">safe API</text><text x="481" y="222" text-anchor="middle" class="m">typed, reviewed</text>
<line class="ln" x1="546" y1="206" x2="572" y2="206" marker-end="url(#ah)"/>
<rect class="pn" x="576" y="178" width="114" height="56" rx="8"/><text x="633" y="210" text-anchor="middle" class="m">risky operation</text>
<text x="170" y="276" class="m">call sites can’t express the mistake; experts review one small module</text>'''
L.append(dict(
    id='pe-5', dot='5', part='P1', nav='Security', h1='Security: if it isn’t secure, it shouldn’t compile',
    final=15, by='Christoph Kern', poc='POC 13 · 14 · 15',
    learn=['Why training and scanning can’t deliver assurance, however much you do', 'Security as an emergent property, application archetypes and invariants', 'Safe Coding: risky operations, safe abstractions and the two ways to build one', 'Supply chain (SLSA, attestations), safe deployment and security observability', 'What AI changes, and why prompt injection resists these techniques'],
    body=(
        h2('The big picture')
        + p('The same kinds of vulnerability top the incident reports year after year: memory corruption, injection, broken access control. The industry’s list of the most dangerous weaknesses has barely changed in a long time, despite decades of secure-coding training.')
        + p('This chapter’s diagnosis is that the problem is structural. We ask every developer to avoid every known mistake at every call site, forever, and we check afterwards with tools that can only find some of what went wrong. People make mistakes because the systems they work in make mistakes easy. So do AI coding tools, which now write more code than humans can review.')
        + p('The platform answer: move security out of each developer’s head and into the things all code is built from, so whole classes of bug can’t be written.')
        + note('What “platform” means here', 'More than the cluster your code runs on. It is the whole stack a developer touches: the language and its type system, libraries and frameworks, the build system, deployment and runtime, and the review and release process. Application bugs are born in the layers nearest the developer, so that is where they can be prevented.')
        + h2('Why the usual approaches fall short')
        + p('Three facts frame the problem.')
        + ul(['<b>Experts are outnumbered several hundred to one.</b> The ratio is about the same at Google as at a small company. Hiring can’t fix it.',
              '<b>Software is programming integrated over time.</b> Code that was secure at launch may not be after next week’s commit, so a point-in-time review proves little.',
              '<b>Testing can’t show absence.</b> Even a tiny program has more possible states than any test suite can visit. A two-by-two grid of 64-bit numbers has about as many states as there are atoms in the observable universe. For ordinary bugs this is tolerable, because a bug nobody hits hardly matters. For security it isn’t, because an attacker goes looking for the one input you never tried.'])
        + p('That last point defines the goal. <b>Assurance</b> is confidence that a requirement holds for every behaviour of the program. <b>Continuous assurance</b> is keeping that confidence for every version you ship.')
        + table(['Approach', 'What it is', 'Why it isn’t enough'],
                [['Ship and patch', 'Find vulnerabilities in production', 'Real exposure, an endless patch treadmill, lost trust. Hard to escape later'],
                 ['Find after commit', 'Static analysis, fuzzing, sanitizers, scanners, security review (increasingly by AI)', 'Tools miss bugs or raise false alarms, usually both. Findings arrive after the author has moved on. Useful as defence in depth; can’t prove nothing remains'],
                 ['Shift left', 'Train developers; analyse in the editor', 'Nobody can hold hundreds of vulnerability patterns in mind while solving a business problem. False alarms teach people to suppress warnings, real ones included']])
        + note('Initial and sustained velocity', 'Security feels like it slows teams down when it is bolted on as reviews and gates. The chapter separates how fast you ship the first version from how fast you keep shipping. Shortcuts buy the first and cost the second. A platform pays the upfront cost once so applications inherit both. For a young product still finding its market, trading sustained speed for initial speed can be rational, if it is a conscious choice with a plan to pay it back.')
        + h2('Shift down: the platform as a security control')
        + p('Security can’t be added afterwards. It emerges from how the system is designed, how the software is structured, and what the platform allows. That works in both directions.')
        + tiles([('If the platform enforces it', 'Applications inherit the guarantee. In Rust, Java or Python, ordinary code can’t corrupt memory, and the exceptions are explicit and reviewable.', 'green'),
                 ('If the platform doesn’t', 'Applications will have the defect. Any large C++ codebase contains memory-safety bugs, and decades of effort haven’t removed them after the fact.', 'red')])
        + p('Shifting down also compounds. Each class of bug the platform eliminates frees the security team from reviewing, advising and responding for that class. They spend the time eliminating the next one.')
        + h3('Three objectives')
        + ol(['<b>Prevent common classes by construction.</b> Design the platform so the bug can’t be introduced.', '<b>Confine what is left.</b> Keep security-critical code in a few well-reviewed platform components, not spread across every application.', '<b>Keep the guarantee through change</b> without an expert reviewing each commit.'])
        + p('Prevention never reaches zero defects, so <b>containment</b> stays essential: sandboxes, least-privilege identities and mediated access limit the damage of whatever slips through.')
        + h3('Application archetypes')
        + p('Most applications are not architecturally unique. A stateless RPC service, a SQL-backed store, a browser frontend talking to an API, a mobile client: the same shapes recur, and the same threats come with each shape whether the app is a bank or a photo editor. The chapter calls a recurring whole-application shape an <b>archetype</b>.')
        + table(['Component', 'Threat it brings', 'Invariant the platform can own'],
                [['Relational storage', 'SQL injection', 'Every query’s structure comes only from the developer; untrusted values are bound as parameters'],
                 ['Web frontend', 'XSS, CSRF, clickjacking', 'Untrusted values reach the page only through types that guarantee correct escaping; state-changing requests are CSRF-checked; framing is restricted'],
                 ['RPC backend', 'Unauthenticated or unauthorised calls', 'Every request is authenticated and authorised before any handler code runs'],
                 ['Mobile client and API', 'Trusting the client', 'The server treats all client input as untrusted and re-checks authorisation']])
        + p('An <b>invariant</b> is a property that holds on every execution path, including for malicious input. A platform can’t own your business logic, but it can own these, and they account for most of what goes wrong in practice.')
        + p('A platform built for a whole archetype beats a set of separate controls, because some risks live between components. A browser frontend and an authenticated API can each be secured and still leave a gap: an attacker’s page can make the victim’s browser call a state-changing endpoint, unless cross-site defences cover the entire API surface. That depends on the boundary, which neither side owns alone.')
        + deeper('Safe Coding, the supply chain, deployment, observability and AI')
        + h2('Safe Coding')
        + p('This is the heart of the chapter. Start with one definition.')
        + p('A <b>risky operation</b> is safe only if some condition holds when it runs, and nothing in the language or API guarantees that it does. Reading element <code>i</code> of an array is safe only if <code>i</code> is in bounds. Running a SQL string is safe only if it was assembled from trusted parts. The condition is often established far away, in another module or another team’s code, so checking it means reasoning about the whole program.')
        + p('A <b>safe abstraction</b> wraps the risky operation in a module with two properties.')
        + ol(['Its public interface puts no safety conditions on the caller. Any use that type-checks is safe.', 'Its implementation takes full responsibility for the conditions of the risky operation inside.'])
        + p('The consequence is the important part: you can verify the abstraction by reading only its own code. A security expert reviews it once and it is safe for every caller, including applications not written yet.')
        + pic(720, 290, _risk, 'My drawing of the chapter’s central move. The risk is relocated from thousands of call sites into one component small enough to review properly.', 'Before: many call sites feed a string-based risky operation and a few are wrong. After: the same call sites go through one typed safe API that guards the risky operation.')
        + h3('Two ways to build one')
        + table(['Technique', 'How it works', 'Example'],
                [['Runtime check', 'Establish the condition immediately before the risky operation', 'A vector type stores its length and checks the index on every access'],
                 ['Type invariant', 'A purpose-built type whose existence is the evidence. If you hold a value of that type, the condition is true', 'A query type that can only be built from constants in the source code']])
        + h3('The injection example')
        + p('The chapter uses a photo app that looks up an album by ID, restricted to the signed-in owner. Here is the same idea in Python.')
        + code('''
# Risky: structure and data travel in one string
q = ("SELECT * FROM albums WHERE owner = '" + user
     + "' AND id = '" + album_id + "'")
db.execute(q)
''')
        + p('Send an album ID of <code>x\' OR id=\'someone-elses</code> and the owner check disappears, because AND binds tighter than OR. The developer didn’t ignore advice. The API takes a string, and a string carries no record of where its characters came from.')
        + p('You can’t add a runtime check for that, since the information is gone. So the condition is tightened into something a type can carry: <i>the query text consists only of constants written by the developer</i>.')
        + code('''
# Safe: the database wrapper accepts only a TrustedSql, and a TrustedSql
# can only be built from a string literal. Values go in separately.
q = TrustedSql("SELECT * FROM albums WHERE owner = ? AND id = ?")
db.query(q, user, album_id)
''')
        + p('The attacker’s text now arrives as a bound value and is compared as data. Concatenating input into the query produces something that is not a constant, the API rejects it, and the build fails. The vulnerable program can no longer be expressed. The web equivalent is templates that escape automatically for each context, typed HTML values, and the browser’s Trusted Types standard, which refuses plain strings at dangerous sinks.')
        + h3('Why it scales')
        + p('Most of a codebase becomes plain safe code with no risky operations at all. A small, stable set of safe abstractions holds every one of them. Experts review those in isolation. The compiler’s type checker then verifies, across the entire codebase and on every build, that nothing reaches a risky operation except through a safe interface.')
        + p('The chapter places this on a spectrum. Testing samples behaviour. Formal verification proves a property for all behaviour and is so costly it is used mainly for cryptography, protocols and microkernels. Safe Coding sits between: an expert argument about one small module, extended mechanically to every program by the type checker. It captures much of the benefit of formal methods at a fraction of the cost.')
        + note('Tink: the same pattern for cryptography', 'Using a cipher correctly means choosing an algorithm, mode, key size, nonce and padding, and one quiet mistake voids the protection while every test still passes. Google’s Tink library offers operations named for what you want, such as authenticated encryption or digital signatures, with safe choices built in, dangerous options absent and key management included. A developer can encrypt correctly without knowing what a nonce is. People adopt it mostly because it is the easiest correct option, which is the ergonomics point in one example.')
        + h3('Making it stick')
        + ul(['<b>Build visibility rules</b> restrict who may call the raw risky API.',
              '<b>Narrow static checks.</b> Earlier, static analysis hunted an open-ended class of bugs and was unreliable. Here it checks one decidable property, such as “is this argument a compile-time constant?”, so it has no false negatives. Its only failure is being conservative, and that is resolved openly: use the safe pattern or get an expert-reviewed exception.',
              '<b>Conformance rules</b> let a codebase declare, and have verified, statements like “no direct DOM manipulation”.',
              '<b>Ergonomics.</b> The safe API must be at least as easy as the risky one and cover what people really need. Otherwise they queue for exceptions or find workarounds.'])
        + h3('What adoption costs')
        + p('A small team maintaining safe abstractions can support thousands of developers. Existing code is the expensive part, and the Android numbers show a way through: writing <i>new</i> code in memory-safe languages took memory-safety bugs from over 70% of the total to 24% in six years, without rewriting the old code. Old code’s bugs get found and fixed over time, so new defects concentrate in new code. Stop adding unsafe code and the rate falls.')
        + p('Plan for an exception process with tracked debt, and use sandboxing to make exceptions cheaper to grant. Count one recurring cost honestly: mandating an API reduces teams’ options and commits the platform team to keeping that API current.')
        + h2('Memory safety')
        + p('Between 60% and 70% of high-severity vulnerabilities in large C and C++ codebases are memory-safety bugs. Choosing a memory-safe language is the most dependable fix and one of the most consequential platform decisions. The guarantee holds only for the safe subset, so escape hatches (Rust’s <code>unsafe</code>, native extensions) must stay rare, explicit and reviewed. Hardened C++ reduces some bug classes at lower cost and does not give the full guarantee.')
        + h2('The software supply chain')
        + p('The goal: every binary running under a privileged production identity was built from trustworthy source that reflects what the organisation intended. Three properties support it: <b>provenance</b> (where it came from and how it was built), <b>integrity</b> (not tampered with) and <b>authorisation</b> (only approved changes, builders and binaries).')
        + table(['SLSA build level', 'Requires', 'Protects against'],
                [['L0', 'Nothing', 'Nothing. Development builds'], ['L1', 'Provenance exists', 'Mistakes, such as building the wrong commit. Easily forged'],
                 ['L2', 'Signed provenance from a hosted build platform', 'Tampering after the build'], ['L3', 'Hardened builds: isolated runs, protected signing keys', 'Tampering during the build by insiders, stolen credentials or other tenants']])
        + p('Be precise in interviews: SLSA build levels say the artifact was built from <i>that</i> source by <i>that</i> process. They say nothing about whether the source or its dependencies are free of flaws. Source integrity needs its own controls: mandatory second-person review, protected branches and strong authentication, configured centrally so every repository inherits them.')
        + flow([('Source', 'Reviewed by a second person'), ('Build', 'Hosted, isolated'), ('Attestations', 'Signed statements: built from commit X; approved; scans passed'), ('Deploy gate', 'Verifies attestations before anything runs', 'green'), ('Production', '')],
               'Google calls the gate binary authorization. Each attestation is a signed claim; the gate trusts signatures, not people.')
        + p('Third-party code gets the same treatment: curated repositories of vetted versions, automated dependency analysis, local copies for stability, and automated vulnerability tracking.')
        + h2('Identity and insiders')
        + ul(['<b>Identity:</b> single sign-on for people, platform-managed identities for workloads, identity carried through every service call.',
              '<b>Authentication:</b> frameworks verify credentials before application code runs; mutual TLS between services, handled by the mesh.',
              '<b>Authorisation:</b> service-to-service policy, role-based control for admin actions, and checks the framework won’t let you skip. For fine-grained questions like “can this user edit this document?”, a central service: Google’s Zanzibar stores relationships and answers consistently for hundreds of products.',
              '<b>Insider risk:</b> multi-party approval for sensitive actions, changes through automation with policy checks in place of direct human access, and proxies that validate, rate-limit and log what operators do.'])
        + p('Centralising concentrates risk, since a flaw in the shared service is valuable to an attacker. It also concentrates the ability to harden and review, with the one team equipped to do it. The chapter judges that a good trade.')
        + h2('Web security: about twenty controls')
        + p('Google’s internal web frameworks switch on roughly twenty controls by default. Knowing the three groups is enough for most interviews.')
        + table(['Group', 'Purpose', 'Controls'],
                [['Encryption', 'Everything travels over HTTPS', 'Secure cookies, HTTPS redirects, HSTS, central TLS termination'],
                 ['Isolation', 'Other sites can’t reach into yours', 'CSRF protection, SameSite cookies, framing protection, cross-origin opener and resource policies, Fetch Metadata checks, host header validation'],
                 ['Injection', 'Untrusted content is never run as code', 'Compile-time checks on JavaScript, typed responses, contextual auto-escaping templates, safe content types, HttpOnly cookies, strict CSP, Trusted Types, reviewed dependencies']])
        + p('No product team could keep all of that configured correctly by hand. And when the security team strengthens one control in the framework, every application gets it.')
        + h2('Safe deployment')
        + p('The Safe Coding idea applied to configuration. Nobody can hold every permission, network rule and option in their head, and a misconfiguration is as dangerous as a code bug.')
        + tiles([('Configuration as code', 'Versioned, reviewed, checked before merge. Every production change is recorded and attributable.'),
                 ('Blueprints', 'Pre-validated templates for common patterns, such as “external-facing web service”, with TLS, network policy and permissions already right. Update the blueprint and the fix propagates.'),
                 ('Conformance verification', 'Continuously compare what is deployed with the approved baseline. Rules like “no container runs as root” block violating deployments and alert on drift. The deployment-time version of a type checker.')])
        + h2('Measuring the guarantees')
        + p('A proxy watching traffic can’t tell whether a response was built by a safe template or whether a CSRF check ran. So Google’s frameworks <b>emit security telemetry themselves</b>, on every request: was the safe templating system used, did CSRF validation run, which code path served this. A central system collects and aggregates it. If a service stops emitting a signal, perhaps because an upgrade broke a check, someone is alerted.')
        + p('This changes what security monitoring can claim. Traditional monitoring detects the presence of problems, which is never complete. Measuring the presence of structural guarantees gives strong evidence of the <i>absence</i> of entire classes of defect.')
        + h2('Security with AI in the loop')
        + tiles([('AI writes buggy code too', 'The same patterns as humans, sometimes more often. Platform guardrails apply equally: code that breaks the rules doesn’t compile and can’t deploy. The bug classes AI most often produces are the ones platforms prevent best.'),
                 ('AI is a strong bug finder', 'Agents now find unknown vulnerabilities and write exploits, limited by compute, not by scarce experts. Still a search after the fact, so it can’t show that nothing remains. Aim it at what prevention doesn’t cover.'),
                 ('AI lowers the cost of adoption', 'Migrating code to safe patterns is high-volume, well-specified and mechanically checkable. An agent can iterate until the build, the conformance checks and the tests pass.')])
        + p('One cost argument is worth quoting in your own words: running a frontier model over every change is expensive, while a safe abstraction, once written, prevents the bug on every build for almost nothing.')
        + note('Why prompt injection is different', 'Prompt injection has the same shape as SQL injection: instructions and data share a channel and the interpreter can’t tell them apart. The cure for SQL depends on the interpreter offering a dependable separate channel for data. Language models don’t have one. Everything is a single stream of tokens with no grammar to enforce a boundary. Until that changes, prompt injection can’t be prevented by construction. Limit what an LLM-driven component is allowed to do.')
        + h2('Assembling your own')
        + p('No product on the market has all of this, because an opinionated platform only works when its opinions fit your organisation. The chapter’s method: for each property you need, pick a component that takes responsibility for it, put that component on the path developers already use, and measure where adoption has gaps.')
        + ol(['<b>Memory safety first.</b> It has the highest leverage. Use a memory-safe language for new services.',
              '<b>Web.</b> Render in the browser with a framework that supports Trusted Types; serve static or auto-escaped bootstrap pages; set security headers in one middleware; put authentication, CSRF and authorisation checks in the RPC layer; require a security reviewer for changes to those few files.',
              '<b>Supply chain.</b> Climb the SLSA levels with signed build attestations, and automate dependency updates.',
              '<b>Deployment.</b> Configuration as code, then policy enforcement at admission.',
              '<b>Observability.</b> The weakest area in public tooling. Emit your own framework-level security signals.'])),
    say='I’d stop treating developers as the last line of defence. Training and scanners find some bugs and can’t show that none remain. I’d shift security down: pick the invariants that matter for our kind of application, and enforce them in the platform with safe APIs that make the vulnerable code impossible to write, signed builds with a deploy gate, and policy checks on configuration. Then I’d measure adoption of those guarantees, because that is evidence that whole classes of bug are absent.',
    aws='Safe Coding is language-level, so it travels: a typed query wrapper over the RDS Data API or your database driver, plus a CI rule that bans raw query calls outside that module. Supply chain: CodeBuild or GitHub Actions producing signed provenance, AWS Signer with ECR image signing, and a gate at deploy time (Lambda code signing configurations, or Kyverno or Gatekeeper on EKS verifying signatures). Dependencies: CodeArtifact as the curated repository and Inspector for vulnerabilities. Identity: IAM Identity Center for people, IAM roles and EKS Pod Identity for workloads, VPC Lattice or a mesh for mutual TLS, and Amazon Verified Permissions for fine-grained, relationship-style authorisation. Web controls: terminate TLS centrally at CloudFront or ALB with ACM, and set HSTS, CSP and framing headers once with a CloudFront response headers policy. Safe deployment: CloudFormation Guard or OPA in the pipeline, Service Control Policies, and Config rules for drift. Posture: Security Hub with Config, which the chapter itself names as the AWS equivalent of Google’s Security Command Center.',
    iq=[('We keep finding SQL injection in code review. How would you make it stop?',
         ['Finding it in review means the API lets people write it, and with enough call sites someone always will. So I’d change what can be written.',
          'I’d introduce a small safe query module. It exposes a query type that can only be constructed from a literal in the source code, and a database wrapper whose query method accepts only that type, with all values passed as bound parameters. The raw driver is wrapped and hidden.',
          'Then I’d enforce it mechanically. A CI check fails the build if any file outside that module calls the raw execute method, and another verifies that the query type is only ever built from a constant. Those are narrow, decidable checks, so they don’t produce the noise that makes people ignore scanners.',
          'For existing code, I’d enforce on new and changed code immediately and list the legacy call sites as tracked exceptions. Most can be migrated automatically, and that is a good job for a coding agent, because success is checkable: it builds, it passes the conformance check, the tests pass.',
          'I’d make sure the safe API handles the awkward cases people really have, like dynamic sort columns or variable-length IN lists, with builder functions. If it doesn’t, they will ask for exceptions all day.',
          'Finally I’d report the percentage of services with zero raw query calls. When that reaches 100%, I’m no longer hoping reviewers catch injection. I have evidence the class is gone.']),
        ('What does SLSA level 3 give you, and what doesn’t it?',
         ['It gives me confidence about the build. The artifact was produced by a hosted build platform, each run isolated from the others, with signing keys the build steps can’t reach, and there is signed provenance saying which source revision and build process produced it. That defends against someone tampering during or after the build, including an insider or a compromised credential.',
          'It doesn’t tell me the source was good. A malicious or vulnerable change that was reviewed and merged will be built faithfully and signed. For that I need source controls: mandatory second-person review, protected branches and strong authentication.',
          'It doesn’t tell me the dependencies were good either. That needs a curated repository, scanning and update automation.',
          'And provenance only matters if something checks it. So I’d pair it with a deploy gate that refuses anything without valid attestations, with a logged and alerted break-glass path for emergencies.'])],
    quiz=[['Why can’t testing alone provide security assurance?', ['Tests are too slow', 'Tests explore a tiny fraction of possible states, and an attacker chooses the input you didn’t test', 'Tests can’t run in production', 'Security bugs don’t cause failures'], 1, 'Assurance means the property holds for every behaviour. Tests sample; adversaries search.'],
          ['What are the two defining properties of a safe abstraction?', ['It is fast and small', 'Its interface puts no safety conditions on callers, and its implementation owns the conditions of the risky operations inside', 'It is written in Rust and reviewed twice', 'It logs every call and rate-limits'], 1, 'Because of those two properties, an expert can verify it by reading only its own code, once, for all callers.'],
          ['Why can’t prompt injection be prevented the way SQL injection is?', ['Models are too slow to parse input', 'Language models have no dependable separate channel for data; instructions and data are one token stream', 'Nobody has tried', 'It can: use parameter binding'], 1, 'The SQL fix relies on the interpreter keeping structure and data apart. An LLM offers no such boundary yet, so limit the component’s privileges.']],
    turn='Three POCs go with this lesson. <b>POC 13</b> implements a trusted-query type, shows the album injection failing against it, and includes a conformance checker that fails the build on raw queries. <b>POC 14</b> is an attestation-based deploy gate with a break-glass path. <b>POC 15</b> renders a blueprint and checks deployed configuration for drift. Run 13 first and try to write the injection.',
    take=['Developers and AI both make mistakes. Design so the important ones can’t be made.', 'A safe abstraction moves risk from thousands of call sites into one module an expert can review.', 'Provenance, a deploy gate and policy checks carry the same idea into build and deployment.', 'Measure adoption of the guarantees: it is evidence that a class of bug is absent.']))
