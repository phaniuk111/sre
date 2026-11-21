# Platform track, lessons 8-10, plus flashcards, drills and the AWS table.
from extras import flow, tiles, table, seq
from extras2 import pic, p, ul
from pe import L, h2, h3, note, deeper, code, ol

# ══════════════════════════════════════════════════════════════ 8 Platform as a product
L.append(dict(
    id='pe-8', dot='8', part='P2', nav='Platform as a product', h1='Platform as a product: from good intentions to an operating model',
    final=19, by='Eric Maxwell', poc='POC 18',
    learn=['Project thinking against product thinking, and the three pillars of the product model', 'The product surface area, for humans and for AI agents', 'What a platform product manager does, and the tools: jobs to be done, build-buy-partner, capability roadmaps', 'The four lifecycle phases and the antipattern in each', 'A three-view scorecard'],
    body=(
        h2('The big picture')
        + p('The previous lesson said developer experience decides whether a platform succeeds. That is a goal. This lesson is the method: run the internal platform with the discipline of product management, as if it were something you sold.')
        + h2('Projects and products')
        + table(['', 'Project', 'Product'],
                [['Shape', 'Defined scope, a start and an end', 'A lasting system for delivering value'], ['Success', 'On time and on budget', 'Outcomes for customers'], ['Incentive', 'Deliver what was planned', 'Deliver what is needed'], ['When it ships', 'The team moves on', 'The work continues: support, debt, improvement']])
        + p('The chapter says much of the friction Google Cloud sees in customers adopting platform engineering comes from running it as a project. Three pillars define the alternative.')
        + tiles([('A defined customer', 'Not “the developer”. A new hire needs smooth onboarding and happy-path documentation. A principal engineer on core services needs advanced configuration and deep observability. A frontend developer needs fast feedback on UI changes.', 'lime'),
                 ('A clear value proposition', 'Why should someone use this instead of what they have? The alternative may be a favourite script, an open-source tool or doing nothing.', 'lime'),
                 ('An indefinite lifecycle', 'From idea through growth and maturity to retirement. The job is never done.', 'lime')])
        + h3('Jobs to be done')
        + p('The value proposition comes from the <b>job</b> a developer is trying to get done, which is rarely the feature they ask for. “I need a deploy button” is a request. “I need to get my change to production quickly and with confidence” is the job.')
        + p('The chapter’s example: a developer asks for a dashboard of build logs. The job is “when my deployment fails, I need to find the cause quickly so I can fix it.” Seen that way, the better answer may be clearer error messages, a chat notification that links straight to the failing step, or detecting the failure before they notice.')
        + h2('The product surface area')
        + p('This is the inventory of every point where a developer, <i>or their AI assistant</i>, touches the platform. The chapter insists on mapping it twice: once for human usability and once for machine discoverability.')
        + table(['Surface', 'For humans', 'For agents'],
                [['Interfaces', 'APIs, command line, console, SDKs, config files and error messages', 'Strict API specifications, predictable names, well-defined tool schemas, and errors with plain-text context. An obscure error code makes an agent invent a fix'],
                 ['Documentation', 'Guides, tutorials, references, troubleshooting. A first-class feature', 'Structured and machine-readable. Your docs are what your assistant knows. Stale docs produce confident wrong answers'],
                 ['Onboarding', 'Time to first “hello world”. A bad first run loses people before they see any value', 'Can an agent create that first application unaided?'],
                 ['Support and communication', 'Chat channels, office hours, tickets, release notes, the roadmap, and a way to propose changes to the platform itself', 'The same channels, increasingly answered with AI help']])
        + note('The engine and the car', 'The API is the engine; the product is the whole car, and nobody buys just an engine. The chapter updates the image: today’s car has self-driving. If the dashboard is beautiful and the engine’s sensors can’t talk to the self-driving system, the car crashes. Your APIs are the sensors and the agents are the self-driving system.')
        + deeper('the product manager, the toolkit, the lifecycle and the scorecard')
        + h2('The platform product manager')
        + p('A product manager for something that earns no revenue can look like a luxury. The chapter argues the role is the owner of the developer experience and the link between what the platform can do and what the organisation needs.')
        + ul(['<b>Shape the vision.</b> Where is the platform going, and why does that matter to developers and the business?', '<b>Be the customer’s voice</b> in every planning and prioritisation discussion.', '<b>Translate in both directions.</b> Developers’ needs into terms leaders use, such as delivery metrics and time to market; leaders’ goals into a roadmap engineers can build.', '<b>Prioritise.</b> Make the trade-offs between user value, feasibility and business impact.'])
        + p('They do it with engineering and design from the first day. Throwing requirements over a wall is named as an antipattern. If there is no dedicated person, the engineering manager or tech lead wears the hat, and must protect time for talking to users, or delivery pressure will eat it.')
        + h3('Discovery habits')
        + ul(['Talk to developers regularly, as open conversations about their work. These are not pitches.', 'Run journey-mapping workshops on one workflow, such as onboarding a new service. Sticky notes on a wall expose hidden friction fast.'])
        + p('The purpose is to avoid the most common failure: an elegant platform that solves a problem nobody has.')
        + h3('Build, buy or partner')
        + ol(['Is this a core competency or a competitive advantage? Then build. A trading firm builds its own low-latency trading system.', 'Does something existing solve 80% of it? Then lean towards buying or partnering. The lifetime cost of building and maintaining in-house is usually far more than the licence.', 'Can you adopt an off-the-shelf product and spend your engineering on the unique last mile? Often the most practical answer. Less engineering, though never none.'])
        + h3('The capability roadmap')
        + p('A roadmap is a communication tool. It says which problems you will solve and why, and it is neither a release plan nor a backlog. Write outcomes (“enable self-service database provisioning”), not features (“build database API v1”).')
        + flow([('Now', 'Being built. High confidence'), ('Next', 'In discovery'), ('Later', 'Direction only. No promised solutions')])
        + h2('The lifecycle')
        + table(['Phase', 'What to do', 'Antipattern'],
                [['1 · Conception', 'State a hypothesis: by solving X for developer Y we get outcome Z. Test it cheaply with a hand-run MVP (below)', 'Vanishing for six months to build a perfect first version'],
                 ['2 · Ramp', 'Turn what worked by hand into a self-service <b>golden path</b>: the opinionated, documented, supported way. Sell it with examples, demos and pairing', 'Mandates without a good product, which produce resentment and malicious compliance'],
                 ['3 · Maturity', 'The platform is the default. Open safe extension points so others can build on it', 'Tyranny (a rigid path nobody may leave) or chaos (so much customisation it can’t be supported)'],
                 ['4 · Evolution and end of life', 'Keep scanning for what is changing. Retire things deliberately', 'The ghost ship: an old platform left to decay with no owner']])
        + h3('The MVP you run by hand')
        + p('Want to build a deployment pipeline? Write no code yet. Find a friendly team and do their deployments for them for two weeks: run the scripts, provision the infrastructure, watch the logs. It doesn’t scale and isn’t meant to. It shows you every edge case and last-mile problem a whiteboard would miss. You are looking for a problem so basic that developers hit it several times a day. Write code only after a handful of hand-served teams are happy.')
        + h3('From golden path to town square')
        + p('A mature platform is less like one road and more like a town square. The platform team provides the paving, lighting and plumbing, meaning reliability, security and core APIs, and keeps the main roads that take 80% of people where they need to go. Around the square, other teams build their own shops through plugins, extension points and contribution models. The community solves its long-tail problems and the platform team stays on the core.')
        + note('“Adoption is voluntary, even when it’s mandatory”', 'The chapter’s best line. You can order people to use a platform. You can’t order them to use it well. A top-down mandate without a product worth choosing gets obedience to the letter and workarounds in spirit.')
        + h3('Deprecation is a launch in reverse')
        + ol(['A plan: a timeline, a migration path and a reason people will accept.', 'Communication, early and repeated, in several channels.', 'Tooling and support. Automate the migration where you can.', 'A final off switch. Until the old system is turned off, you haven’t collected the benefit.'])
        + p('To find out who still depends on an old service, run a <b>brownout</b>: break it deliberately for a short time and see who notices.')
        + h2('A scorecard with three views')
        + table(['View', 'Question', 'Metrics'],
                [['User', 'Do developers use it and like it?', 'Adoption and retention, satisfaction scores, first-attempt task success, time to “hello world”, themes from feedback'],
                 ['System', 'Is it healthy and affordable?', 'Reliability against SLOs; cost of goods sold: infrastructure cost per active user, per service or per build'],
                 ['Business', 'Does it move the organisation?', 'Delivery metrics for adopters, time to market, security and compliance (fewer vulnerabilities per service; share of services meeting a supply-chain standard)']])
        + p('Read them in that order. If developers don’t use the platform, the other two views don’t matter. Rising cost per user without more adoption or capability is a warning. And beware vanity metrics: “total deployments” says nothing about whether anyone is better off.')),
    say='I run a platform as a product, not a project. That means named customer segments, a value proposition measured against whatever they use today, and a lifecycle that includes retirement. I find the job behind each feature request, validate it by doing the work by hand for a couple of teams, then pave it as a golden path and earn adoption. I report three views: whether developers use it, whether it is reliable and affordable, and whether teams on it deliver faster and safer.',
    aws='A golden path on AWS is a template that produces a repository, a pipeline, IAM roles, alarms and dashboards in one step, published through Backstage or Service Catalog and built from shared CDK constructs or Terraform modules. Extension points are versioned constructs teams can compose, with Service Control Policies marking what can’t be changed. For the scorecard: adoption from tags or template usage, cost per service from Cost and Usage Reports with cost allocation tags, platform SLOs in CloudWatch, and delivery metrics from pipeline events. For deprecation, use CloudTrail and access logs to find remaining callers, then a scheduled brownout with a 4xx response that names the replacement.',
    iq=[('You’ve been asked to build an internal developer platform from scratch. What are your first ninety days?',
         ['I’d spend the first weeks not building. I’d interview and shadow developers across a few team types to find where their time goes between writing code and seeing it in production, and I’d map one or two workflows end to end with every wait and hand-off.',
          'From that I’d pick one job that is painful and frequent, probably something like “get a new service safely to production”. I’d write the hypothesis down: solving this for these teams should cut their lead time by this much.',
          'Then I’d run it by hand. For two or three friendly teams, my team does the work for them for a couple of weeks. That shows the edge cases and tells me whether the problem is real before I’ve built anything.',
          'In the second month I’d automate what worked into a thin golden path: a template that gives a repository, pipeline, permissions and monitoring with good defaults, and documentation with a working example. I’d measure time to first deploy and first-attempt success from day one.',
          'In the third month I’d widen to more teams by invitation, with pairing sessions and a champion in each. I’d publish a now-next-later roadmap and the first numbers.',
          'I’d decide build against buy for each piece as I go. Most of the pieces exist; my engineering should go into the integration and the last mile that is specific to us.',
          'What I’d avoid: a six-month build in isolation, a mandate before the product is good, and features nobody asked for.']),
        ('How do you retire a platform that 40 teams still use?',
         ['I treat it as a product launch run backwards, and I start with the replacement. If the new path isn’t clearly better and ready, the deprecation will fail however well I communicate.',
          'I’d publish a plan with a timeline, the reason, and a migration path for each kind of user. I’d find out who really uses the old system from logs, since the list of who says they do is always wrong.',
          'I’d make migration cheap: automated tooling where possible, pairing for the hard cases, and visible tracking so teams can see where they stand.',
          'I’d communicate early and repeatedly, in the channels teams read, and to their managers as dates approach.',
          'Before the end I’d run brownouts: short, announced outages of the old system that surface the callers nobody knew about.',
          'And I’d turn it off on the date. A platform that is deprecated and still running is a ghost ship: it keeps costing money, carries security risk and has no owner.'])],
    quiz=[['A developer asks for a dashboard of build logs. Using jobs-to-be-done, what should the platform team do first?', ['Build the dashboard', 'Find the underlying job, such as diagnosing a failed deployment quickly, and consider other solutions', 'Decline the request', 'Add it to the “later” column'], 1, 'The request is a feature. The job may be better served by clearer errors or a direct link to the failing step.'],
          ['What is a brownout in platform deprecation?', ['An unplanned partial outage', 'Deliberately breaking an old service briefly to discover who still depends on it', 'Running the platform at reduced capacity to save cost', 'A gradual feature rollout'], 1, 'It is a controlled way to find hidden users before the final switch-off.'],
          ['Which pair names the twin antipatterns of a mature platform?', ['Speed and safety', 'Tyranny and chaos', 'Build and buy', 'Left and down'], 1, 'Tyranny is a rigid path that no longer fits. Chaos is so much customisation the platform can’t be supported. Aim for a stable, opinionated core with defined extension points.']],
    turn='Write a now-next-later roadmap for your platform using outcomes, not features. Then run <b>POC 18</b>: it builds the three-view scorecard from sample data (adoption, time to first deploy, cost per active service, delivery metrics for adopters and non-adopters) and plans a brownout schedule from access logs.',
    take=['A product has customers, a value proposition and a lifecycle. A project has a deadline.', 'Find the job behind the request, and prove it by hand before automating.', 'Golden path first, then extension points; retire old platforms on purpose.', 'Score it from three views: user, system, business.']))

# ══════════════════════════════════════════════════════════════ 9 AI
L.append(dict(
    id='pe-9', dot='9', part='P2', nav='AI and platforms', h1='AI and platform engineering: a dual mandate',
    final=22, by='Isaac Albarran with Konrad Dryja', poc='POC 19',
    learn=['Platforms for AI and AI for platforms', 'Why the ML lifecycle needs its own abstractions and well-lit path', 'How efficiency, reliability and security change for AI workloads', 'The stages of AI in operations, up to agentic platforms'],
    body=(
        h2('The big picture')
        + tiles([('Platforms for AI', 'Infrastructure, abstractions and workflows for the whole life of a model. Usually called MLOps.', 'lime'),
                 ('AI for platforms', 'Using AI to improve how the platform itself is designed, automated, observed and run. Usually called AIOps.', 'magenta')])
        + p('The two feed each other. A well-abstracted platform is what lets an organisation use AI at scale, and the intelligence that produces is then turned on the platform. The chapter is written from Google’s position: the same investments that made Search and Gmail possible, in cluster management, distributed storage and custom accelerators, are what made training very large models possible.')
        + note('A naming point', 'The chapter refers to Google Cloud’s managed AI service as “Agent Platform”, with components for pipelines, a feature store, a model registry and experiment tracking. I use generic names here, since the ideas apply on any cloud.')
        + h2('Why AI needs its own platform')
        + p('An AI system is more than code. It is code, data and model configuration bound together, and that three-way coupling multiplies complexity. In ordinary software a person writes the logic. In machine learning the logic is learned from data.')
        + p('The chapter’s instruction is the <b>abstraction imperative</b>: servers were abstracted into virtual machines and containers to free application developers, and now accelerators, data pipelines and training workflows must be abstracted to free ML engineers.')
        + flow([('Data', 'Ingest, clean, track lineage'), ('Experiment', 'Non-linear. Failure is normal'), ('Train', 'Days or weeks on accelerators'), ('Productionise', 'Version, canary, roll back'), ('Serve', 'Latency and throughput'), ('Monitor', 'Drift, then retrain')],
               'Each stage has a reliability problem ordinary web services don’t. Data is treated as a liability as much as an asset.')
        + p('One term to know: the <b>configured model</b> is the complete set of code, data and hyperparameters. An experiment can be reproduced only if all three are captured.')
        + h3('Hiding the hardware')
        + table(['Abstraction', 'What it means'],
                [['Resource virtualisation', 'Model code doesn’t name hardware. The platform schedules onto whatever accelerators are free'], ['Fault tolerance', 'Automatic checkpoints and restarts. A node failing in a week-long run loses nothing and needs nobody'], ['Scalability', 'Training across hundreds of chips without anyone wiring up the interconnect by hand']])
        + p('A researcher should be thinking about the model. The topology of an accelerator pod and the driver versions of a GPU cluster belong to the platform.')
        + h3('The well-lit path for ML')
        + tiles([('Standard pipelines', 'Preprocess, train and evaluate as defined steps that run the same way every time.'),
                 ('A central feature store', 'One source for feature values, so the value used in training is exactly the value used in serving. This is the main defence against training-serving skew.'),
                 ('A model registry', 'The source of truth for models: versions, lineage, and which version is the default for prediction.')])
        + deeper('quality attributes for AI, the middle layer, and AIOps')
        + h2('The quality attributes, applied to AI')
        + h3('Efficiency')
        + p('Training one large model can use enormous amounts of energy and compute. Managing accelerators centrally lets the platform scale predictively and right-size from usage history, where teams would otherwise hold expensive hardware idle. And an improvement to a shared piece, such as the data-loading library or the serving protocol, reaches every AI team at once. The chapter calls it a flywheel.')
        + h3('Reliability: the silent failure')
        + p('In ordinary software, a fast “200 OK” usually means the service works. A model endpoint can return a fast 200 with an answer that is wrong or harmful. So model and data quality become first-class reliability signals.')
        + table(['Signal', 'What can go wrong', 'Example'],
                [['Model freshness', 'A model starts ageing the moment it ships, because the world moves', 'A stale fraud model is a reliability incident even while the API is healthy'],
                 ['Data quality', 'Inputs drift away from what the model was trained on. Different from integrity, which asks whether a file is corrupt', 'A fraud model tuned on transactions of $10 to $500 starts receiving $5,000 ones'],
                 ['Probabilistic correctness', 'Outputs aren’t deterministic, so you can’t assert on them', 'Use confidence thresholds and safety filters, and block low-confidence answers']])
        + p('That last row contains a trade worth naming: the platform chooses to refuse an answer, giving up some availability, to avoid a confident wrong one. It is fail closed, applied to a model.')
        + h3('Safety and security')
        + ul(['<b>Supply chain.</b> Scan containers, and deploy only signed and verified models.', '<b>Protecting the weights.</b> Model weights are often core intellectual property. Confidential computing keeps data and models encrypted while in use, shielding them even from platform operators and the infrastructure provider.', '<b>Adversarial defence.</b> Input and output guardrails deployed as gateways in the infrastructure, working independently of the model, to catch prompt injection, jailbreak attempts and toxic output.', '<b>Safe change.</b> Canary a new model version on a fraction of traffic and roll back automatically if metrics fall.'])
        + h3('The middle layer')
        + p('Between feature teams and the AI backends sits integration glue. Done badly it slows everyone down or gets ignored. Done well it saves feature teams from repeating integration work and lets the backends scale without their effort growing in step. Because AI changes so fast, the chapter sets three rules for it.')
        + ol(['<b>Iterate quickly.</b> Prefer small prototypes, with a plan to harden the parts that prove themselves.', '<b>Velocity first.</b> The layer exists to remove overhead. Any part that slows teams without a clear benefit destroys its own value.', '<b>Expect pivots.</b> Deliver something partial early. A command-line tool this month can beat a polished web application next quarter, and is easier to change.'])
        + p('ML engineers are also a distinct kind of customer. Their work is iterative and lives in notebooks, so offer SDKs before command lines, and visual tools for lineage, training curves and comparing experiments.')
        + h2('AI for platforms')
        + p('Modern platforms produce more telemetry than people can read. The chapter describes AIOps as the highest-leverage form of shifting down: expert operational knowledge encoded into tools that watch, predict and act.')
        + seq([('Make sense of the noise', 'One failure can set off thousands of alerts across dependent services. Models correlate them, narrow down the source and produce one targeted alert.'),
               ('Predict', 'Learn normal behaviour in place of fixed thresholds. Catch memory leaks and failing hardware early, and forecast capacity shortfalls in time to provision.'),
               ('Assist the operator', 'Ask in plain language what caused a latency spike. Have incident chat summarised and the postmortem drafted. Get a probable cause and a suggested playbook, with a person still deciding.'),
               ('Act', 'Schedule workloads against performance, cost and energy together. Restart a stuck process or roll back safely without waiting. Scale ahead of demand using history and upstream traffic.')])
        + h3('Agentic platforms')
        + p('Platforms now have a second kind of user. Consoles, APIs and SDKs serve people. Agents need structured, intent-based APIs and tool definitions they can discover and reason about.')
        + p('When agents do the operating, the platform’s role moves from supplying tools to supplying <b>controls and policies</b>. An autonomous agent may wander from what was intended, so the platform has to be the physics of the environment: the security, compliance and reliability limits that hold whatever the agent tries.')
        + note('Back to pace layers', 'The chapter closes with the layers model from lesson 2. AI applications are the fast layer, changing constantly. The platform is the slow, stabilising layer. It absorbs the shocks and gradually takes in what has proven itself above.')),
    say='There are two jobs. One is building the platform AI teams need: hide the accelerators, give them standard pipelines, a feature store and a model registry, and treat freshness, drift and confidence as reliability signals, because a model can return a 200 and be wrong. The other is using AI to run the platform: correlate alerts, predict problems, assist responders and, with guardrails, act. In both, the platform’s part is the controls that hold regardless of what a model or agent does.',
    aws='For the ML path: SageMaker Pipelines for standard workflows, Feature Store against training-serving skew, Model Registry with approval status as the source of truth, managed training with checkpointing and Spot for fault-tolerant jobs, and Model Monitor for data and quality drift. For generative workloads, Bedrock Guardrails act as the input and output gateway independent of the model, and Nitro Enclaves or confidential instances protect weights in use. Sign model artifacts and gate deployment on the signature, as with any other binary. For AIOps: CloudWatch anomaly detection and investigations, DevOps Guru for correlated insights, predictive scaling, and agents whose permissions are bounded by IAM and Service Control Policies so the limits hold whatever the agent decides.',
    iq=[('A model endpoint has 100% availability and low latency, and the business says predictions have got worse. How should the platform have caught this?',
         ['This is the silent failure that ordinary monitoring can’t see. The four golden signals measure whether the service answered. They don’t measure whether the answer was good.',
          'The platform should treat three more things as reliability signals. Freshness: how old is the model and the data it learned from, against a target for this use case. Data quality: are the live inputs still distributed like the training data? I’d compare feature distributions continuously with a drift measure and alert on a threshold. Output quality: track confidence, the rate of low-confidence answers, and wherever ground truth arrives later, accuracy against it.',
          'I’d also check for training-serving skew, where a feature is computed one way in training and another way in serving. A central feature store prevents that by serving the same value to both.',
          'Then I’d connect the signals to action: a drift alert opens a retraining pipeline; a new model version goes out as a canary with automatic rollback; and for high-stakes predictions a confidence gate declines to answer when the model is unsure, which gives up a little availability to avoid confident mistakes.',
          'I’d give the model an SLO in those terms, alongside the latency one. If quality isn’t in the objective, nobody is paged when it fails.'])],
    quiz=[['A model endpoint returns HTTP 200 quickly with a wrong prediction. What does the chapter call this?', ['A cascading failure', 'A silent failure', 'A gray failure', 'A brownout'], 1, 'The infrastructure is healthy and the model is not. That is why freshness, data quality and confidence need to be monitored as reliability signals.'],
          ['What is the main purpose of a central feature store?', ['Cheaper storage', 'Serving the same feature value in training and in production, to prevent training-serving skew', 'Faster training', 'Storing model weights'], 1, 'Skew arises when features are computed by different code paths. One source removes the difference.']],
    turn='Run <b>POC 19</b>. It computes a drift score between training and live feature distributions, checks a freshness objective, applies a confidence gate and reports how much availability it costs, and refuses to promote a model version that is unsigned or failed evaluation.',
    take=['Two mandates: build platforms for AI, and use AI to run platforms.', 'A model can be up and wrong. Monitor freshness, drift and confidence.', 'Abstract the hardware; give ML engineers pipelines, a feature store and a registry.', 'With agents operating, the platform’s job is the controls that always hold.']))

# ══════════════════════════════════════════════════════════════ 10 Education
L.append(dict(
    id='pe-10', dot='10', part='P2', nav='Education', h1='Education: why teaching belongs to the platform team',
    final=24, by='Titus Winters', poc='',
    learn=['Why a culture of learning is the root of engineering performance', 'What a computer science degree can’t cover', 'Why education fits the platform organisation, and how to staff it', 'What AI changes: documentation, specification and verification'],
    body=(
        h2('The big picture')
        + p('The chapter opens with a rule from its author that is worth memorising: if something is accidentally complex, simplify it; if it is inherently complex, educate.')
        + p('Its argument has three steps. Engineering performance comes from culture. The root of good culture is learning and growth. And somebody has to be responsible for the learning that can’t be left to chance, which is most naturally the platform organisation.')
        + h2('A culture of learning')
        + p('Management thinkers, academic researchers, Google’s own team studies and the DORA research all point the same way: culture is at the root of performance. The culture they describe is <b>psychological safety</b>, where it is safe to be wrong, safe not to know, and safe to make an honest mistake.')
        + p('The chapter makes a sharper point than “people work better when they aren’t afraid”. Safety is what lets information move and makes learning valued.')
        + note('What psychological safety does not excuse', 'A sceptic once told the author that it just lets people off for failing. His answer: it excuses <i>honest, novel</i> mistakes. Repeating the same error, or doing something plainly careless, should still count against you. The aim is that an organisation learns each hard lesson once, not once per engineer because everyone hides their failures.')
        + h3('Who gets the next task?')
        + p('An old model from the 1970s, the “surgical team”, gives the critical work to the best engineer and has everyone else support them. The chapter explains why that no longer fits, in game-theory terms. It was a strategy for a single game: assemble a team, build one system, disband. Modern engineering is an endless stream of projects with people moving between teams.')
        + flow([('Single game', 'Give everything to your best person', 'orange'), ('Endless game', 'Give the next task to the most junior engineer who can do it with some guidance', 'green')],
               'The second rule values growth, and frees senior people for new problems and mentoring.')
        + h3('Brittle productivity')
        + p('Research by Cat Hicks describes what happens without a learning culture. Only submitted code counts. Investigating, understanding and explaining look like waste. Teaching isn’t rewarded. Engineers come to define productivity as effort, hours and solitary work, which the chapter calls performative hustle. Her terms are <b>learning debt</b> and <b>brittle productivity</b>.')
        + p('It suggests a reframing borrowed from her: stop saying “developer productivity” and say “developer problem solving”. That makes it obvious that skills and understanding are the thing to build.')
        + p('Documentation is where this shows. It is the one factor in the DORA research that may matter even more than team culture, and it is the most visible, measurable sign of whether a team values the group’s output over individual output.')
        + note('A thought experiment', 'Which team would you rather lead? One that is forbidden from using any IDE or AI assistant and keeps everything else. Or one with every modern tool that can never learn anything beyond what its members were taught at university. Tools help. Without learning, engineering stops.')
        + deeper('what degrees miss, how to organise education, and AI')
        + h2('Why universities can’t do it for us')
        + ul(['<b>The field is young.</b> Certification works for disciplines that are centuries old. Software engineering is about fifty years old and still finding its best practices.',
              '<b>There aren’t enough hours.</b> All the lectures, labs and homework in a computing degree add up to less than 18 months of full-time work, and less than a third of the popular “10,000 hours to mastery” figure.',
              '<b>The content is skewed.</b> Students learn to implement a linked list more than they learn when to use one.',
              '<b>Software engineering is programming plus time plus people.</b> Version control, testing and design patterns exist to cope with change over time and with other engineers. A course can’t make either of those real.',
              '<b>Student teams aren’t teams.</b> Real teams mix experience levels, have authority structures and face a stream of work.',
              '<b>Nobody reads the code.</b> Enrolment in the US grew about fivefold in 15 years and teaching staff didn’t, so early courses are graded automatically on whether the output is right. Some graduates have never had a person comment on their code.'])
        + p('At Google a new hire’s first code review is treated as a rite of passage. It teaches the difference between “it seems to work” and “it is done to a quality we can afford to maintain”.')
        + h2('Why education belongs with the platform')
        + p('A company’s business strategy is to diversify into many products, each with its own specialists. Its infrastructure strategy should be to keep one platform. So the platform organisation is the one part of engineering that sees the whole enterprise and works on what all teams share.')
        + ul(['<b>Expertise accumulates there.</b> Being the Java expert on a team of ten is one thing. Being the person 10,000 Java engineers bring their questions to is another. That depth is learned from answering the same questions and collecting the edge cases.',
              '<b>The platform chooses what is easy.</b> If it has made one way standard, it owes people an explanation of that way. Managing the community actively beats hoping good practice spreads by itself.',
              '<b>The missions match.</b> Education increases engineering capacity and reduces waste, misuse and misconfiguration of expensive systems. That is the platform’s purpose too.'])
        + h3('How to staff it')
        + table(['Option', 'Verdict'],
                [['Everyone teaches, with targets', 'No. Good educators are rare, and the wrong person in that role does harm'],
                 ['A separate education department', 'No. It drifts away from current practice and real problems'],
                 ['Matrixed', 'Yes. On each component team, a few engineers who like to write or teach get part of their time for community support, writing up best practice, and building and delivering training. Reward it']])
        + p('The chapter compares this to how SRE treats toil. When you are tired of answering the same question, write the essay, record the talk or build the class. Done well, education reduces the support load the same way automation reduces operational load.')
        + p('Keep the scope tied to what the platform supports. A company standardised on Go, Kubernetes and a managed Git service should teach those, and should not branch into unrelated topics. For general material, <b>curate</b> instead of producing. Popularity is a poor guide: studies in physics education found that students’ own rating of how much they learned tracks how much they liked the instructor, and has little to do with measured learning.')
        + h2('Education and AI')
        + p('The chapter quotes the 2025 DORA finding that AI is an <b>amplifier</b>. It magnifies the strengths of organisations that work well and the dysfunction of those that don’t. The returns come from the underlying system: the quality of the internal platform, clear workflows, aligned teams.')
        + tiles([('Clean up your documentation', 'Your tools are internal, so a general model doesn’t know them. You point it at your docs. If they are current, the assistant is useful. If they are stale, it repeats stale answers and invents the rest. AI can’t tell an outdated page from a current one.', 'magenta'),
                 ('Teach specification', 'Writing new code is no longer the bottleneck. Describing precisely what is needed is: requirements, contracts, constraints, architecture.', 'magenta'),
                 ('Teach verification', 'The other bottleneck is checking that the result is fit for purpose: reading code, reviewing, testing, thinking critically.', 'magenta')])
        + p('Both onboarding and retraining need this. The chapter’s closing view is that software engineering can’t really be separated from education, and AI has made a long-postponed investment urgent.')),
    say='I think of education as part of the platform’s job. The platform team sees every team’s problems and decides what the standard way is, so it should also explain that way. I’d give a few engineers on each platform component real time for support, writing and teaching, and I’d treat repeated questions as toil to automate with documentation. With AI in the picture it matters more: assistants answer from our docs, and the scarce skills are now specifying what we want and verifying what we got.',
    aws='Make documentation part of the golden path: every template ships a README, a runbook and architecture notes in the repository, rendered in the developer portal. Keep them current with ownership metadata and a staleness check in CI, because that corpus is what an internal assistant (Amazon Q Business or a Bedrock knowledge base) will answer from. Scope training to what the platform supports, and curate AWS Skill Builder paths instead of writing general cloud courses yourself. Use game days and Well-Architected reviews as teaching moments, not audits.',
    iq=[('We’re rolling out AI coding assistants to 500 engineers. What would you do to make that pay off?',
         ['I’d start from the finding that AI amplifies whatever is already there. If our platform, workflows and documentation are in good shape, assistants will help a lot. If they aren’t, we’ll produce confusion faster. So part of the rollout is fixing the foundations.',
          'First, documentation. Our internal tools aren’t in any public model’s training, so the assistant will answer from our docs. I’d audit the most-used pages, delete or fix the stale ones, give every page an owner and a review date, and make the content structured enough for a machine to use.',
          'Second, guardrails in the platform, so generated code is safe by construction: safe APIs it must compile against, signed builds, policy checks at deploy. Then review doesn’t have to catch everything.',
          'Third, training, aimed at the new bottlenecks. Writing code is cheap now. Specifying precisely what we want and verifying what comes back are the scarce skills, so I’d teach requirements and contracts, code reading, review and testing, to juniors and seniors alike.',
          'Fourth, I’d protect how juniors learn. If the assistant does every task a junior would have learned from, we’ll have no seniors in five years. I’d keep giving juniors real tasks with guidance and make explaining the result part of review.',
          'I’d measure delivery metrics and satisfaction before and after, by team, and expect the gain to be largest where the foundations were strongest.'])],
    quiz=[['What does the chapter say psychological safety excuses?', ['All mistakes', 'Honest, novel mistakes', 'Repeated mistakes, as long as they are reported', 'Nothing; it is about comfort only'], 1, 'The aim is to learn each hard lesson once as an organisation. Repeated or careless errors still count.'],
          ['According to the DORA finding quoted in the chapter, what is AI’s main effect on software organisations?', ['It replaces junior engineers', 'It amplifies existing strengths and existing dysfunction', 'It removes the need for documentation', 'It makes platforms unnecessary'], 1, 'Returns depend on the underlying system: platform quality, clear workflows and aligned teams.']],
    turn='Pick the five internal documentation pages your team is asked about most. For each, record when it was last updated, who owns it, and whether its first example still runs. Fix the worst one today. Then write down the last question you answered three times, and turn the answer into a page.',
    take=['If it is accidentally complex, simplify. If it is inherently complex, educate.', 'Give the next task to the most junior engineer who can do it with guidance.', 'Education fits the platform team: it sees everything and sets the standard way.', 'AI answers from your docs, and makes specification and verification the scarce skills.']))

# ══════════════════════════════════════════════════════════════ practice material
CARDS = [
    ['Shift left vs shift down', 'Shift left finds a problem earlier and leaves it with the developer. Shift down moves the responsibility into the platform so the problem is prevented or handled by default.'],
    ['Developer ecosystem vs developer platform', 'The ecosystem is the marketplace of languages, libraries, tools and practices. A platform is an opinionated assembly from it for one kind of application, giving quality by design and by default.'],
    ['Explicit vs implicit coupling', 'Explicit: one part calls another. Implicit: no direct interaction, but one assumes the other’s existence or behaviour, such as a queue’s message format.'],
    ['Four reasons to couple on purpose', 'Efficiency, performance, atomicity, traceability.'],
    ['Four costs of coupling', 'Less reuse, less extensibility, less robustness (Hyrum’s law, cascades), less freedom of choice.'],
    ['What is retargetability?', 'Google’s word for being able to reuse part of a system for a different purpose. It is what you trade away for engineering efficiency when you couple.'],
    ['Five kinds of coupling (4+1 views)', 'Logical, development, process, physical, and scenario (linked only by a real-world event).'],
    ['Four coupling antipatterns', 'Shared database, distributed monolith, megamorphic artifacts (junk-drawer config or objects), control coupling (behaviour flags).'],
    ['Three risks of workflow engines', 'Stuck flows, orphaned state, and version skew between steps while workflows are in flight.'],
    ['Four ways to discover hidden coupling', 'Static analysis, tracing, log correlation, chaos engineering (the costliest, and the best for physical and scenario coupling).'],
    ['Six layers of platform engineering, fast to slow', 'Prototypes and experiments, products, infrastructure, technical directives, business culture, regulatory and legal.'],
    ['How do fast and slow layers relate?', 'Fast layers learn and propose. Slow layers remember and decide. Shocks are absorbed at the top.'],
    ['The core equation of shared fate', 'The more an ecosystem limits a developer’s architectural choices, the more liability it can take on for them.'],
    ['The three Rs', 'Resources the ecosystem provides, rights the developer has, responsibilities the developer keeps.'],
    ['Walled garden vs frontier contract', 'Walled garden (type 4): conformity for leverage. Frontier (types 2 and 3): autonomy for accountability.'],
    ['Resource vs guardrail', 'A resource helps and enforces nothing (a package registry). A guardrail makes the safe choice the only one (a managed dependency system that blocks bad packages).'],
    ['What is an application productivity metric?', 'Useful work a service reports, divided by the resources it used. It separates “busier” from “less efficient”.'],
    ['How are regressions from an on-by-default optimisation handled?', 'Small ones are absorbed. Large ones for a few get a per-application opt-out, which is then worked down. Opt-outs are information about real edge cases.'],
    ['Assurance vs testing', 'Assurance is confidence a property holds for every behaviour. Testing samples a tiny fraction of states, and an attacker picks the input you didn’t try.'],
    ['Three objectives of continuous assurance', 'Prevent common vulnerability classes by construction, confine residual risk to reviewed platform components, and keep the guarantee through change.'],
    ['Application archetype', 'A recurring whole-application shape. Each component brings a fragment of threat model, and the platform can own the matching security invariants.'],
    ['Risky operation', 'An operation that is safe only if a condition holds when it runs, with nothing in the language or API guaranteeing it.'],
    ['Two properties of a safe abstraction', 'Its interface puts no safety conditions on callers. Its implementation owns the conditions of the risky operations inside. So it can be verified by reading only its own code.'],
    ['Two ways to build a safe abstraction', 'A runtime check just before the risky operation, or a type invariant, where holding a value of the type is the evidence.'],
    ['SLSA build levels', 'L0 nothing. L1 provenance exists. L2 signed provenance from a hosted builder. L3 hardened: isolated builds and protected signing keys.'],
    ['What don’t SLSA build levels tell you?', 'Whether the source or its dependencies are free of vulnerabilities or malicious code. They only establish how and from what the artifact was built.'],
    ['Binary authorization', 'A deploy gate that verifies signed attestations (built by a trusted builder from the intended source, reviewed, scanned) before an artifact may run.'],
    ['Why can’t prompt injection be prevented by construction?', 'The SQL cure needs a dependable separate channel for data. Language models take instructions and data as one token stream, with no grammar to enforce a boundary.'],
    ['Three parts of safe deployment', 'Configuration as code, pre-validated blueprints, and continuous conformance verification against approved baselines.'],
    ['What is a risk profile?', 'A service’s criticality and error budget, used by the platform to set its deployment policy automatically: strict staged rollouts for critical services, a fast path for low-risk ones.'],
    ['Three tests for shifting a reliability capability down', 'Blast radius, complexity, and the cost of a mistake.'],
    ['What makes break-glass acceptable?', 'Every use is permitted and immediately logged, alerted on and reviewed. It is a feature with accountability, not a silent bypass.'],
    ['Why must the platform have stricter SLOs than its tenants?', 'It is a single point of failure. If deployment is down nobody can ship or roll back; if monitoring is down everyone is blind.'],
    ['The platform paradox', 'Technically excellent, well-funded internal platforms that still get friction and low adoption, because the experience of using them was not designed.'],
    ['Three dimensions of developer experience', 'Feedback loops, cognitive load, flow state.'],
    ['What does API-first give a platform?', 'Functional parity. The console, command line, infrastructure-as-code tools and agents are all clients of one API.'],
    ['Project vs product', 'A project has scope and an end date and succeeds by shipping on time. A product is a lasting system that succeeds by customer outcomes.'],
    ['Jobs to be done', 'Ask what the developer is trying to accomplish, not which feature they want. The job often has a better solution than the request.'],
    ['Four phases of a platform product', 'Conception with a hand-run MVP, ramp and the golden path, maturity as a town square with extension points, evolution and end of life.'],
    ['Three views of a platform scorecard', 'User (adoption, satisfaction, task success), system (reliability, cost per user or service), business (delivery metrics, time to market, compliance).'],
    ['The dual mandate for AI', 'Build platforms for AI (MLOps) and use AI to run platforms (AIOps).'],
    ['Three AI-specific reliability signals', 'Model freshness, data quality and drift, and probabilistic correctness through confidence thresholds.'],
    ['Winters’ rule on complexity', 'If it is accidentally complex, simplify. If it is inherently complex, educate.'],
    ['Who should get the next task?', 'The most junior engineer who can do it with some guidance. Engineering is an endless game, so growth has value.'],
]

DRILLS = [
    ['Explain “shift down” to a sceptical engineering director who thinks shift left already covers it.',
     '<p>Shift left moves a check earlier. A scanner in the editor instead of in the pipeline, or training before the code is written. The developer still has to notice the problem and fix it, every time, and we’re relying on their attention.</p>'
     '<p>Shift down changes who is responsible. The platform takes the problem on, so the developer can’t make the mistake or never has to think about it. A typed query API means SQL injection doesn’t compile. A standard pipeline means every deploy gets canary analysis without anyone configuring it.</p>'
     '<p>The economics are different too. Shift left costs every developer a little, forever, and its effectiveness has a ceiling because tools miss things and people tune out warnings. Shift down costs a platform team once, and then every application inherits the result. Google’s examples are no SQL injection in protected applications for more than ten years, and fleet-wide CPU savings from one allocator change.</p>'
     '<p>It isn’t free. We give up some choice, and the platform team commits to maintaining those abstractions. So I’d apply it where the stakes justify it: wide blast radius, rare expertise, or catastrophic mistakes. For the rest, shift left is fine.</p>'],
    ['Design a secure-by-default path to production for a team building a new web service on AWS.',
     '<p>I’d start from the invariants I want every service of this shape to hold, then pick a component to own each one.</p>'
     '<p>In the code: a memory-safe language, a typed query layer so queries are built only from constants with bound parameters, and a framework that sets security headers and enforces authentication before handler code. A CI check bans the raw alternatives.</p>'
     '<p>In the build: a hosted, isolated build that produces a signed artifact with provenance, dependencies served only from a curated repository, and vulnerability scan results attached as attestations.</p>'
     '<p>At deploy: a gate that verifies signature and attestations before anything runs, infrastructure from a reviewed blueprint (TLS, least-privilege role, network policy, multi-zone), and policy checks that block drift from it. Rollout follows the service’s risk profile, with alarms that roll back automatically.</p>'
     '<p>At runtime: workload identity with least privilege, central TLS termination, standard telemetry, and security signals emitted by the framework so I can see across the fleet which services have the protections active.</p>'
     '<p>For emergencies there is a break-glass route that works and is loud: logged, alerted and reviewed.</p>'
     '<p>The team writing the service sees almost none of this. They instantiate a template and write business logic. That is the test of whether I’ve done it well.</p>'],
    ['Leadership wants proof that the platform team is worth its headcount. What do you show them?',
     '<p>I’d show three views, in order, and I’d compare teams on the platform with teams off it wherever I can.</p>'
     '<p>First, whether developers use it. Active adoption and retention, time from a new repository to a first production deploy, and how often that works first time without help. If these are poor, I’d say so, because nothing else counts until they improve.</p>'
     '<p>Second, whether it is healthy and affordable. The platform’s own SLOs, and cost per active service. I’d flag it myself if cost per service is rising without more adoption or capability.</p>'
     '<p>Third, what it does for the business. Lead time, deployment frequency, change failure rate and recovery time for adopters against non-adopters. Security posture: the share of services with signed builds and no raw risky APIs. And the avoided cost: capabilities like canary analysis or multi-zone placement that twenty teams didn’t each have to build.</p>'
     '<p>I’d avoid totals that sound impressive and mean little, like the number of deployments. And I’d bring one concrete story of a team that shipped something faster or avoided an incident because of the platform, since numbers land better with a case attached.</p>'],
]

AWS_ROWS = [
    ['Loose coupling patterns', 'Publish-subscribe, pipelines, federation, fail open', 'SNS, EventBridge, MSK, Kinesis, Step Functions, IAM Identity Center, AppConfig defaults', 'POC 12'],
    ['Finding hidden coupling', 'Static analysis, tracing, log correlation, chaos', 'X-Ray and Application Signals service map, CloudTrail data events, Logs Insights, Fault Injection Service', 'POC 12'],
    ['Layers and directives', 'Different rates of change for experiments, products, platform and policy', 'Organizations OUs, sandbox accounts, Service Control Policies, Config conformance packs, Audit Manager', ''],
    ['Shared responsibility inside the company', 'Resources, rights, responsibilities by ecosystem type', 'Control Tower guardrails, Security Hub scores per account, CodeArtifact, coverage dashboards', 'docs/platform'],
    ['Fleet efficiency', 'Profiling, on-by-default optimisation, work per unit of resource', 'Cost and Usage Reports, Compute Optimizer, a continuous profiler, CloudWatch metric math, Graviton by default', 'POC 17'],
    ['Safe Coding', 'Safe abstractions and conformance checks', 'Typed wrapper over the RDS Data API or driver, CI rule against raw queries, Amazon Q Developer for migration', 'POC 13'],
    ['Supply chain', 'Provenance, signing, deploy gate, break-glass', 'CodeBuild, AWS Signer, ECR image signing, Lambda code signing, Kyverno or Gatekeeper on EKS, Inspector, CloudTrail', 'POC 14'],
    ['Safe deployment', 'Configuration as code, blueprints, conformance', 'CDK or Terraform modules, CloudFormation Guard, Service Catalog, Config rules, Security Hub', 'POC 15 · POC 10'],
    ['Identity and authorisation', 'Workload identity, mutual TLS, central fine-grained authorisation', 'IAM roles, EKS Pod Identity, VPC Lattice, Verified Permissions, Identity Center', ''],
    ['Web security controls', 'TLS, isolation and injection controls set once', 'CloudFront response headers policy, ACM, ALB, WAF', ''],
    ['Risk-profile rollouts', 'Deployment strictness set by service tier and budget', 'CodeDeploy deployment configurations, AppConfig strategies, CloudWatch alarms, Route 53 ARC safety rules', 'POC 16 · POC 05'],
    ['Platform SLOs', 'Stricter objectives for the platform itself', 'CloudWatch SLOs on pipeline success, deploy latency, telemetry lag', 'POC 16'],
    ['Developer experience and product', 'Golden paths, one API, scorecard, deprecation', 'Backstage or Service Catalog, shared CDK constructs, EventBridge pipeline events, cost allocation tags', 'POC 18'],
    ['Platforms for AI', 'Pipelines, feature store, registry, drift, guardrails', 'SageMaker Pipelines, Feature Store, Model Registry, Model Monitor, Bedrock Guardrails, Nitro Enclaves', 'POC 19'],
    ['AI for platforms', 'Correlation, prediction, assisted and automated response', 'CloudWatch anomaly detection and investigations, DevOps Guru, predictive scaling, agents bounded by IAM and SCPs', 'POC 11'],
]
