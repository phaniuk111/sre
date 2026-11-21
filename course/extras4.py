# Rewritten model answers for the SRE lessons.
# The first version compressed each answer into one dense paragraph of shorthand. These say
# the same things the way you would say them aloud: answer first, then why, then how, with
# jargon explained the first time it appears.

IQ = {}

IQ[1] = [('How is SRE different from DevOps?', [
    'DevOps is a culture: developers and operations share responsibility for running software, instead of developers “throwing code over the wall”. It tells you what to value but not exactly how to do it.',
    'SRE is one concrete way to do it. It turns the culture into mechanisms you can point at. <b>SLOs and error budgets</b> decide, with numbers, when to ship faster and when to slow down for reliability. A <b>cap on toil</b> (at least half of the team’s time goes on engineering) stops operations work from swallowing the team. <b>Blameless postmortems</b> turn failures into fixes. And SREs write software to automate operations away.',
    'The book adds one more difference: SRE is a role. A small company can use these mechanisms without hiring SREs. At scale, a dedicated team gives reliability a voice that the next feature deadline can’t drown out.',
    'A one-line version: DevOps says “share responsibility”; SRE says “here is the budget, the policy and the team that make shared responsibility work”.'])]

IQ[2] = [('Your CTO asks why she should fund an SRE team. What do you say?', [
    'I wouldn’t start with the team. I’d start with what unreliability costs her today, in her terms.',
    'First, what is at stake. How much revenue does a minute of checkout downtime lose? Do users retry, or leave for a competitor? When are the peak periods, and what would an outage then cost?',
    'Second, the hidden cost. The book’s point is that one hour of major downtime costs 100 to 1,000 engineer-hours once you count the response, the review, internal communication, customer communication and the fixes. Many companies spend a large share of engineering time on incidents and repetitive operations without measuring it. Google reports production work under 15% of engineering time, with SRE under 4% of headcount.',
    'Third, a small proposal with a measurable result. One or two SREs on the most critical service for a quarter: define SLOs, make alerts actionable, cut the top sources of toil, and add safe rollouts with rollback. Then report the change in incidents, time to mitigate, and how much developer time came back to features.',
    'That turns “fund a team” into “fund an experiment with a clear success test”, which is much easier to approve.'])]

IQ[3] = [('Why aren’t RTO and RPO enough as reliability metrics?', [
    'Because they only describe disasters. RTO (recovery time objective) says how fast you’ll be back after a catastrophe; RPO (recovery point objective) says how much data you can lose. Both assume the service is either up or down.',
    'Most real failures aren’t like that. Checkout is slow for 10% of users. One feature is broken in one region. Searches succeed but return nothing. RTO and RPO have nothing to say about any of these, and they only start counting after things have gone badly wrong.',
    'SLOs on critical user journeys fill that gap. They measure continuously, from the user’s side, so a partial degradation shows up as error budget being spent. You can act before it becomes an outage.',
    'So I’d keep RTO and RPO for what they’re good at, which is disaster recovery and data protection planning, and use SLOs for everyday reliability.'])]

IQ[4] = [
    ('An engineer ran a command that took down production. How do you handle the postmortem?', [
        'I’d run it blameless, which means the goal is to understand why the action made sense to them at the time, not to find someone to punish.',
        'I’d reconstruct their view: what did they believe about the system? What did the tool show them, and what did it not show? Were they under time pressure? Why did nothing stop a command with that much blast radius?',
        'The answers usually point at the system, so the fixes go there: a dry-run mode, a confirmation step when a command affects many hosts, least-privilege access so one person can’t take everything down, and applying changes progressively instead of everywhere at once.',
        'Accountability still exists. It means the people closest to the incident help design and own the fixes. Discipline is only for reckless or malicious behaviour, which is rare. If people fear punishment, they hide mistakes, and you lose the information you need.']),
    ('Our new SRE team keeps getting blamed after outages. What would you change?', [
        'That is a culture problem, and it will kill the SRE team if nothing changes.',
        'First I’d name it. The book uses Westrum’s three culture types: pathological (power-oriented), bureaucratic (rule-oriented) and generative (performance-oriented). Blaming whoever was holding the pager is a sign of the first two.',
        'Then I’d change how postmortems are run: blameless, written by someone not involved, focused on contributing factors, with actions owned by the teams who can fix them. I’d get one senior leader to model it visibly, because people copy what leaders do.',
        'I’d also check one thing: did the organisation just rename an operations team to “SRE” without giving it the power to say no, such as an error budget policy? If so, fix that too. Otherwise the label takes the blame and the idea gets discredited for years.'])]

IQ[5] = [('How would you onboard a new SRE onto your team’s on-call rotation?', [
    'I’d build confidence step by step, so their first real page isn’t their first time seeing the system break.',
    'Week one: a checklist of systems, dashboards and playbooks to work through, plus a small starter project that isn’t urgent, so they learn the code and tools by doing.',
    'Then practice: “Wheel of Misfortune” sessions, where we replay a past incident and they play the on-caller while a teammate plays the system. They also give short whiteboard talks explaining a system back to the team. Teaching it is the best test of understanding it.',
    'Then real on-call in two steps: shadowing, where they watch the primary on-caller, then reverse shadowing, where they lead and the experienced person watches and steps in if needed.',
    'They go primary once they can handle the top five failure modes from the playbooks. I’d measure their confidence with a short survey before, after and a few months later, because the book uses confidence as the evidence that training worked.'])]

IQ[6] = [
    ('Centralised or embedded SRE? Defend a choice.', [
        'For an organisation starting out, I’d centralise first.',
        'Expertise is scarce at the start. A central team can set the common standards everyone needs: how SLOs are defined, the alerting approach, the deployment pipeline, the incident process. If you scatter the first few SREs across product teams, each one reinvents those alone.',
        'Once one or two products are critical enough to justify dedicated people, I’d embed SREs with them. Embedded SREs learn the product deeply and are close to the developers.',
        'Two safeguards make that work. Embedded SREs keep reporting through the SRE line, so they keep their reliability voice and a career path, and don’t become the product team’s operations staff. And a community of practice across all SREs, so a fix one of them makes becomes a standard for everyone.',
        'I’d revisit the balance every year or so. The book is clear that any model drifts as the organisation grows.']),
    ('Leadership wants a reliability scorecard that ranks teams. What do you think?', [
        'Measuring is good: things nobody measures tend to get worse. Ranking is the problem.',
        'Two things go wrong, and the book names both. When numbers are used to judge without understanding a team’s situation, people become afraid, and psychological safety suffers. And when a number becomes a target, people game it. The book’s example: if you score deployment frequency, a team can redeploy the same binary every hour.',
        'So I’d offer a version that coaches instead of ranks. Score several areas of health, not one number. Have reviewers outside the team’s management chain, who understand the context. Use the result to agree each team’s next improvement, not to name winners and losers.',
        'And I’d keep listening to the stories behind the numbers. When the data and the anecdotes disagree, the anecdotes are often right.'])]

IQ[7] = [
    ('A product team wants you to “just take the pager”. How do you respond?', [
        'I’d say no to that version, and offer something better.',
        'If SRE simply takes over on-call, the developers stop feeling the pain of their own failures. Nothing in the code improves, SRE becomes a human buffer, and the pager gets worse over time. The book treats this as an antipattern.',
        'What I’d offer is a partnership with agreed outcomes. Together we set SLOs for the service. We fix the top sources of pages first. We add progressive rollouts and playbooks. Then we share on-call: either one combined rotation, or SRE takes infrastructure problems while developers take application problems.',
        'And one rule up front: if the page load stays above an agreed level, some of it goes back to the developers until the causes are fixed. That keeps the feedback loop alive.']),
    ('SRE is drowning in services it inherited. How do you fix the engagement model?', [
        'Stop treating every service the same, and choose deliberately.',
        'Split the work in two. Foundational offerings are things every service gets with little SRE time: the platform, templates, documentation, office hours. Outcome-based engagements are where SREs work directly on one service towards a specific result, such as “cut pages by half” or “add multi-region failover”.',
        'Rank the possible outcomes with development leadership, staff only the top few, and time-box each one. When an engagement finishes, the SREs move on.',
        'For low-priority services the team inherited, plan a handback: train the developers, give them playbooks and alerts that make sense, and return the pager. Decouple on-call from team structure so one team doesn’t carry rotations for dozens of services it can’t improve.'])]

IQ[8] = [('Walk me through setting an SLO and alerting for a new checkout API.', [
    'I’d start from the user, not from the server.',
    '<b>1. The journey.</b> What does the user do? Add to cart, then pay. Checkout working means the payment request succeeds and is fast enough.',
    '<b>2. The target, agreed with product.</b> For example: 99.9% of valid checkout requests succeed, and 99% finish in under 300 ms, measured over a rolling 30 days. “Valid” excludes things like malformed requests from a buggy client.',
    '<b>3. The budget.</b> 99.9% over 30 days allows 0.1% failures, which is about 43 minutes of full downtime. That budget is what the team can spend on risk.',
    '<b>4. Where to measure.</b> At the load balancer or frontend, so it includes everything behind it, plus a synthetic probe that runs the whole flow every minute.',
    '<b>5. Alerts on burn rate,</b> meaning how fast the budget is being used. Page someone if 2% of the monthly budget is gone in an hour (a burn rate of 14.4), confirmed by the last 5 minutes so it stops paging once fixed. Open a ticket for slower burns. If traffic is low, require statistical confidence before paging, or one failed request will wake someone up.',
    '<b>6. A policy.</b> Write down what happens when the budget runs out: releases limited to fixes, and the next sprint goes to reliability. Agree it before you need it.',
    'On AWS: CloudWatch Application Signals for the SLO, CloudWatch Synthetics for the probe, and burn-rate alarms. POC 01 builds this.'])]

IQ[9] = [('What’s the difference between monitoring and observability, and how would you roll out observability on AWS?', [
    '<b>Monitoring</b> answers questions you thought of in advance. You decided beforehand that error rate matters, so you built a graph and an alert: “is the error rate above 1%?”. It tells you <i>that</i> something is wrong.',
    '<b>Observability</b> lets you answer questions you didn’t think of in advance, during an incident, without shipping new code. For example: “Are the failing requests all from the new mobile app version, in one region, for customers with large baskets?” If your telemetry carries enough context, you can slice it that way on the spot. It helps you find <i>why</i>.',
    'The book’s test is practical: can someone without tribal knowledge form a hypothesis, check it and rule it out quickly? If only the person who built the service can debug it, you have monitoring but not observability.',
    'How I’d roll it out on AWS:',
    '<b>1. One standard way to emit telemetry.</b> OpenTelemetry, an open standard for metrics, logs and traces, deployed through ADOT (the AWS Distro for OpenTelemetry). One SDK in every service means one format everywhere and you can change backends later.',
    '<b>2. Make signals joinable.</b> Every metric, log line and trace carries the same identity tags (service name, version, environment, region) and the trace ID. Then you can jump from an alert to the logs of the exact failing request. These shared tags are what the lesson calls resource identity and trace context.',
    '<b>3. Put high-detail data in the right place.</b> Don’t put user IDs or request IDs on metrics: every unique value creates a new time series, and cost explodes. Keep them in logs and traces, which are built for that detail.',
    '<b>4. Alerts first, on what users feel.</b> SLO-based alerts on critical journeys, plus automatic first checks (recent deploys, error breakdown by region) attached to each page.',
    '<b>5. Keep alerting independent.</b> Alerts must not depend on the system they watch. If the service and its monitoring share fate, both go dark together.',
    'In AWS services: ADOT collectors, CloudWatch metrics and Application Signals for SLOs, X-Ray for traces, CloudWatch Logs Insights for questions you didn’t plan, and CloudWatch RUM and Synthetics for the user’s view. POC 02 sets this up.'])]

IQ[10] = [
    ('You’re paged at 3am: checkout errors are spiking. What do you do in the first 15 minutes?', [
        'Priority one is stopping the damage, not understanding it. Diagnosis can wait until users are safe.',
        '<b>Minutes 0–2.</b> Acknowledge the page so nobody else is woken for the same thing, and take the incident commander role until someone else does.',
        '<b>Minutes 2–5.</b> Size it. Check the SLO dashboard and probes: which journeys are failing, what share of users, which region or availability zone?',
        '<b>Minutes 5–10.</b> Ask what changed. Deploys, config pushes, feature flags, dependency incidents. If a change lines up with the start of the errors, roll it back now, without proving it was the cause first. Rollback is cheap and safe; debugging at 3am is slow. If the problem is confined to one zone, move traffic away from it (on AWS, a zonal shift).',
        '<b>Minutes 10–15.</b> If it isn’t contained, get help explicitly: page the service owner and a second responder, hand communications to someone, and split the work into named hypotheses with one owner each. Post a first update to stakeholders: what we know, what we’re doing, when the next update comes.',
        'Throughout, say each mitigation out loud in the incident channel and watch the SLO graph to see whether it worked.']),
    ('Your incident has 60 people on the bridge and no progress. What do you do?', [
        'Sixty people is a coordination failure, not a staffing success. The book cites research showing the cost of coordination is often what slows incidents down.',
        'I’d restructure: one incident commander who stops doing hands-on work, an operations lead who directs the fixing, and a communications lead who handles all updates.',
        'Split the problem into child incidents, each with its own lead and small team, for example “database latency” and “payment provider errors”.',
        'Give everyone else a specific task or release them. People who are only watching add noise and ask for updates.',
        'Set a fixed update rhythm, such as every 20 minutes, so people stop interrupting the responders. If the decisions span several organisations, escalate to a senior incident coordinator.'])]

IQ[11] = [
    ('How do you make sure postmortem action items actually prevent recurrence?', [
        'Most postmortems fail after they are written: the action items quietly expire. So I’d manage them like real work.',
        'Every item traces back to a specific contributing factor in the analysis, so nobody adds generic “be more careful” items.',
        'Sort them into four kinds: <b>prevent</b> (stop it happening), <b>detect</b> (notice it faster), <b>mitigate</b> (shorten it) and <b>process</b>. Many teams write only prevention items; the detection and mitigation ones often pay off more.',
        'Each item has one owner and a due date, and completion is reviewed every week in the production meeting and in leadership reliability reviews. Overdue items are visible.',
        'Finally, look across incidents, not only within one. Google’s line is that there are rarely new outages, only new instances of old ones. A regular digest of postmortems helps spot the same pattern in other services and fix it there too.']),
    ('What makes a postmortem good?', [
        'Five things.',
        'An author who wasn’t directly involved, so the account isn’t defensive.',
        'A complete timeline, including when people were told, not only what the system did.',
        'Several contributing factors, across people, process and technology. A single “root cause” usually means the analysis stopped too early.',
        'An honest section on what went well and where we got lucky. Luck is a risk you haven’t fixed.',
        'Action items sorted into prevent, detect and mitigate, each with an owner. The real proof is the follow-up: the next similar incident was shorter or smaller. The book has an example of exactly that, comparing how two similar regional incidents went.'])]

IQ[12] = [
    ('What would STPA find that a traditional design review would miss?', [
        'A design review checks each component against good practice: is the database replicated, does the service have timeouts. STPA (system-theoretic process analysis) looks at how components control each other, and what each one believes about the others.',
        'That finds a different kind of problem: failures where nothing is broken. For example, an automated deployer promotes a release because a health signal is missing, and it treats “no data” as “healthy”. Or two teams each assume the other one is approving a change, so nobody does.',
        'It has three advantages. It doesn’t rely on someone happening to imagine the failure, because the method walks every control action systematically. It works before any code exists. And fixing a design flaw at the design stage is far cheaper than fixing it in production.',
        'The book’s example: STPA on one Maps system produced 34 recommendations, against 7 from the earlier postmortem.']),
    ('Nothing broke, but users got wrong data. How do you analyse that?', [
        'I’d use CAST, which is STPA applied backwards to an incident that already happened.',
        'Map the control structure: who and what decided the data was ready to publish, and what information did each of them have?',
        'Then find where someone’s mental model was wrong and why feedback didn’t correct it. The book’s example is a dataset of US city names: reviewers checked a sample of four states, the errors were in six other states, and nothing told them the sample wasn’t representative.',
        'Then go up to systemic factors: time pressure, incentives, how the review process drifted over time.',
        'The recommendations should remove the whole class of problem, for example continuously checking whether the assumptions behind a design still hold, not just fixing the one bad dataset.'])]

IQ[13] = [
    ('Your team restarts a stuck worker 60 times a month. Do you automate the restart?', [
        'Not as the first move. Automating the restart hides the defect, and you end up building more automation on top of something broken.',
        'First measure the toil, then find the cause with the developers: a memory leak, a deadlock, a dependency that hangs. Fix that.',
        'If the real fix will take weeks, an automatic restart is fine as a temporary measure, with conditions. It is rate-limited, so it can’t restart in a loop. It raises an alert and logs every restart, so the problem stays visible. And it has an expiry date and a ticket for the real fix.',
        'Then count the restarts and track them down to zero.']),
    ('Should we auto-restart the service when memory goes above 90%?', [
        'It depends on how often it happens and which way it’s heading.',
        'Yes, as a tactical measure, if the leak is rare and expensive to fix: rate-limit the restarts, alert on each one, and keep a ticket open for the real fix.',
        'No, if restarts are becoming more frequent than releases. Then the automation is hiding growing technical debt, and one day it will restart everything at once.'])]

IQ[14] = [
    ('How do you decide whether a canary is healthy?', [
        'A canary is a new version serving a small share of real traffic. The question is whether it is worse than the current version, so you need a fair comparison.',
        'Compare it with a <b>control</b>: a few instances of the current version, started at the same time and given the same share of traffic. Comparing with the whole fleet is unfair, because fresh instances behave differently from long-running ones.',
        'Use statistics, not eyeballing: a test on error rate, a comparison of the whole latency distribution (not only the average), and the business metrics of the journeys that matter.',
        'Require a minimum number of requests. A canary that got almost no traffic is <i>inconclusive</i>, not healthy.',
        'Look at it from the callers’ side as well, because a new version can return “success” with bad data. Bake long enough to see the normal traffic mix and a peak. If it fails, roll back automatically.',
        'On AWS: CodeDeploy canary deployments with CloudWatch alarms for automatic rollback. POC 05 implements the comparison.']),
    ('How do you stop configuration pushes from causing outages?', [
        'Treat configuration exactly like code, because config changes cause as many outages.',
        'Check it in layers before it ships: <b>syntax</b> (does it parse?), <b>semantics</b> (is a limit set to zero, did a value change by 300 times, is a new port exposed?) using policy-as-code, and a <b>dynamic</b> test that actually starts something with the new config.',
        'Roll it out progressively with a canary comparison, like a binary. Detect drift between what’s running and what’s committed.',
        'Keep an emergency path for urgent changes that still validates them and records them afterwards. And keep the last good config ready so you can switch back instantly.'])]

IQ[15] = [
    ('How many instances do you need for 9,000 requests a second at peak, if one instance handles 100 within the SLO, across three availability zones?', [
        'Work it out in three steps, out loud.',
        '<b>1. Headroom.</b> Don’t plan to run instances at 100%: latency rises sharply near the limit. Target about 70%, so each instance carries 70 requests a second. 9,000 ÷ 70 ≈ 129 instances.',
        '<b>2. Survive losing a zone.</b> If one of three zones fails, the other two must carry everything without waiting for autoscaling. So two zones need 129 between them: 65 each. Three zones of 65 is 195 instances.',
        '<b>3. Check it.</b> At peak, with all zones up, the fleet runs at 9,000 ÷ (195 × 100) ≈ 46%. That looks wasteful, but it is the price of surviving a zone loss.',
        'Then the insight that impresses interviewers: the extra capacity for losing one of N zones is 1 ÷ (N − 1). With three zones that’s 50%. Spread across six cells, it drops to 20%. More, smaller failure domains are cheaper.']),
    ('We expect 10 times normal traffic for a one-off event in six weeks. What do you do?', [
        'Treat it as a planned incident with six weeks of preparation.',
        'Map every dependency, including third parties, and ask each one whether it can take 10 times the load.',
        'Load-test until throughput stops rising, to find the real bottleneck before the event does.',
        'Buy the capacity in advance. Don’t rely on autoscaling during the spike, because it reacts too late and the capacity may not be available.',
        'Build and test ways to degrade gracefully: switch off expensive features, and shed low-priority traffic first so checkout survives. Then staff the event like an incident, with roles and a war room.'])]

IQ[16] = [
    ('We use DynamoDB global tables across two Regions, so we don’t need backups. Right?', [
        'No. Replication and backups protect against different things.',
        'Global tables protect you if a whole Region fails: the other Region has a copy.',
        'But replication copies <i>everything</i>, including mistakes. If a bad deploy corrupts items, or someone deletes data by accident, that change reaches the other Region within seconds. Now both copies are wrong.',
        'You still need three things. Point-in-time recovery, to rewind the table to just before the corruption. Separate backups in a different account with a locked vault (AWS Backup with Vault Lock), so an operator mistake or an attacker can’t delete them. And regular restore tests, because a backup you have never restored is only a hope.']),
    ('Design backups for a new orders database.', [
        'Start with the business, then the tooling.',
        'Classify the data and get the business to set three numbers: <b>RPO</b>, how much data we can lose; <b>RTO</b>, how long until we’re back (counted from when the problem starts, so detection time is included); and how far back we must be able to go, which the book calls RWO and which deletion laws may limit.',
        'Then cover each kind of failure. Point-in-time recovery for bad writes. Locked, cross-account backups for operator mistakes and ransomware. Cross-Region copies for losing a Region.',
        'Automate restore tests that also check the restored data makes sense, for example that order totals add up. Write the recovery policy down and get leadership to sign it. POC 08 covers this.'])]

IQ[17] = [
    ('Explain how a retry storm becomes an outage, and how you’d prevent it.', [
        'It is a feedback loop that keeps going after the original cause is gone.',
        '<b>How it happens.</b> A traffic spike makes the server slow. Requests wait in queues until their callers give up, but the server still processes them: wasted work. Each caller retries, and often every layer of the stack retries too, so one user click becomes many requests. Load climbs further, health checks fail, instances restart and caches go cold. Now the system can’t recover even when the spike ends. The book calls this a metastable failure.',
        '<b>How to prevent it, on the server.</b> Keep queues short and reject early with a clear “overloaded, retry later” or “overloaded, don’t retry”. Pass deadlines along with requests so nobody works on something the caller has abandoned.',
        '<b>On the client.</b> Exponential backoff with random jitter, so retries spread out. A retry budget, for example retries may add at most 10% to normal traffic. Adaptive throttling, so a client backs off when it sees many errors. Retry at one layer only.',
        '<b>Priorities.</b> Label requests by importance so checkout survives while batch jobs are dropped.',
        '<b>In an emergency.</b> Turn off automatic restarts and bring capacity back gradually, so the system isn’t knocked over again as it starts up.']),
    ('Your chat and video tools are down during an outage. Now what?', [
        'Switch to the emergency plan you agreed beforehand, which is the point: this has to be prepared before the day.',
        'Use the fallback channel: a phone bridge or a separate chat system that doesn’t depend on your own infrastructure. Use offline copies of playbooks and a contact list.',
        'Use break-glass access if normal access is down, with more than one person approving and everything logged.',
        'In the interview, add that you’d prove all of this in drills, starting with the most important journeys, because an emergency path nobody has used tends not to work.'])]

IQ[18] = [
    ('Teams keep bypassing your platform. What do you do?', [
        'Treat it as product feedback, not disobedience.',
        'Find out what they’re doing instead and why. The book calls these “desire paths”, like the trodden path across a lawn. Is a feature missing? Is the platform slower or harder than the workaround? Is there a use case nobody planned for?',
        'Make the paved road cheaper than the workaround: templates, good defaults, faster provisioning.',
        'Offer an official escape hatch for genuine special cases, recorded with an owner and an expiry date, so exceptions stay visible.',
        'Use hard blocks only for actions that are genuinely unsafe. Then measure adoption, developer satisfaction and incidents for teams on the platform against teams off it.']),
    ('How do you roll out a new reliability policy to 500 services?', [
        'Make compliance automatic for most services and visible for the rest.',
        'Encode the policy as an automated check. Make the platform’s defaults compliant, so new services pass without effort. Block new violations from the day it starts.',
        'For existing services, grant automatic exemptions with a reason and an expiry date, so nothing breaks on day one but nothing is exempt forever.',
        'Publish a clear rollup of who complies, fix things automatically where that’s safe, and choose how hard to push based on risk. POC 10 does exactly this.'])]

IQ[19] = [('How should SRE adapt to the volume of AI-generated code?', [
    'Assume much more change is coming, and strengthen the safeguards that don’t care who wrote the code.',
    'Reviewers can’t read everything, so production-side protection matters more: progressive rollouts with automatic statistical canaries, monitoring of critical user journeys during every change, feature flags, and rollback that is fast and tested.',
    'Use stronger checks where they pay off: specifications, tests generated from them, and formal methods for the most critical parts.',
    'Use AI on the defensive side too, for review and incident investigation, inside guardrails.',
    'And keep humans in practice with drills, so people can still take over when the automation is wrong. The book also warns about “roll-forward pressure”: with so many changes, people prefer fixing forward to rolling back, so make every change easy to reverse.'])]

IQ[20] = [('Define SLOs for an LLM-powered support chatbot.', [
    'Four kinds, because a chatbot can fail in four different ways.',
    '<b>Availability.</b> 99.9% of conversations get a response without a server error.',
    '<b>Latency.</b> 95% of responses start within 1.5 seconds (time to first token), and text streams faster than a minimum number of tokens per second. Users feel both.',
    '<b>Quality.</b> This is the one people forget: a fast, successful answer can be wrong. Sample real conversations, score them weekly with an evaluation suite (a judge model plus human spot checks), and keep the score at or above an agreed baseline. If the system falls back to a smaller model, count that as degraded.',
    '<b>Safety.</b> Zero personal-data leaks in a sampled audit.',
    'Then act on them: alert when the distribution of answers drifts, and roll back the model version automatically if quality drops. POC 19 implements the quality and drift checks.'])]

IQ[21] = [('Would you let an AI agent roll back production? Under what conditions?', [
    'Yes, but it has to earn that permission, one kind of action at a time.',
    'The book describes levels of autonomy. Start at L1: the agent investigates and suggests. Move to L2: it proposes a rollback with its evidence, and a human approves. Allow L3, acting without approval, only for one narrow situation, such as a clear statistical regression right after a deploy, and only after replayed past incidents show it gets that situation right almost every time.',
    'Guardrails stay on at every level. The action must be reversible. The agent checks the result straight away and undoes it if things got worse. Everything is logged. Its permissions cover only what it needs. And there is a kill switch.',
    'Promote it scenario by scenario, never in general. POC 11 implements these gates.'])]

IQ[22] = [('You’re the first SRE at a 40-engineer startup. What are your first 90 days?', [
    'Earn trust by fixing real pain first, then build the foundations.',
    '<b>Weeks 1–2.</b> Join every incident and fix the failure that happens most often. That shows value fast.',
    '<b>Weeks 3–6.</b> Make the system visible: logs, metrics and traces in one place, and alerts on symptoms users feel. Make deploys automatic with one-click rollback, because changes are usually the biggest cause of outages. Write playbooks for the last few incidents.',
    '<b>Weeks 7–12.</b> Agree two or three SLOs with the founders and product. Start a shared on-call rotation with the developers instead of taking the pager alone. Require review for every change.',
    'Report progress with numbers: fewer incidents, faster mitigation, safer deploys. The book’s startup example cut downtime on critical journeys by about 60% in six months this way.'])]

IQ[23] = [('How will SRE change over the next five years?', [
    'The book’s answer is that the principles stay and the work changes.',
    'There will be far more change, because AI will produce far more code. Releasing it the old way would pack more changes into each release and make every release riskier. So releases become many small, heavily automated steps.',
    'The work shifts from doing to supervising. Agents investigate, detect and mitigate; humans handle novel problems and set the guardrails. The authors call this moving from human-centric to human-supervised operations, and say SREs will be “automating themselves into jobs, not out of them”.',
    'The fundamentals that remain: user-focused SLOs, reliability built into platforms by default, and treating risk as a leading indicator instead of waiting for outages.',
    'In an interview, finish with what you’d do now: make every change reversible, invest in the platform, and practise the skills you’d need if the automation fails.'])]
