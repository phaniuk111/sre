# Platform Engineering at Google: study notes

Notes in my own words on the O’Reilly early release (ISBN 9781098169428). Ten chapters were published when these were written, out of a planned thirty-one; the notes cover those ten and nothing else. Chapter numbers are the ones planned for the final book. The interactive version, with diagrams, quizzes and flashcards, is the course artifact linked from the README. These notes don’t replace the book.

## Platform engineering: the second book on the map

### The argument in one paragraph

Every engineering organisation wants the same things from its software: secure, reliable, efficient, compliant. The usual way to get them is to ask every developer to remember every rule. That fails at scale, because developers are human and there are never enough experts to check their work.

Platform engineering takes the opposite route. It moves those responsibilities **down** into the things developers already build on: languages, libraries, frameworks, build systems, deployment pipelines, runtime infrastructure. Experts solve a problem once, inside the platform, and every team inherits the answer. The book calls this **shifting down**. It is different from shifting left, which moves the same work earlier but leaves it with the developer.

1.  **Shift left**: Find the problem earlier. The developer still has to find it
2.  **Shift down**: Make the problem impossible, or handled by default, in the platform

*Shift left reduces the cost of each mistake. Shift down reduces the number of mistakes that can be made.*

If you finished the SRE lessons, you met this idea in chapter 18, with its 0-to-4 scale from YOLO to Assured. This book is the long version, written by the people who built Google’s internal platforms.

### What is in the early release

The book is still being written. O’Reilly publishes chapters as they are drafted, so the numbering you see online is temporary. Ten chapters are available. I read all ten in full, and all five figures. The other twenty-one are listed in the table of contents and can’t be read yet, so they are not in this course.

| Lesson | Topic                              | Final chapter | Author                                |
|--------|------------------------------------|---------------|---------------------------------------|
| 1      | Coupling                           | 9             | Michelle Brush                        |
| 2      | Layers                             | 10            | Kaan Kivilcim                         |
| 3      | Shared fate and responsibility     | 12            | Andy Qin                              |
| 4      | Deep dive: efficiency              | 14            | Chris Kennelly                        |
| 5      | Deep dive: security                | 15            | Christoph Kern                        |
| 6      | Deep dive: reliability             | 16            | Bharath Modhipalli and Michelle Brush |
| 7      | Why developer experience matters   | 18            | Eric Maxwell                          |
| 8      | Platform as a product              | 19            | Eric Maxwell                          |
| 9      | AI with platform engineering       | 22            | Isaac Albarran with Konrad Dryja      |
| 10     | Education and platform engineering | 24            | Titus Winters                         |

> **What you can’t read yet.** Chapters on what platform engineering is, ecosystem types, modular abstractions, quality attributes, shifting down, golden paths, platform ROI, measuring success, migrations and getting started are planned and not published. Several of the available chapters refer to them. Where a lesson leans on one of those, I say so.

### Five words the whole book uses

| Term                                     | Meaning                                                                                                                                                |
|------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|
| Developer ecosystem                      | Everything an organisation could build with: languages, libraries, frameworks, build tools, runtimes, practices. A marketplace of parts.               |
| Developer platform                       | An opinionated selection from that marketplace, integrated and configured for one kind of application, so that quality comes by design and by default. |
| Quality attributes                       | The “ilities”: security, reliability, efficiency, compliance, maintainability. What a platform is meant to guarantee.                                  |
| Golden path / well-lit path / paved road | The supported, documented, easiest way to do a common task. Three names for one idea.                                                                  |
| Ecosystem type                           | How tightly integrated an ecosystem is. Type 2 is guided, type 3 engineered, type 4 assured. The more integrated, the more the platform can promise.   |

### How to study this track

- **Architecture first**: Lessons 1 to 6: coupling, layers, shared fate, then the three deep dives. These are design questions.
- **Then execution**: Lessons 7 to 10: developer experience, product management, AI, education. These are leadership questions.
- **Then the code**: POCs 12 to 19 in the repo turn each idea into something you can run, mapped to AWS.

### Key takeaways

- Shift down means the platform takes the responsibility; shift left only moves it earlier.
- A platform is an opinionated assembly from an ecosystem, built for one kind of application.
- Ten chapters are published. The lessons cover those and nothing else.

## Chapter 9: Coupling: decide what depends on what

*Author: Michelle Brush. Code: POC 12.*

### The big picture

Coupling is how much the parts of a system depend on each other. It is usually talked about as a defect. This chapter’s position is more useful: some coupling is unavoidable, some is valuable, and the real failure is coupling nobody chose.

Two distinctions set up everything else.

|          | Meaning                                                                               | Example                                                                                                              |
|----------|---------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------|
| Explicit | One part calls another directly                                                       | A service makes an RPC to another service                                                                            |
| Implicit | No direct interaction, but one part assumes the other exists or behaves a certain way | A producer writes to a queue. It has never heard of the consumer, and a change to the message format still breaks it |
| Tight    | Parts know each other’s internals                                                     | A service reads another team’s database tables                                                                       |
| Loose    | Parts know only each other’s interfaces                                               | A service calls a versioned API                                                                                      |

**Cohesion** is the mirror image: how closely related the things inside one module are. A module with low cohesion does many unrelated jobs, so either it depends on many things or many things depend on it. Low cohesion and high coupling tend to arrive together.

### When coupling pays

- **Efficiency**: One safe path for everyone. Google’s tooling is coupled to its issue tracker, so every change has a tracked reason and bugs close themselves when the fix is fully rolled out.
- **Performance**: Fewer layers and hops. Spanner can interleave child rows with their parent. Maths lives in libraries, not services, because an RPC would cost more than the sum.
- **Atomicity**: All-or-nothing changes. Deleting a cloud project must also delete its VMs and disks, or resources leak.
- **Traceability**: Follow data end to end. Google’s tracing works everywhere because every service uses the same RPC layer, which gives one place to instrument.

Google has a name for what you give up: **retargetability**, the ability to reuse a part of the system for a different purpose. The trade is engineering efficiency against retargetability.

One warning on performance. Couple for speed only after other options are exhausted. Tight coupling can block later optimisation, because speeding up one module may break a timing assumption in another.

### When coupling costs

- **Reuse**: Coupled parts can’t be used alone. And reuse itself creates coupling: when the tiny left-pad package was unpublished in 2016, thousands of builds broke.
- **Extensibility**: A change in one place has side effects elsewhere, and isolated tests are hard to write.
- **Robustness**: Hyrum’s law: with enough users, every observable behaviour is depended on by someone. Failures cascade.
- **Freedom of choice**: Lock-in. Teams can’t adopt something better without engineering work, and can’t self-serve.

### Finding the balance

> **Diagram.** Three axes: efficiency, performance and retargetability. A tightly coupled design reaches far on efficiency and performance and little on retargetability; a loosely coupled design does the reverse. After Figure 1-1, redrawn. A coupling decision picks a shape in this space. You can stretch towards one corner only by pulling back from another.

No platform can be the best on every axis. A tool that does one job will eventually beat the platform at that job, and users will want to leave for it. Leaving needs loose coupling. Meeting expectations across several axes needs tight coupling. The chapter’s answer is to look for the design that gets the most benefit from the least coupling, which is Pareto efficiency: a point where you can’t improve one dimension without giving up another.

How do you choose the point? Ask what your users value most. If they need raw performance, couple. If they need to extend and customise, don’t.

> **Google’s own trade.** Source control, code review, build and deployment are tightly coupled at Google. That lets them mark one change as bad so it can never ship, even by accident. When Log4Shell appeared, a central profiler wired into the build and scheduling systems showed quickly that exposure was small. The price was that every team had to use the same tools, whatever they were missing.

### Five kinds of coupling

The chapter borrows Kruchten’s “4+1” architectural views and asks, for each one, how two components can be tied together.

| View        | Coupled when…                                                             | How restrictive                                                 |
|-------------|---------------------------------------------------------------------------|-----------------------------------------------------------------|
| Logical     | Code in one calls functions or classes in the other                       | Most                                                            |
| Development | One package needs the other to be deployed with it, like a shared library | High                                                            |
| Process     | They talk at runtime through RPCs or messages                             | Lower: each can be updated on its own                           |
| Physical    | They must share a machine, rack or data centre to work                    | Deceptive: hidden assumptions about latency and failure domains |
| Scenario    | Nothing technical links them, and a real-world event does                 | Invisible until it happens                                      |

The scenario examples are memorable. A shark bit one of Google’s undersea cables. When many people left Twitter in 2022, they overwhelmed Mastodon’s servers. Neither pair of systems shared a line of code.

### Patterns that loosen coupling

| Pattern               | How it decouples                                                                 | On AWS                                                                                                                           |
|-----------------------|----------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|
| Layers                | Each layer knows only the one beneath it                                         | VPC, then EKS, then your services                                                                                                |
| Pipe and filter       | Independent steps joined by a channel. Extend by adding a step                   | Kinesis or MSK with Lambda or Flink stages; Step Functions for batch                                                             |
| Publish and subscribe | Publishers don’t know who is listening                                           | SNS, EventBridge, MSK                                                                                                            |
| Federation            | Interchangeable parts behind a strict contract. Each owns its data and behaviour | IAM Identity Center with an external identity provider; a deletion workflow that asks each service to clean up its own resources |
| Fail open             | When a dependency fails, degrade, use a default or fall back                     | Cached responses, AppConfig defaults, circuit breakers                                                                           |

Fail open deserves care. It removes runtime coupling, since the caller survives, while logical coupling remains, since the call is still in the code. The opposite, fail closed, is correct when the dependency is a security or correctness check.

### Antipatterns that tighten it by accident

- **Shared database**: Several services read and write the same tables. The schema becomes the interface, so every schema change needs a coordinated release. Fix: a store per service behind an API, and let the platform provide backup and replication.
- **Distributed monolith**: Services look separate and aren’t. Signs: releases must be orchestrated in order, they must sit in the same rack, or one failing takes all down. The costs of microservices with the constraints of a monolith.
- **Megamorphic artifact**: A config file or object that grew into a junk drawer. Nobody knows who reads which part, so every edit is risky.
- **Control coupling**: A flag lets the caller steer the callee’s internal behaviour. The caller now knows how the callee works. Fix: split into separate operations.

Data warehouses and lakes are not the shared-database antipattern. Their consumers expect schemas to change and use registries and ETL tools to cope.

> **The megamorphic file at Compute Engine.** One large configuration file started as infrastructure as code. Because it was easy to extend, it collected per-customer preferences and behaviour flags. Almost every service read a piece of it and none needed all of it. Small edits began causing rollbacks and minor incidents. The team split it into smaller, cohesive files, audited every consumer, and removed access nobody needed. Dependencies became visible and the blast radius of a bad edit shrank.

#### The odd one: workflow engines

A workflow engine runs a process as a state machine and retries each step until the whole thing finishes. That decouples steps nicely, provided every step is idempotent and has no side effects beyond its output. Data pipelines usually qualify. Elsewhere, three problems appear.

- **Stuck flows.** A step that can never succeed is retried forever. Someone must detect it and decide whether to roll back or leave things half done.
- **Orphaned state.** Early steps wrote data that the failed workflow never used. You need compensating actions (the saga pattern) or a janitor job, and both are coupled to the business logic of the steps.
- **Version skew.** A step is redeployed while workflows are in flight, and later steps depended on its old behaviour.

### Finding coupling nobody intended

| Method            | Finds                                                                                    | Cost                  | On AWS                                                                 |
|-------------------|------------------------------------------------------------------------------------------|-----------------------|------------------------------------------------------------------------|
| Static analysis   | Logical coupling: imports, shared data structures, global state                          | Low                   | Dependency graphs in CI; Amazon Q Developer or Inspector code scans    |
| Tracing           | Runtime calls, including through queues if messages carry trace context                  | Low once instrumented | X-Ray, Application Signals service map, OpenTelemetry                  |
| Log correlation   | Two services touching the same state or the same request                                 | Medium                | CloudWatch Logs Insights joined on request IDs; CloudTrail data events |
| Chaos engineering | Physical and scenario coupling. Turn off a whole failure domain and see what else breaks | Highest               | Fault Injection Service, ARC zonal shift                               |

When you find an accidental dependency, weigh it like a deliberate one. Does it buy efficiency, performance, atomicity or traceability? If not, migrate to one of the loose patterns.

### Say it in an interview

I don’t treat coupling as good or bad. I ask what it buys and what it costs. It buys efficiency, performance, atomicity and traceability, and it costs reuse, extensibility, robustness and freedom of choice. So I decide which of those my users care about, couple deliberately for that, and then go looking for the coupling nobody chose, with dependency analysis, tracing and fault injection.

### On AWS

The loose patterns map directly: SNS and EventBridge for publish-subscribe, Kinesis and Step Functions for pipelines, API Gateway and versioned APIs between services, IAM Identity Center for federation. For the shared-database antipattern, give each service its own DynamoDB table or Aurora cluster behind an API and let AWS Backup carry the common concerns. To discover hidden coupling, use the X-Ray or Application Signals service map for runtime calls, CloudTrail to see who touches which table or bucket, and Fault Injection Service to remove an Availability Zone and watch what fails.

### Practice question

**Your team has thirty microservices and every release needs a spreadsheet to coordinate the deploy order. What is wrong, and what do you do?**

That is a distributed monolith. The services are separate in the code and coupled somewhere else, and the release spreadsheet is the evidence. I’d say so plainly, because the team is paying the operational cost of microservices and getting none of the independence.

First I’d find where the coupling lives. Shared database tables are the usual cause: I’d check which services read or write the same tables, using CloudTrail or database audit logs. Then implicit contracts: message formats on queues, and shared configuration that many services read. Tracing gives the runtime call graph, and the deploy history shows which services always ship together.

Then I’d fix the worst edge first, not everything. For a shared table, one service becomes the owner and exposes an API; the others migrate to it one at a time. For message formats, a schema registry with compatibility checks in CI. For a junk-drawer config file, split it by consumer.

I’d also ask whether some of those services should be merged. If two services always change together, they are one module with a network call in the middle, and merging them is a legitimate answer.

The measure of success is simple: the percentage of releases that ship one service alone, with no coordination.

### Key takeaways

- Coupling should be a decision. The dangerous kind is the kind nobody chose.
- It buys efficiency, performance, atomicity and traceability, and costs reuse, extensibility, robustness and choice.
- Shared databases, distributed monoliths, junk-drawer configs and behaviour flags are how it sneaks in.

## Chapter 10: Layers: parts of a platform change at different speeds

*Author: Kaan Kivilcim.*

### The big picture

Abstractions give you reusable components. Coupling describes how they connect. Layers add time: which parts of a platform change quickly, which change slowly, and how they influence each other.

That matters because a platform team is always balancing two speeds. Product teams want to ship this week. Governance, security and compliance move on a scale of quarters and years. A layered view tells you which speed belongs where, so the fast parts can move without shaking the slow ones.

### Three earlier ideas about layers

| Model           | From                             | What it gives platform engineers                                                                                                                                                                                                                                          |
|-----------------|----------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| OSI model       | Zimmermann, 1980                 | Three benefits of strict layering: each layer adds value to those below, the problem is divided into manageable pieces, and a layer can change inside as long as it offers the same service upward. It is prescriptive, and real systems bend it.                         |
| Shearing layers | Frank Duffy; Stewart Brand, 1994 | A building is six layers that age at different rates: site, structure, skin, services, space plan, stuff. The site is forever and the furniture moves weekly. It is descriptive, which suits platforms, since they mirror their organisation and resist forced standards. |
| Pace layers     | Stewart Brand, 1999              | Civilisation as six layers by speed: fashion, commerce, infrastructure, governance, culture, nature. Health comes from the tension between them.                                                                                                                          |

Brand’s summary of how fast and slow layers relate is the line to remember. The fast layers learn and propose. The slow layers remember and decide. Shocks are absorbed by the fast layers at the top, and stability comes from each layer respecting the pace of its neighbours.

### Six layers of platform engineering

> **Diagram.** Six stacked layers from prototypes and experiments at the top to regulatory and legal at the bottom, with shorter arrows for slower layers. After Figure 2-4, redrawn as bands. The top layer turns over in days. The bottom one barely moves, until a court ruling or a new law moves it all at once.

| Layer                          | What lives here                                                                                                                                                            | Pace               |
|--------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------|
| 1 · Prototypes and experiments | Building to learn. Most of it is thrown away, and the lessons decide what moves down. Rust experiments at Google eventually shaped company-wide directives.                | Days to weeks      |
| 2 · Products                   | The marketplace. Proven ideas become features with requirements and stability. Product teams think about what, not how.                                                    | Months             |
| 3 · Infrastructure             | The paved road: runtimes, server frameworks, networking, CI/CD. Convergence here saves each team tens or hundreds of person-years, and every improvement reaches everyone. | Quarters or longer |
| 4 · Technical directives       | The law of the engineering organisation: binding cross-company decisions, such as safety expectations for AI agents or converging on a set of server frameworks.           | Quarters to years  |
| 5 · Business culture           | Why the company does what it does. Durable system health over short-term gain; protecting users by default.                                                                | Years              |
| 6 · Regulatory and legal       | The outside world. Everything above must eventually comply. A change here cascades upward through culture, directives and infrastructure.                                  | Slow, then sudden  |

### One tool, six layers

The chapter follows an internal screenshot tool called SnipIt through every layer. It is a good story to retell because it shows the layers pushing on each other in both directions.

1.  **Prototype.** Started in 2009 as a 20% project. Nobody would have funded a screenshot tool if asked.
2.  **Product.** For more than 15 years a tiny team, often one person part-time, kept it running. By 2024 it was the third most used internal application at Google.
3.  **Infrastructure.** It reached 8 billion screenshots with no major rework, because it ran on App Engine. The leverage was so complete it was invisible.
4.  **Directive.** Security standards moved on, and the tool needed finer-grained access controls. The first decision was to shut it down.
5.  **Culture.** Employees pushed back hard: testimonials, petitions, memes. Shutting down something this useful was called “ungoogley”.
6.  **Legal.** The obligation to protect internal data could not be argued with. So the only remaining answer was to invest and bring the tool up to standard.

Read it as two forces. A fast layer proposed something and it worked. A slow layer said no. A slower layer overruled that no, and the slowest layer set the terms of the yes.

### Using the layers in practice

- **Place every decision on a layer before arguing about it.** A choice of library is layer 1 or 2 and should be cheap to reverse. A choice of deployment framework is layer 3. A mandate is layer 4 and needs an owner and a reason.
- **Let ideas move down only when proven.** The top layers are where you learn cheaply. Promote what works; don’t standardise an experiment.
- **Don’t make slow layers move at the speed of fast ones.** Rewriting your deployment platform every quarter to follow a trend is how platforms lose trust.
- **Expect shocks from the bottom.** When regulation changes, plan the cascade: what the policy becomes, which directive it turns into, which platform component enforces it.

The AI chapter later uses the same picture: AI applications are the fast layer, and the platform is the slow layer that absorbs shocks and gradually takes on whatever has proven itself.

> **Connection to the SRE track.** Chapter 3 of the SRE book describes compliance being written as policy-as-code and checked before deployment. In this model that is a layer 6 requirement, turned into a layer 4 directive, implemented at layer 3.

### Say it in an interview

I think about a platform as layers that change at different speeds. Experiments and products at the top change in days or months. Infrastructure, technical directives, culture and regulation below them change over quarters and years. The fast layers are where we learn; the slow layers are where we keep what we learned. Most platform arguments get easier once you agree which layer a decision belongs to.

### On AWS

A workable mapping: sandbox accounts for experiments (layer 1), product accounts and services (layer 2), the shared platform of landing zone, EKS or ECS base, pipelines and golden-path templates (layer 3), Service Control Policies, Config conformance packs and tagging standards as technical directives (layer 4), and compliance frameworks tracked in Audit Manager and Security Hub standards at the bottom (layer 6). Use AWS Organizations to give the layers different rates of change: sandbox OUs with loose guardrails, production OUs with strict ones.

### Practice question

**A team wants to use a new language that the platform doesn’t support. How do you decide?**

I’d start by asking which layer the request sits on. Trying a language in a prototype is a top-layer activity. It should be cheap and allowed, in a sandbox, without platform guarantees, and the team should know they own everything the platform would normally give them.

Putting it into a product that pages someone is a different request. Now it touches the infrastructure layer: build, dependency management, security scanning, observability and deployment all need to work for that language. That is a real cost, paid by the platform team for years.

So I’d set a path. Experiment freely. If the experiment shows a clear advantage for a class of workloads, write that up, and decide at the directive level whether to add the language to the paved road. Google’s Rust adoption followed that route: exploration first, then a company-wide direction, then investment in tooling.

What I’d avoid is the middle state, where a production service runs on a stack nobody supports. That gives the team the freedom of a low-integration ecosystem while they still expect the guarantees of a high-integration one.

### Key takeaways

- Layers describe rates of change. Match each decision to the layer it belongs on.
- Fast layers learn and propose; slow layers remember and decide.
- Changes at the bottom cascade upward, so plan how a new rule becomes a directive and then a platform feature.

## Chapter 12: Shared fate and shared responsibility

*Author: Andy Qin. Code: POC 14.*

### The big picture

In a mature engineering ecosystem, components are connected on purpose. One team’s library update, security patch or shortcut reaches everyone who builds on it. The book calls this **shared fate**. It is what makes fleet-wide improvements possible, and it is also what makes fleet-wide failures possible.

Shared fate without **shared responsibility** ends in a tragedy of the commons. Each team does what is locally sensible, such as adding a risky dependency or ignoring a deprecation notice, and the common ground everyone depends on gets worse.

### The economics: choice for liability

The whole chapter rests on one equation. **The more an ecosystem limits a developer’s architectural choices, the more liability it can take on for that developer.**

> **Diagram.** Three bars for ecosystem types 2, 3 and 4. The share of responsibility carried by the platform grows from small to most of the bar, while architectural choice shrinks. My drawing of the chapter’s spectrum. The filled part is how much of safety, reliability, efficiency and compliance the platform carries. The types come from a chapter that is not published yet; the names match the 0-to-4 scale in the SRE book.

|          | Type 4 · highly integrated                                                                                         | Type 2 or 3 · loosely integrated                                                                  |
|----------|--------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------|
| You get  | Leverage. The platform owns security, reliability, efficiency and compliance                                       | Flexibility and a fast start. Any language, library or toolchain                                  |
| You pay  | Conformity. Standard build system, languages and tools. The head of every library must always build and pass tests | The operational load comes back to you. You are your own security engineer and compliance officer |
| Good for | Most production software at scale                                                                                  | Acquisitions, special projects, early experiments                                                 |

Two of Google’s numbers show the dividend. A central improvement to the C++ memory allocator reached every team at once and saved a significant share of fleet CPU, with no team changing a line. And safe-by-design query APIs produced zero SQL injection in more than a decade in one ecosystem. Neither result came from training thousands of engineers.

#### One example across the types: third-party packages

| Ecosystem | What the platform does                                                           | What is left to you                                               |
|-----------|----------------------------------------------------------------------------------|-------------------------------------------------------------------|
| Type 2    | Stores packages in a registry                                                    | Reviewing updates, licences, freshness, patching. Everything      |
| Type 3    | Handles ingestion and gives you scan data                                        | Choosing versions and deciding how to mitigate each vulnerability |
| Type 4    | Ingests, scans for malware, enforces freshness and licences, blocks bad packages | Almost nothing, and almost no choice                              |

The chapter separates a **resource** from a **guardrail** with this example. A registry is a resource: it helps, and the easiest thing to do with it is ignore updates. A managed dependency system is a guardrail: the safe package is the only one you can get.

### Governance: from policing to stewardship

Central enforcement works in a uniform ecosystem, where it can be automated until developers no longer notice it. It does not work across mixed environments, where a central team can’t enforce what it can’t see.

There the platform’s job changes to stewardship. It provides tools, data and guidance, including coverage metrics that let each team lead see how well they meet their own obligations. Accountability for accepting risk sits with the local team. The shift is from enforcement to enablement, and it keeps the central team from becoming a bottleneck.

### Guardrails: the path of least resistance

You can’t run a large system on willpower. The safest action has to be the easiest one.

1.  **Type 2**: Find defects after the commit: static analysis, fuzzing. The developer must triage and fix
2.  **Type 4**: Assurance by design: safe-by-default frameworks, and raw risky APIs locked away from everyone except reviewed code

*The chapter calls this the hierarchy of assurance. Enforcement is mechanical, through build visibility rules, and never by convention alone.*

A useful phrase from the chapter: **friction is a directive**. People do what is easy. Remove friction from safe behaviour and add it to risky behaviour, and the system steers itself.

Uniformity also pays in maintenance. With one compiler and build chain, the platform team can make a **large-scale change** across thousands of projects quickly, for example to respond to a new security threat. In a mixed environment every team patches by hand.

### The three Rs

- **Resources**: What the ecosystem gives the developer: compute, storage, safe APIs, managed dependencies.
- **Rights**: What the developer is allowed. In a loose ecosystem, unlimited choice. In an integrated one, that right is given up in exchange for the right to assured safety.
- **Responsibilities**: What the developer puts in to keep the ecosystem healthy.

The contract is most often broken in one specific way: a team wants the rights of a loose ecosystem and the resources of an integrated one. Free choice of stack, and automatic security. Those two can’t be had together, and saying so explicitly is most of the work.

|                       | Walled garden (type 4)                                                                     | Frontier (types 2 and 3)                                                     |
|-----------------------|--------------------------------------------------------------------------------------------|------------------------------------------------------------------------------|
| The deal              | Conformity for leverage                                                                    | Autonomy for accountability                                                  |
| Platform’s obligation | Full support for security, reliability and compliance                                      | Resources, tools and visibility. No assurances                               |
| Team’s obligation     | Sustainability: don’t add debt that blocks the automated machinery                         | Be the primary guardian. You are the security team                           |
| The image             | A passenger on a high-speed train. You don’t drive, and you don’t pull the emergency brake | A settler. Nobody is coming to save you                                      |
| Typical failure       | A team quietly diverges and blocks a fleet-wide change                                     | A team imports a malicious library, assuming central security would catch it |

#### Where the contract strains

The friction shows at the edges. An acquired company arrives with a very different ecosystem. A team spinning out a special project tries to take the big machinery with it and finds it can’t run it alone. The chapter asks for **permeability**: moving between ecosystems is a renegotiation of the contract, and it goes better when framed as a trade the team is making, not a mandate imposed on them.

### Why this matters more with AI agents

An agent writes code faster than people can review it. In a loose ecosystem, where safety depends on human vigilance and manual glue, that speed multiplies mistakes. In a tightly integrated one, the platform’s constraints act as a containment field: an agent can’t commit code that breaks a safety rule, because that code doesn’t build.

Agents also do better when there is less to get right. If the platform handles build flags, dependencies and safety properties, the agent only has to express the business intent. The human’s role moves to being a **guardian of intent**: define the goal and the success criteria precisely, trust the fast generation, and verify deliberately.

> **Not everything belongs in the walled garden.** The chapter ends on a menu of deliberate trade-offs. Start experiments where friction is low. Let acquisitions integrate gradually. What matters is that each team knows which contract it has signed.

#### Learning loops

Incidents, audit findings and red-team results are raw material for shared learning. To use them you need two kinds of metrics: team-level delivery metrics in the DORA style, and ecosystem-level ones such as toolchain effectiveness and governance coverage.

### Say it in an interview

Shared fate means one team’s choices land on everyone, so it has to come with shared responsibility. I frame it as a trade: the more a platform limits your choices, the more liability it can carry for you. I make that explicit with three Rs: what resources the platform gives, what rights the team has, and what responsibilities they keep. The failure I watch for is a team wanting free choice of stack and automatic guarantees at the same time.

### On AWS

AWS publishes its own shared responsibility model, and your internal platform needs one too. A type 2 account gets raw services and a registry (ECR, CodeArtifact) and owns everything else. A type 3 landing zone adds Control Tower guardrails, Config rules, Inspector scan results and Security Hub scores that teams must act on. A type 4 golden path makes the safe choice the only one: Service Control Policies block the risky APIs, CodeArtifact serves only vetted packages, pipelines are the sole route to production, and Lambda code signing or an EKS admission policy refuses unsigned artifacts. Publish a coverage dashboard so every team lead can see their own posture.

### Practice question

**A team asks for an exemption from the standard pipeline because it slows them down. How do you respond?**

I’d treat it as a conversation about which contract they want, not as a yes or no.

First I’d find out what is slow, because that may be a platform bug. If the pipeline takes forty minutes or blocks on a flaky check, that is our problem to fix, and their complaint is useful. Friction on the safe path pushes people off it.

If they need something the path really can’t do, I’d lay out the trade. On the standard path, the platform carries security scanning, signed artifacts, canary analysis, rollback and compliance evidence. Off it, they carry all of that, and they’re no longer eligible for fleet-wide fixes. I’d put that in writing: the resources they give up and the responsibilities they take on.

Then I’d make the exemption safe and visible: time-limited, with an owner, tracked as debt, and contained so a mistake can’t spread, for example in its own account with its own blast radius.

Finally I’d treat the request as product feedback. One exemption is a special case. Five for the same reason is a gap in the platform.

### Key takeaways

- Limit choice and the platform can carry liability. That is the trade.
- Make it explicit with resources, rights and responsibilities.
- Guardrails must make the safe path the easy one, and that matters most when agents write the code.

## Chapter 14: Efficiency: one optimisation, every team

*Author: Chris Kennelly. Code: POC 17.*

### The big picture

When every team runs on the same foundations, two things become possible. You can see where resources go across the whole fleet. And when you improve a shared component, everyone gets faster at once. Seeing leads to improving, and improving pays for more seeing. The chapter calls it a virtuous cycle.

1.  **Common infrastructure**: Same scheduler, RPC layer and libraries
2.  **Fleet-wide observability**: A profiler on every machine
3.  **Central optimisation**: Fix the shared thing once
4.  **Savings**: Which fund more observability

*Each new measurement rides on rails that already exist, so the next insight is cheaper than the last.*

#### How Google got there

- **The scheduler hides placement.** Borg decides which jobs share a machine. A CPU-heavy team and a memory-heavy team fit together, and spare capacity for failures is pooled across the data centre, not held by each team.
- **The same agents run on every machine.** That made it possible to profile everything: Google-Wide Profiling gives each team a debugging tool and gives the company one aggregated picture.
- **The aggregate showed surprises.** In 2015 the memory allocator accounted for about 8% of fleet usage, more than any single application. Nobody would have found that by looking at one service.

> **Profile-guided optimisation, made automatic.** Compilers can optimise better with a profile of real usage. Getting one used to mean each team building a load test, an instrumented binary and a second build step, so few did. Google used the fleet profiler to synthesise a profile for every team automatically, and adoption became a one-line change. In its first year this doubled the share of the fleet using the technique. The lesson: effort deters adoption more than doubt does.

### Shifting optimisations down

#### On by default

The platform team prototypes an optimisation, canaries it on major workloads, evaluates it, and then turns it on for everyone. Teams pick it up at their next normal release and do nothing. This avoids the trap of building something and waiting for teams to discover it, and it keeps the decision with the people who understand the change.

Not every workload gets faster. The chapter is candid about how regressions are handled.

| Regression       | What they do                                            | Why                                                                                                                          |
|------------------|---------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------|
| Small, for a few | Absorb it                                               | Per-application tuning adds options, and every option enlarges the set of states each future change must be tested against   |
| Large, for a few | Offer an opt-out per application, and work to remove it | An opt-out is information: it shows which edge cases truly matter. One long-standing opt-out led to two further improvements |
| Large, for many  | Don’t ship                                              |                                                                                                                              |

The judgement behind this: an imperceptible slowdown or a little opt-out work for one team can be better than not shipping a major win for hundreds.

#### Spread the best local idea

A better hash table began as a collaboration between the core C++ library team and two engineers on the search index. The index team could have swapped their hottest tables and stopped. Instead the platform team rolled the new table out across the whole codebase with automated refactoring, and CPU and memory needs fell substantially.

A detail worth knowing: the designers made the table’s iteration order **random on purpose**. Earlier attempts to optimise hash tables had been blocked because code quietly relied on the order (Hyrum’s law again). Randomising it stopped that dependency from forming, which kept the door open for later improvements. Teams sometimes ask to switch it off. Saying yes would help them today and hurt everyone, including them, later.

#### Work further up the stack

A low-level copy routine can only be made so fast, because it must do the copy. Higher up, analysis of the code may show the copy was never needed. The fastest copy is the one you don’t make. Tools from linters to language models find these recurring patterns, and the central team sends ready-made changes to owners for review.

#### Shift left for performance too

- Fleet telemetry raises alerts when a function, application or library regresses after a rollout.
- Canaries pause for automated performance checks against the old version, not only reliability checks.
- Benchmarks run periodically and on proposed changes.
- Code-review tooling flags known slow patterns and proposes the fix.
- Well-designed libraries make the efficient way the obvious way.

### Connect efficiency to business value

Nobody buys servers in order to allocate memory. Low-level numbers are easy to measure and say little about value. What matters is how much useful work you get for what you buy.

The problem: a service’s CPU use went up 20%. Is that a regression, or is it handling more traffic? You can’t tell by looking.

Google’s answer is the **application productivity metric** (APM). Each service reports how much useful work it does, and the platform divides by resources used: videos processed per CPU-second, records per byte-second of memory, queries per accelerator-hour.

| CPU used | Useful work | Work per CPU-second | Verdict                       |
|----------|-------------|---------------------|-------------------------------|
| +20%     | +20%        | Flat                | Busier. Nothing is wrong      |
| +20%     | Flat        | Down 17%            | A regression. Find the change |
| Flat     | +15%        | Up 15%              | An optimisation landed        |

- **Defaults make it practical.** RPC servers report requests; pipelines report records. Most services need no setup.
- **Outliers reveal bad metrics.** A batch service should count items, not batches. A service whose work metric doesn’t track its resource use at all is probably misconfigured.
- **They catch what component metrics hide.** Work on the allocator’s layout decisions made applications faster and made the allocator *look* more expensive in relative terms. Only a work-based metric showed the win. The team’s joke was that the allocator had become faster than light.

#### Not all work is equally valuable

Some resource use serves no user directly and is still necessary: monitoring probes, hedged requests, load tests, load balancing and shedding. Some serves nobody: a video still playing to an empty room, or a backend finishing a request whose caller has already given up. Deadline propagation stops the second kind. Knowing the criticality of each kind lets you shed the non-essential during a disruption and push background work off-peak, which means less idle capacity held in reserve.

> **Proxies and Goodhart.** Measuring precisely costs something too. Use proxies that track the business goal closely, and remember Goodhart’s law: a measure that becomes a target stops being a good measure.

### Three lessons

- **Take the long view**: The cost of an opinionated platform is visible. The cost of flexibility is not: every option must be discoverable, tested and carried forward, and it becomes a tax on every later change.
- **Don’t assume the platform is fixed**: Application teams work around platform problems. If everyone works around the same one, it looks rare. Report it; the platform can change when the value is there.
- **Create leverage and use it**: Improve something already widely used. Or migrate ten implementations to one, so every later improvement lands on everybody.

### Say it in an interview

Efficiency at scale comes from leverage. If every team shares the same libraries and runtime, I can profile the whole fleet, find that some shared component is the biggest consumer, fix it once, and ship it on by default. I’d measure with useful work per unit of resource, because raw CPU can’t tell me whether a service got slower or just busier.

### On AWS

Start with visibility: Cost and Usage Reports with cost allocation tags, Compute Optimizer, and a continuous profiler across the fleet (CodeGuru Profiler or an open-source eBPF profiler). Build an application productivity metric in CloudWatch with metric math: a business counter from your service divided by vCPU-seconds from Container Insights. Shift down with shared base images, a common runtime and Graviton as the default, delivered through the golden-path pipeline so teams get improvements at their next deploy. For criticality, use Spot and scheduled scaling for work that can wait.

### Practice question

**Your cloud bill for a service rose 30% in a quarter. How do you find out whether that is a problem?**

I wouldn’t start from the bill. I’d start from what the service did for that money.

First I’d define useful work for this service: requests served, orders processed, records transformed. Then I’d plot work per vCPU-second and per gigabyte-hour over the quarter. If work also rose about 30%, the service is busier and the cost is growth. If work is flat, efficiency dropped and I have a regression to find.

For a regression I’d line the productivity curve up against deploys and config changes, and use profiles from before and after to see which functions grew. Common culprits are a new serialisation step, a logging change, a retry storm, or a dependency upgrade.

I’d also check criticality. Some growth is work nobody needs: retries against a failing dependency, requests that continue after the caller timed out, a batch job running at peak. Deadline propagation and moving batch off-peak fix those without touching the code path.

Finally I’d ask whether the fix belongs in the service or in the platform. If the cause is a shared library or base image, fixing it centrally helps every team that has the same problem and hasn’t noticed.

### Key takeaways

- Shared foundations turn one optimisation into a fleet-wide saving.
- Ship on by default, absorb small regressions, and treat opt-outs as information.
- Measure useful work per unit of resource, or you can’t tell slower from busier.

## Chapter 15: Security: if it isn’t secure, it shouldn’t compile

*Author: Christoph Kern. Code: POC 13 · 14 · 15.*

### The big picture

The same kinds of vulnerability top the incident reports year after year: memory corruption, injection, broken access control. The industry’s list of the most dangerous weaknesses has barely changed in a long time, despite decades of secure-coding training.

This chapter’s diagnosis is that the problem is structural. We ask every developer to avoid every known mistake at every call site, forever, and we check afterwards with tools that can only find some of what went wrong. People make mistakes because the systems they work in make mistakes easy. So do AI coding tools, which now write more code than humans can review.

The platform answer: move security out of each developer’s head and into the things all code is built from, so whole classes of bug can’t be written.

> **What “platform” means here.** More than the cluster your code runs on. It is the whole stack a developer touches: the language and its type system, libraries and frameworks, the build system, deployment and runtime, and the review and release process. Application bugs are born in the layers nearest the developer, so that is where they can be prevented.

### Why the usual approaches fall short

Three facts frame the problem.

- **Experts are outnumbered several hundred to one.** The ratio is about the same at Google as at a small company. Hiring can’t fix it.
- **Software is programming integrated over time.** Code that was secure at launch may not be after next week’s commit, so a point-in-time review proves little.
- **Testing can’t show absence.** Even a tiny program has more possible states than any test suite can visit. A two-by-two grid of 64-bit numbers has about as many states as there are atoms in the observable universe. For ordinary bugs this is tolerable, because a bug nobody hits hardly matters. For security it isn’t, because an attacker goes looking for the one input you never tried.

That last point defines the goal. **Assurance** is confidence that a requirement holds for every behaviour of the program. **Continuous assurance** is keeping that confidence for every version you ship.

| Approach          | What it is                                                                           | Why it isn’t enough                                                                                                                                             |
|-------------------|--------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Ship and patch    | Find vulnerabilities in production                                                   | Real exposure, an endless patch treadmill, lost trust. Hard to escape later                                                                                     |
| Find after commit | Static analysis, fuzzing, sanitizers, scanners, security review (increasingly by AI) | Tools miss bugs or raise false alarms, usually both. Findings arrive after the author has moved on. Useful as defence in depth; can’t prove nothing remains     |
| Shift left        | Train developers; analyse in the editor                                              | Nobody can hold hundreds of vulnerability patterns in mind while solving a business problem. False alarms teach people to suppress warnings, real ones included |

> **Initial and sustained velocity.** Security feels like it slows teams down when it is bolted on as reviews and gates. The chapter separates how fast you ship the first version from how fast you keep shipping. Shortcuts buy the first and cost the second. A platform pays the upfront cost once so applications inherit both. For a young product still finding its market, trading sustained speed for initial speed can be rational, if it is a conscious choice with a plan to pay it back.

### Shift down: the platform as a security control

Security can’t be added afterwards. It emerges from how the system is designed, how the software is structured, and what the platform allows. That works in both directions.

- **If the platform enforces it**: Applications inherit the guarantee. In Rust, Java or Python, ordinary code can’t corrupt memory, and the exceptions are explicit and reviewable.
- **If the platform doesn’t**: Applications will have the defect. Any large C++ codebase contains memory-safety bugs, and decades of effort haven’t removed them after the fact.

Shifting down also compounds. Each class of bug the platform eliminates frees the security team from reviewing, advising and responding for that class. They spend the time eliminating the next one.

#### Three objectives

1.  **Prevent common classes by construction.** Design the platform so the bug can’t be introduced.
2.  **Confine what is left.** Keep security-critical code in a few well-reviewed platform components, not spread across every application.
3.  **Keep the guarantee through change** without an expert reviewing each commit.

Prevention never reaches zero defects, so **containment** stays essential: sandboxes, least-privilege identities and mediated access limit the damage of whatever slips through.

#### Application archetypes

Most applications are not architecturally unique. A stateless RPC service, a SQL-backed store, a browser frontend talking to an API, a mobile client: the same shapes recur, and the same threats come with each shape whether the app is a bank or a photo editor. The chapter calls a recurring whole-application shape an **archetype**.

| Component             | Threat it brings                      | Invariant the platform can own                                                                                                                      |
|-----------------------|---------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|
| Relational storage    | SQL injection                         | Every query’s structure comes only from the developer; untrusted values are bound as parameters                                                     |
| Web frontend          | XSS, CSRF, clickjacking               | Untrusted values reach the page only through types that guarantee correct escaping; state-changing requests are CSRF-checked; framing is restricted |
| RPC backend           | Unauthenticated or unauthorised calls | Every request is authenticated and authorised before any handler code runs                                                                          |
| Mobile client and API | Trusting the client                   | The server treats all client input as untrusted and re-checks authorisation                                                                         |

An **invariant** is a property that holds on every execution path, including for malicious input. A platform can’t own your business logic, but it can own these, and they account for most of what goes wrong in practice.

A platform built for a whole archetype beats a set of separate controls, because some risks live between components. A browser frontend and an authenticated API can each be secured and still leave a gap: an attacker’s page can make the victim’s browser call a state-changing endpoint, unless cross-site defences cover the entire API surface. That depends on the boundary, which neither side owns alone.

### Safe Coding

This is the heart of the chapter. Start with one definition.

A **risky operation** is safe only if some condition holds when it runs, and nothing in the language or API guarantees that it does. Reading element `i` of an array is safe only if `i` is in bounds. Running a SQL string is safe only if it was assembled from trusted parts. The condition is often established far away, in another module or another team’s code, so checking it means reasoning about the whole program.

A **safe abstraction** wraps the risky operation in a module with two properties.

1.  Its public interface puts no safety conditions on the caller. Any use that type-checks is safe.
2.  Its implementation takes full responsibility for the conditions of the risky operation inside.

The consequence is the important part: you can verify the abstraction by reading only its own code. A security expert reviews it once and it is safe for every caller, including applications not written yet.

> **Diagram.** Before: many call sites feed a string-based risky operation and a few are wrong. After: the same call sites go through one typed safe API that guards the risky operation. My drawing of the chapter’s central move. The risk is relocated from thousands of call sites into one component small enough to review properly.

#### Two ways to build one

| Technique      | How it works                                                                                                  | Example                                                               |
|----------------|---------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------|
| Runtime check  | Establish the condition immediately before the risky operation                                                | A vector type stores its length and checks the index on every access  |
| Type invariant | A purpose-built type whose existence is the evidence. If you hold a value of that type, the condition is true | A query type that can only be built from constants in the source code |

#### The injection example

The chapter uses a photo app that looks up an album by ID, restricted to the signed-in owner. Here is the same idea in Python.

    # Risky: structure and data travel in one string
    q = ("SELECT * FROM albums WHERE owner = '" + user
         + "' AND id = '" + album_id + "'")
    db.execute(q)

Send an album ID of `x' OR id='someone-elses` and the owner check disappears, because AND binds tighter than OR. The developer didn’t ignore advice. The API takes a string, and a string carries no record of where its characters came from.

You can’t add a runtime check for that, since the information is gone. So the condition is tightened into something a type can carry: *the query text consists only of constants written by the developer*.

    # Safe: the database wrapper accepts only a TrustedSql, and a TrustedSql
    # can only be built from a string literal. Values go in separately.
    q = TrustedSql("SELECT * FROM albums WHERE owner = ? AND id = ?")
    db.query(q, user, album_id)

The attacker’s text now arrives as a bound value and is compared as data. Concatenating input into the query produces something that is not a constant, the API rejects it, and the build fails. The vulnerable program can no longer be expressed. The web equivalent is templates that escape automatically for each context, typed HTML values, and the browser’s Trusted Types standard, which refuses plain strings at dangerous sinks.

#### Why it scales

Most of a codebase becomes plain safe code with no risky operations at all. A small, stable set of safe abstractions holds every one of them. Experts review those in isolation. The compiler’s type checker then verifies, across the entire codebase and on every build, that nothing reaches a risky operation except through a safe interface.

The chapter places this on a spectrum. Testing samples behaviour. Formal verification proves a property for all behaviour and is so costly it is used mainly for cryptography, protocols and microkernels. Safe Coding sits between: an expert argument about one small module, extended mechanically to every program by the type checker. It captures much of the benefit of formal methods at a fraction of the cost.

> **Tink: the same pattern for cryptography.** Using a cipher correctly means choosing an algorithm, mode, key size, nonce and padding, and one quiet mistake voids the protection while every test still passes. Google’s Tink library offers operations named for what you want, such as authenticated encryption or digital signatures, with safe choices built in, dangerous options absent and key management included. A developer can encrypt correctly without knowing what a nonce is. People adopt it mostly because it is the easiest correct option, which is the ergonomics point in one example.

#### Making it stick

- **Build visibility rules** restrict who may call the raw risky API.
- **Narrow static checks.** Earlier, static analysis hunted an open-ended class of bugs and was unreliable. Here it checks one decidable property, such as “is this argument a compile-time constant?”, so it has no false negatives. Its only failure is being conservative, and that is resolved openly: use the safe pattern or get an expert-reviewed exception.
- **Conformance rules** let a codebase declare, and have verified, statements like “no direct DOM manipulation”.
- **Ergonomics.** The safe API must be at least as easy as the risky one and cover what people really need. Otherwise they queue for exceptions or find workarounds.

#### What adoption costs

A small team maintaining safe abstractions can support thousands of developers. Existing code is the expensive part, and the Android numbers show a way through: writing *new* code in memory-safe languages took memory-safety bugs from over 70% of the total to 24% in six years, without rewriting the old code. Old code’s bugs get found and fixed over time, so new defects concentrate in new code. Stop adding unsafe code and the rate falls.

Plan for an exception process with tracked debt, and use sandboxing to make exceptions cheaper to grant. Count one recurring cost honestly: mandating an API reduces teams’ options and commits the platform team to keeping that API current.

### Memory safety

Between 60% and 70% of high-severity vulnerabilities in large C and C++ codebases are memory-safety bugs. Choosing a memory-safe language is the most dependable fix and one of the most consequential platform decisions. The guarantee holds only for the safe subset, so escape hatches (Rust’s `unsafe`, native extensions) must stay rare, explicit and reviewed. Hardened C++ reduces some bug classes at lower cost and does not give the full guarantee.

### The software supply chain

The goal: every binary running under a privileged production identity was built from trustworthy source that reflects what the organisation intended. Three properties support it: **provenance** (where it came from and how it was built), **integrity** (not tampered with) and **authorisation** (only approved changes, builders and binaries).

| SLSA build level | Requires                                               | Protects against                                                            |
|------------------|--------------------------------------------------------|-----------------------------------------------------------------------------|
| L0               | Nothing                                                | Nothing. Development builds                                                 |
| L1               | Provenance exists                                      | Mistakes, such as building the wrong commit. Easily forged                  |
| L2               | Signed provenance from a hosted build platform         | Tampering after the build                                                   |
| L3               | Hardened builds: isolated runs, protected signing keys | Tampering during the build by insiders, stolen credentials or other tenants |

Be precise in interviews: SLSA build levels say the artifact was built from *that* source by *that* process. They say nothing about whether the source or its dependencies are free of flaws. Source integrity needs its own controls: mandatory second-person review, protected branches and strong authentication, configured centrally so every repository inherits them.

1.  **Source**: Reviewed by a second person
2.  **Build**: Hosted, isolated
3.  **Attestations**: Signed statements: built from commit X; approved; scans passed
4.  **Deploy gate**: Verifies attestations before anything runs
5.  **Production**

*Google calls the gate binary authorization. Each attestation is a signed claim; the gate trusts signatures, not people.*

Third-party code gets the same treatment: curated repositories of vetted versions, automated dependency analysis, local copies for stability, and automated vulnerability tracking.

### Identity and insiders

- **Identity:** single sign-on for people, platform-managed identities for workloads, identity carried through every service call.
- **Authentication:** frameworks verify credentials before application code runs; mutual TLS between services, handled by the mesh.
- **Authorisation:** service-to-service policy, role-based control for admin actions, and checks the framework won’t let you skip. For fine-grained questions like “can this user edit this document?”, a central service: Google’s Zanzibar stores relationships and answers consistently for hundreds of products.
- **Insider risk:** multi-party approval for sensitive actions, changes through automation with policy checks in place of direct human access, and proxies that validate, rate-limit and log what operators do.

Centralising concentrates risk, since a flaw in the shared service is valuable to an attacker. It also concentrates the ability to harden and review, with the one team equipped to do it. The chapter judges that a good trade.

### Web security: about twenty controls

Google’s internal web frameworks switch on roughly twenty controls by default. Knowing the three groups is enough for most interviews.

| Group      | Purpose                                | Controls                                                                                                                                                                       |
|------------|----------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Encryption | Everything travels over HTTPS          | Secure cookies, HTTPS redirects, HSTS, central TLS termination                                                                                                                 |
| Isolation  | Other sites can’t reach into yours     | CSRF protection, SameSite cookies, framing protection, cross-origin opener and resource policies, Fetch Metadata checks, host header validation                                |
| Injection  | Untrusted content is never run as code | Compile-time checks on JavaScript, typed responses, contextual auto-escaping templates, safe content types, HttpOnly cookies, strict CSP, Trusted Types, reviewed dependencies |

No product team could keep all of that configured correctly by hand. And when the security team strengthens one control in the framework, every application gets it.

### Safe deployment

The Safe Coding idea applied to configuration. Nobody can hold every permission, network rule and option in their head, and a misconfiguration is as dangerous as a code bug.

- **Configuration as code**: Versioned, reviewed, checked before merge. Every production change is recorded and attributable.
- **Blueprints**: Pre-validated templates for common patterns, such as “external-facing web service”, with TLS, network policy and permissions already right. Update the blueprint and the fix propagates.
- **Conformance verification**: Continuously compare what is deployed with the approved baseline. Rules like “no container runs as root” block violating deployments and alert on drift. The deployment-time version of a type checker.

### Measuring the guarantees

A proxy watching traffic can’t tell whether a response was built by a safe template or whether a CSRF check ran. So Google’s frameworks **emit security telemetry themselves**, on every request: was the safe templating system used, did CSRF validation run, which code path served this. A central system collects and aggregates it. If a service stops emitting a signal, perhaps because an upgrade broke a check, someone is alerted.

This changes what security monitoring can claim. Traditional monitoring detects the presence of problems, which is never complete. Measuring the presence of structural guarantees gives strong evidence of the *absence* of entire classes of defect.

### Security with AI in the loop

- **AI writes buggy code too**: The same patterns as humans, sometimes more often. Platform guardrails apply equally: code that breaks the rules doesn’t compile and can’t deploy. The bug classes AI most often produces are the ones platforms prevent best.
- **AI is a strong bug finder**: Agents now find unknown vulnerabilities and write exploits, limited by compute, not by scarce experts. Still a search after the fact, so it can’t show that nothing remains. Aim it at what prevention doesn’t cover.
- **AI lowers the cost of adoption**: Migrating code to safe patterns is high-volume, well-specified and mechanically checkable. An agent can iterate until the build, the conformance checks and the tests pass.

One cost argument is worth quoting in your own words: running a frontier model over every change is expensive, while a safe abstraction, once written, prevents the bug on every build for almost nothing.

> **Why prompt injection is different.** Prompt injection has the same shape as SQL injection: instructions and data share a channel and the interpreter can’t tell them apart. The cure for SQL depends on the interpreter offering a dependable separate channel for data. Language models don’t have one. Everything is a single stream of tokens with no grammar to enforce a boundary. Until that changes, prompt injection can’t be prevented by construction. Limit what an LLM-driven component is allowed to do.

### Assembling your own

No product on the market has all of this, because an opinionated platform only works when its opinions fit your organisation. The chapter’s method: for each property you need, pick a component that takes responsibility for it, put that component on the path developers already use, and measure where adoption has gaps.

1.  **Memory safety first.** It has the highest leverage. Use a memory-safe language for new services.
2.  **Web.** Render in the browser with a framework that supports Trusted Types; serve static or auto-escaped bootstrap pages; set security headers in one middleware; put authentication, CSRF and authorisation checks in the RPC layer; require a security reviewer for changes to those few files.
3.  **Supply chain.** Climb the SLSA levels with signed build attestations, and automate dependency updates.
4.  **Deployment.** Configuration as code, then policy enforcement at admission.
5.  **Observability.** The weakest area in public tooling. Emit your own framework-level security signals.

### Say it in an interview

I’d stop treating developers as the last line of defence. Training and scanners find some bugs and can’t show that none remain. I’d shift security down: pick the invariants that matter for our kind of application, and enforce them in the platform with safe APIs that make the vulnerable code impossible to write, signed builds with a deploy gate, and policy checks on configuration. Then I’d measure adoption of those guarantees, because that is evidence that whole classes of bug are absent.

### On AWS

Safe Coding is language-level, so it travels: a typed query wrapper over the RDS Data API or your database driver, plus a CI rule that bans raw query calls outside that module. Supply chain: CodeBuild or GitHub Actions producing signed provenance, AWS Signer with ECR image signing, and a gate at deploy time (Lambda code signing configurations, or Kyverno or Gatekeeper on EKS verifying signatures). Dependencies: CodeArtifact as the curated repository and Inspector for vulnerabilities. Identity: IAM Identity Center for people, IAM roles and EKS Pod Identity for workloads, VPC Lattice or a mesh for mutual TLS, and Amazon Verified Permissions for fine-grained, relationship-style authorisation. Web controls: terminate TLS centrally at CloudFront or ALB with ACM, and set HSTS, CSP and framing headers once with a CloudFront response headers policy. Safe deployment: CloudFormation Guard or OPA in the pipeline, Service Control Policies, and Config rules for drift. Posture: Security Hub with Config, which the chapter itself names as the AWS equivalent of Google’s Security Command Center.

### Practice question

**We keep finding SQL injection in code review. How would you make it stop?**

Finding it in review means the API lets people write it, and with enough call sites someone always will. So I’d change what can be written.

I’d introduce a small safe query module. It exposes a query type that can only be constructed from a literal in the source code, and a database wrapper whose query method accepts only that type, with all values passed as bound parameters. The raw driver is wrapped and hidden.

Then I’d enforce it mechanically. A CI check fails the build if any file outside that module calls the raw execute method, and another verifies that the query type is only ever built from a constant. Those are narrow, decidable checks, so they don’t produce the noise that makes people ignore scanners.

For existing code, I’d enforce on new and changed code immediately and list the legacy call sites as tracked exceptions. Most can be migrated automatically, and that is a good job for a coding agent, because success is checkable: it builds, it passes the conformance check, the tests pass.

I’d make sure the safe API handles the awkward cases people really have, like dynamic sort columns or variable-length IN lists, with builder functions. If it doesn’t, they will ask for exceptions all day.

Finally I’d report the percentage of services with zero raw query calls. When that reaches 100%, I’m no longer hoping reviewers catch injection. I have evidence the class is gone.

### Practice question

**What does SLSA level 3 give you, and what doesn’t it?**

It gives me confidence about the build. The artifact was produced by a hosted build platform, each run isolated from the others, with signing keys the build steps can’t reach, and there is signed provenance saying which source revision and build process produced it. That defends against someone tampering during or after the build, including an insider or a compromised credential.

It doesn’t tell me the source was good. A malicious or vulnerable change that was reviewed and merged will be built faithfully and signed. For that I need source controls: mandatory second-person review, protected branches and strong authentication.

It doesn’t tell me the dependencies were good either. That needs a curated repository, scanning and update automation.

And provenance only matters if something checks it. So I’d pair it with a deploy gate that refuses anything without valid attestations, with a logged and alerted break-glass path for emergencies.

### Key takeaways

- Developers and AI both make mistakes. Design so the important ones can’t be made.
- A safe abstraction moves risk from thousands of call sites into one module an expert can review.
- Provenance, a deploy gate and policy checks carry the same idea into build and deployment.
- Measure adoption of the guarantees: it is evidence that a class of bug is absent.

## Chapter 16: Reliability: the platform turns SRE into a default

*Author: Bharath Modhipalli and Michelle Brush. Code: POC 16.*

### The big picture

Reliability means meeting what users expect, consistently and correctly. Uptime is one part of it. A system can be up and too slow to use, or up and returning wrong data. The chapter lists six dimensions: availability, latency, correctness, freshness, durability and throughput. For AI services, correctness becomes probabilistic.

The central sentence of the chapter is this one, paraphrased: **SRE provides the blueprint for reliability, and platform engineering provides the machinery that produces reliable services at scale.** Asking every team to learn and apply SRE practices on their own doesn’t scale. The platform’s job is to capture those practices as code and APIs, so a team inherits them by using the standard path.

### The economics: local savings, global costs

Feature teams are rewarded for shipping. That is a local measure. When a team skips resilience work to ship sooner, the cost doesn’t disappear. It moves to the organisation as cascading failures, firefighting and cross-team incident response. Economists call that an externality.

The chapter is kind about motive: teams rarely decide to trade reliability for speed. They assume everything will be fine. It names the result bluntly, though. Reliability becomes an **unfunded local mandate**, and everyone suffers.

A platform internalises the cost. Building an automated canary analysis service might take four engineers several months. After that, no product team writes or watches its own deployment checks, and the investment typically pays back within a year.

> **Canary analysis as a platform gate.** Google’s service compares a new release’s telemetry (latency, errors, resource use) statistically against the version already running. It sits in the deployment platform as an automatic gate. A significant regression stops the rollout and triggers a rollback. Nobody stares at a dashboard during a deploy.

### Four SRE principles, encoded

| Principle                        | What the platform does                                                   | Example from the chapter                                                                                                                       |
|----------------------------------|--------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------|
| Operations is a software problem | Replaces manual work with self-service                                   | Customer onboarding that took weeks of configuration becomes automated, which is faster and makes fewer mistakes                               |
| Eliminate toil                   | Automates routine approvals                                              | Cloud quota increases needed an engineer for hours and customers waited days. Now the system validates and approves reasonable requests itself |
| 100% is the wrong target         | Enforces the velocity-risk balance in the delivery tooling               | Risk profiles (below)                                                                                                                          |
| Learn from incidents             | Changes the system so the right action is easy and the wrong one is hard | Ask what made the action look right to the person at the time, then change the platform                                                        |

#### Risk profiles

This is the most concrete new idea in the chapter. A service’s **risk profile** sets its deployment policy, so nobody has to judge how careful to be with each change.

| Service                                          | Policy the platform applies                                                           |
|--------------------------------------------------|---------------------------------------------------------------------------------------|
| Critical, with a tight error budget              | Multi-stage progressive rollout, long canary bake times, strict automated supervision |
| Low-risk internal tool, or plenty of budget left | Permissive: changes reach production quickly                                          |

The organisation’s risk tolerance is enforced by the pipeline. The safe choice is the default, and low-risk work isn’t slowed down to protect high-risk work.

### Getting the nines

> **Diagram.** Curve of cost and complexity against availability target, rising gently to 99.9% and steeply to 99.999%, with yearly downtime for each level. Allowed downtime shrinks tenfold with each nine while the cost of getting there climbs steeply. Downtime figures are from the chapter.

| Target             | What it takes                                                                                                                                                                                                                                      | Who can fund it                                                                                           |
|--------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------|
| Two to three nines | Engineering hygiene: error budgets, standard pipelines, basic telemetry, automated backups, static multi-zone redundancy, regional load balancing                                                                                                  | Well understood, but still belongs in the platform. Otherwise every team rebuilds it, or quietly skips it |
| Four nines         | A steep step. Active-active across clusters, global application-layer load balancing, N+1 planning by region, automated failover, dynamic capacity, distributed tracing, automated canary analysis and rollback, fault injection and chaos testing | Only a shared platform. Per-team funding is unsustainable                                                 |
| Five nines         | Sharded serving, smart retries everywhere, request hedging, staggered change propagation, autonomous response, analysis of near misses                                                                                                             | Only the most critical shared components                                                                  |

Spanner is the example at the top. Its multi-region service is offered at five nines, and getting there took dedicated GPS receivers and atomic clocks in every data centre for globally consistent time, plus consensus replication across regions. No product team could justify that. As a platform service, a team provisions an instance and inherits it.

### What belongs in the platform

Not everything. A platform stuffed with business-specific logic becomes rigid and hard to understand. The chapter gives a risk-driven test.

- **Blast radius**: If one team’s misconfiguration can hurt everyone, the platform must enforce a standard. One service retrying aggressively without backoff can overwhelm shared databases and load balancers.
- **Complexity**: If a capability takes rare expertise, such as multi-region failover or canary statistics, abstract it so teams don’t each build it.
- **Cost of a mistake**: If an error is minor, leave teams free to choose. If it could be catastrophic, such as draining every region or losing data, the platform takes responsibility and blocks it.

Retries are the model case. Google didn’t ask each developer to write careful backoff loops. Its RPC framework provides adaptive throttling and retry budgets and sheds excess load on the client side. gRPC is the public descendant of that framework.

### Six capabilities to shift down

| Capability                   | What the platform provides                                                                                                                  | Google example                                                                                                                     |
|------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------|
| Abstracting infrastructure   | You declare desired state; the platform keeps it true and reschedules around failures. Critical services can’t be deployed to a single zone | Borg, which makes machine failure invisible to services                                                                            |
| Safe change management       | One opinionated pipeline: staged rollouts, automated canary analysis, automatic rollback, and a clear view of what is deployed where        | The Rollouts platform, whose goal is to make production changes boring and predictable                                             |
| Capacity                     | Forecast-based provisioning, autoscaling and N+1 redundancy by default                                                                      | A long-term planner that forecasts and places capacity, and an autoscaler that reacts in minutes, both horizontally and vertically |
| Preventing unsafe operations | Invariants enforced in code, not in documents                                                                                               | A command that would drain more than one region is rejected                                                                        |
| Standard observability       | The four golden signals for every service, same names and method everywhere, and SLO tracking as a service                                  | One monitoring system fed automatically by every job; tracing built into the RPC library                                           |
| Constant evolution           | Lessons from incidents become platform changes                                                                                              | See “institutional memory” below                                                                                                   |

Two details in that table are worth saying aloud. Capacity changes are rolled out through the *same* progressive pipeline and canary checks as software, so an infrastructure change is as safe as a release. And the platform owns the *how* of deployment while the developer owns the *what*.

> **Break-glass, done properly.** Strict rules sometimes have to be bypassed to restore service. Suppose only signed, scanned images may deploy, and an emergency fix can’t wait for the full pipeline. A break-glass mechanism lets responders override the policy with an explicit marker on the deployment. The important part is what happens next: the override is written to the audit log, a high-priority alert goes to security and operations, and the record is permanent for review afterwards. It is a platform feature with accountability, never a silent bypass.

#### Observability and the human

The chapter describes an incident as a **joint cognitive system**: people and tools share a working memory, with operators relying on the system to show them what is happening. When every service’s metrics have the same names and every dashboard the same layout, responders work from muscle memory and spend their attention on the problem. When each service is different, they spend the first critical minutes decoding the environment.

For AI and agent workloads the golden signals aren’t enough. Add model freshness, version skew, data quality and probabilistic correctness, and for agents: tokens used, end-to-end latency of an invocation, and which external tools were called and how often.

#### The platform as institutional memory

If several teams have outages from the same kind of misconfiguration, the answer is not retraining or a documentation update. Change the platform: add validation, change the default, or remove the setting altogether. That is how an organisation stops having the same outage.

A related feature at Google: any change in source control can be marked as a **bad change**, and the deployment system then refuses every rollout that contains it.

### The reliability of the platform itself

Centralising makes the platform the most critical system in the company. If the deployment system is down, nobody can release, and nobody can roll back either. If monitoring is down, everyone is blind. A reliable platform multiplies stability for everything on it. An unreliable one aggregates risk.

So platform teams must apply SRE to themselves, and to a higher standard than the applications they host.

- **Strict, published SLOs** for the platform: build success rate, deployment latency, monitoring ingestion lag.
- **Defence in depth:** no internal single points of failure, and graceful degradation.
- **Conservative rollouts** with fast rollback, because a platform bug has the whole organisation as its blast radius.
- **Disaster practice** for the case where the platform is the thing that is down.

| Platform          | What its SLOs cover                                                                                                  |
|-------------------|----------------------------------------------------------------------------------------------------------------------|
| Cluster scheduler | Scheduling latency and the share of tasks ready to serve, with tiers: strict for user-facing jobs, relaxed for batch |
| Build service     | Failures caused by the system, deliberately excluding errors the user caused, with latency targets by priority       |
| Monitoring        | Ingestion lag and timely availability, so alerts can be trusted during an outage                                     |

Publishing these turns “the platform is reliable” from a promise into a measurable agreement.

### What the organisation gets

- **Sublinear scale**: Without a platform, operational effort grows in step with the number of services. With one, the cost of each capability is paid once and each fix lands everywhere.
- **Lower cognitive load**: Reliability stops being a pre-launch checklist and becomes the physics of the environment.
- **Fast diagnosis**: The first question in an outage is “what changed?” A platform has one audit trail for binaries, configuration, flags and infrastructure.
- **Fleet-wide remediation**: Patch a shared runtime or proxy once and roll it out everywhere. That is the payoff of golden paths.

The contract from the shared-fate lesson applies. Teams that bypass guardrails or go bespoke create debt the platform can’t see, scale or heal, and the burden returns to them. Staying on the standard path keeps a service *eligible* for automated capacity, failover and fleet-wide fixes.

### Say it in an interview

SRE tells you what reliable looks like; the platform is how you get it for every team without each one learning it the hard way. I’d put into the platform anything with a wide blast radius or a catastrophic failure mode: safe rollouts with automated canary analysis, retry budgets, multi-zone placement, capacity, standard telemetry and SLO tracking. I’d tie deployment strictness to each service’s risk profile. And I’d hold the platform itself to tighter SLOs than its tenants, because when it fails everyone fails.

### On AWS

Risk profiles map well to CodeDeploy deployment configurations and AppConfig deployment strategies: pick linear or canary steps and bake times by service tier, with CloudWatch alarms for automatic rollback. Abstract infrastructure with EKS or ECS spread across at least three Availability Zones through topology constraints the golden path sets for you. Capacity: predictive and target-tracking Auto Scaling, Karpenter on EKS. Unsafe operations: Service Control Policies, Route 53 ARC safety rules that refuse to turn off too many cells at once, deletion protection and AWS Backup with Vault Lock. Observability: Application Signals for golden signals and SLOs on every service, X-Ray or OpenTelemetry tracing injected by the platform. Break-glass: a dedicated emergency role whose use is logged by CloudTrail and raises an EventBridge alert. For the platform itself, publish SLOs for pipeline success, deploy latency and telemetry lag, and test them with Fault Injection Service.

### Practice question

**How do you decide which reliability features go into the platform and which stay with product teams?**

I use three tests. The first is blast radius: if one team getting it wrong can hurt other teams, it belongs in the platform. Retry behaviour is the classic case. A service that retries hard without backoff can take down a shared database, so the client library should enforce backoff and a retry budget for everyone.

The second is complexity. If doing it well needs rare expertise, such as statistical canary analysis or multi-region failover, building it once and offering it as a service is cheaper than having twenty teams each build a worse version.

The third is the cost of a mistake. If the worst outcome is minor, I leave the team free to choose. If it is catastrophic or irreversible, such as draining all regions or deleting the only copy of data, the platform should make it impossible, with a logged break-glass path for genuine emergencies.

What I keep out is business logic. A platform that knows about one product’s special cases becomes rigid and harder for everyone else to understand.

Then I match strictness to risk. A critical service with little error budget gets slow staged rollouts and long bake times automatically. An internal tool gets a fast path. That keeps the safe default from becoming a tax on low-risk work.

### Practice question

**Your deployment platform had an outage and nobody could ship or roll back for two hours. What do you change?**

I’d treat it as the most serious kind of incident, because the deployment system is how every other incident gets mitigated. Losing it removes the main tool for recovery everywhere.

First, the platform needs its own SLOs, stricter than its tenants’, and published: pipeline success rate counting only system-caused failures, time from merge to deployed, and availability of the rollback path as its own objective.

Second, I’d separate the rollback path from the rest. Rolling back to a known-good version should depend on as little as possible: no build step, no external registry call that can fail, cached artifacts. I’d test it with fault injection.

Third, the platform should be rolled out more conservatively than anything it deploys: staged across cells or regions with bake time, so a platform bug hits a fraction of teams first.

Fourth, a break-glass route for when the platform is down: a documented, audited manual deployment that responders have practised.

And I’d run the postmortem with the same question we ask of product teams: what made this failure possible, and which default should change so it can’t recur?

### Key takeaways

- SRE is the blueprint; the platform is how every team gets it by default.
- Shift down what has a wide blast radius, needs rare expertise, or fails catastrophically.
- Each nine costs far more than the last, so only a shared platform can fund the top ones.
- The platform needs stricter SLOs than anything it hosts.

## Chapter 18: Developer experience: platforms nobody uses are worth nothing

*Author: Eric Maxwell. Code: POC 18.*

### The big picture

Organisations spend heavily on internal platforms that are robust, scalable and technically impressive, and then watch adoption stall. Developers keep their old scripts or build unofficial tools around the official one. The platform team is frustrated that nobody appreciates what they built. Developers feel burdened by tools that make their work harder.

The chapter calls this the **platform paradox**. Its explanation is that a platform succeeds or fails less on what it technically provides than on what it is like to use.

### “Build it and they will come”

This is the belief that a technically superior platform attracts users by itself. It misreads developers in three ways.

- **It ignores their workflow**: People have tuned how they work. A tool that makes them abandon that feels like an implant, not an extension.
- **It costs too much attention**: If understanding the platform takes more thought than the business problem, people look for an easier route.
- **The payoff is too far away**: Developers are measured on what ships now. A steep learning curve with long-term benefits loses to a simple fix today, and that is a rational choice.

> **The broccoli problem.** An old saying inside Google went roughly: things that should be easy are medium-hard here, and things that should be impossible are also medium-hard. An engineer made a short cartoon, known as the “Broccoli Man” video, in which someone only wants to serve five terabytes of data and is buried in process. In this book, **broccoli** means paying the setup and running costs of a billion-user system for something small: an internal tool, a prototype, a dashboard. It doesn’t come from incompetence. It comes from putting an application on the wrong kind of platform. The chapter’s example: three days to bring up a “hello world” server because the platform demands cluster names and outdated access settings, for a task that is a one-click form elsewhere.

The costs go beyond wasted investment: lower productivity and morale, burnout, less experimentation, and unofficial tooling that adds debt and security risk.

### What developer experience is

The chapter’s definition, in my words: developer experience is everything a developer encounters, perceives and feels when dealing with a platform, its tools *and the team behind it*. It is a technical discipline about removing friction, and has little to do with keeping people cheerful.

- **Feedback loops**: How fast and how clear the response to an action is. Test times, build times, the quality of an error message.
- **Cognitive load**: How much thinking a task needs. Driven by complexity, the number of tools, and the quality of abstractions.
- **Flow state**: Uninterrupted, absorbed work. Broken by waiting, context switches, external dependencies and toil.

#### Seven pillars

| Pillar                         | What good looks like                                                                                                                                                           |
|--------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Usability and simplicity       | Interfaces are predictable and easy to learn                                                                                                                                   |
| Discoverability and onboarding | People find what they need. The time to a first “hello world” is short and guided                                                                                              |
| Fast, clear feedback           | Builds, tests and deploys are quick. Errors say what went wrong and what to do                                                                                                 |
| Reliability and trust          | The platform behaves the same way every time                                                                                                                                   |
| Workflow integration           | API-first, so every interface has the same abilities (below)                                                                                                                   |
| Flexibility and escape hatches | Sensible defaults for about 80% of cases, and a supported way out for legitimate special needs. Paved roads shouldn’t be prisons                                               |
| Documentation and support      | Accurate, searchable, full of working examples, with responsive help. Research finds documentation quality predicts whether teams can adopt practices like continuous delivery |

> **Diagram.** Four interfaces (web console, command line, infrastructure as code, AI agents) all call one platform API, which exposes the capabilities. API-first. The console is one client of the API, exactly like the command line, infrastructure-as-code providers and agents. Nothing can be done in one that can’t be done in the others.

This settles the old argument about clicking in a console versus automating. A good console is the best way to explore and understand a system’s state. The API underneath means the same action can be scripted when it becomes routine. People move from exploring by hand to automation without changing tools.

### Why it is a business matter

- **Productivity.** The best-performing organisations in the DORA research aren’t working longer hours. Their tools remove friction, so lead times are hours, not weeks. One survey cited in the chapter found developers spend more than 15 hours a week on tasks other than writing application code.
- **People.** Satisfaction with tools tracks team performance and lower burnout. An employee recommendation score measures past friction, which makes a falling score an early warning of future productivity loss. Good tooling also helps hiring and retention.
- **Innovation.** If trying an idea takes minutes, people try ideas. That is psychological safety in practical form.
- **Risk.** A service template that arrives with security scanning, structured logging and monitoring already wired makes the right way the easy way. Developers meet complex standards without becoming experts in them. Investing in experience is investing in risk management, which matters most in regulated industries.

### Cultivating it: build with, not for

| Practice                   | How                                                                                                                            |
|----------------------------|--------------------------------------------------------------------------------------------------------------------------------|
| Interviews and observation | Ask developers to walk you through their work. Watching where they get stuck tells you more than asking what they want         |
| Informal usability tests   | Have someone try a new feature while sharing their screen and thinking aloud. Minutes, not weeks                               |
| Mine the support channels  | Recurring questions point at gaps in documentation or flaws in design                                                          |
| Personas and journey maps  | A new hire, a frontend specialist and a principal backend engineer need different things. Check the personas against real work |
| Close the loop             | Act on feedback and say what changed. That is what earns more feedback                                                         |
| Value stream mapping       | Draw every step, hand-off and wait from idea to production. The waits are where flow dies                                      |

Then make sure people know. The chapter lists: a public roadmap and clear release notes; documentation treated as a feature; support that behaves like a partner and never like a gatekeeper; a user community; **champions** in product teams who get previews and a direct line; and published success stories. This has to be in the platform team’s charter, with time allotted.

> **Go as a developer-experience story.** The Go language began because three senior engineers were suffering with slow builds, tangled dependencies and awkward concurrency in C++. They were their own users. Experience was designed in from the start: a formatter that ended style arguments, simple dependency fetching, built-in testing and a fast compiler. The creators acted as the first champions and worked closely with early adopter teams. It spread from the ground up because the compiler and tooling were treated as a product.

### Measuring it

| Kind     | Metric                                                                                                                    | What it tells you                                                                        |
|----------|---------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------|
| Numbers  | HEART: happiness, engagement, adoption, retention, task success                                                           | Google’s user-experience framework, applied to an internal platform                      |
| Numbers  | Adoption and retention                                                                                                    | Active users against those who tried it once and left                                    |
| Numbers  | Task time and first-attempt success                                                                                       | Friction, directly. How long to deploy a new service? How often without asking for help? |
| Numbers  | DORA delivery metrics: lead time, deployment frequency, change failure rate, failed-deployment recovery time, rework rate | Compare teams on the platform with teams off it. The strongest proof of value            |
| Opinions | Satisfaction and “would you recommend this platform?” scores                                                              | Sentiment over time                                                                      |
| Opinions | Themes in interviews, surveys and tickets                                                                                 | The reasons behind the numbers                                                           |

### Say it in an interview

A platform is only worth what its adoption is worth, and adoption depends on how it feels to use. I look at three things: how fast and clear the feedback is, how much a developer has to hold in their head, and how often they’re interrupted. I’d build with the users, watching them work, then measure time to first deploy, first-attempt success, and delivery metrics for teams on the platform against teams off it.

### On AWS

Give the platform one API and let every interface sit on it: a Backstage portal or Service Catalog for discovery, the same actions available through the CLI, CDK constructs or Terraform modules, and tool definitions agents can call. Golden-path templates should arrive with a pipeline, IAM roles, alarms, dashboards and tracing already configured, so the first deploy takes minutes. Measure it: emit pipeline events through EventBridge to compute lead time, deployment frequency and failure rate per team, and track time from repository creation to first production deploy. Provide an escape hatch as a documented, supported extension point instead of leaving teams to fork the template.

### Practice question

**Your platform team built a deployment system that is clearly better than what teams use, and adoption is 15%. What do you do?**

I’d assume the problem is the experience, not the users, and go and watch.

I’d sit with three or four teams, some who adopted and some who didn’t, and ask them to deploy something while I observe. I’m looking for where they stop: an unclear error, a concept they have to learn first, a step that needs a ticket, something their current script does that ours doesn’t.

I’d measure the first-run experience. How long from nothing to a first successful deploy, and how often it works on the first attempt without help. If that is days, nothing else matters yet.

I’d check for broccoli: are we making a small internal service fill in the same configuration as our largest product? If so, we need a lighter path with good defaults.

Then I’d fix the top two or three sources of friction, tell people what changed, and recruit a champion in each adopting team. I’d publish one honest success story with numbers.

I would not reach for a mandate first. A mandate without a good product gets compliance on paper and workarounds in practice. If a mandate is eventually needed for security or compliance reasons, it goes much better after the product is something people would choose.

### Key takeaways

- Adoption depends on the experience of use more than on technical merit.
- Three dimensions: feedback loops, cognitive load, flow.
- Build with your users, give them a way out for special cases, and measure adopters against non-adopters.

## Chapter 19: Platform as a product: from good intentions to an operating model

*Author: Eric Maxwell. Code: POC 18.*

### The big picture

The previous lesson said developer experience decides whether a platform succeeds. That is a goal. This lesson is the method: run the internal platform with the discipline of product management, as if it were something you sold.

### Projects and products

|               | Project                           | Product                                        |
|---------------|-----------------------------------|------------------------------------------------|
| Shape         | Defined scope, a start and an end | A lasting system for delivering value          |
| Success       | On time and on budget             | Outcomes for customers                         |
| Incentive     | Deliver what was planned          | Deliver what is needed                         |
| When it ships | The team moves on                 | The work continues: support, debt, improvement |

The chapter says much of the friction Google Cloud sees in customers adopting platform engineering comes from running it as a project. Three pillars define the alternative.

- **A defined customer**: Not “the developer”. A new hire needs smooth onboarding and happy-path documentation. A principal engineer on core services needs advanced configuration and deep observability. A frontend developer needs fast feedback on UI changes.
- **A clear value proposition**: Why should someone use this instead of what they have? The alternative may be a favourite script, an open-source tool or doing nothing.
- **An indefinite lifecycle**: From idea through growth and maturity to retirement. The job is never done.

#### Jobs to be done

The value proposition comes from the **job** a developer is trying to get done, which is rarely the feature they ask for. “I need a deploy button” is a request. “I need to get my change to production quickly and with confidence” is the job.

The chapter’s example: a developer asks for a dashboard of build logs. The job is “when my deployment fails, I need to find the cause quickly so I can fix it.” Seen that way, the better answer may be clearer error messages, a chat notification that links straight to the failing step, or detecting the failure before they notice.

### The product surface area

This is the inventory of every point where a developer, *or their AI assistant*, touches the platform. The chapter insists on mapping it twice: once for human usability and once for machine discoverability.

| Surface                   | For humans                                                                                                            | For agents                                                                                                                                                     |
|---------------------------|-----------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Interfaces                | APIs, command line, console, SDKs, config files and error messages                                                    | Strict API specifications, predictable names, well-defined tool schemas, and errors with plain-text context. An obscure error code makes an agent invent a fix |
| Documentation             | Guides, tutorials, references, troubleshooting. A first-class feature                                                 | Structured and machine-readable. Your docs are what your assistant knows. Stale docs produce confident wrong answers                                           |
| Onboarding                | Time to first “hello world”. A bad first run loses people before they see any value                                   | Can an agent create that first application unaided?                                                                                                            |
| Support and communication | Chat channels, office hours, tickets, release notes, the roadmap, and a way to propose changes to the platform itself | The same channels, increasingly answered with AI help                                                                                                          |

> **The engine and the car.** The API is the engine; the product is the whole car, and nobody buys just an engine. The chapter updates the image: today’s car has self-driving. If the dashboard is beautiful and the engine’s sensors can’t talk to the self-driving system, the car crashes. Your APIs are the sensors and the agents are the self-driving system.

### The platform product manager

A product manager for something that earns no revenue can look like a luxury. The chapter argues the role is the owner of the developer experience and the link between what the platform can do and what the organisation needs.

- **Shape the vision.** Where is the platform going, and why does that matter to developers and the business?
- **Be the customer’s voice** in every planning and prioritisation discussion.
- **Translate in both directions.** Developers’ needs into terms leaders use, such as delivery metrics and time to market; leaders’ goals into a roadmap engineers can build.
- **Prioritise.** Make the trade-offs between user value, feasibility and business impact.

They do it with engineering and design from the first day. Throwing requirements over a wall is named as an antipattern. If there is no dedicated person, the engineering manager or tech lead wears the hat, and must protect time for talking to users, or delivery pressure will eat it.

#### Discovery habits

- Talk to developers regularly, as open conversations about their work. These are not pitches.
- Run journey-mapping workshops on one workflow, such as onboarding a new service. Sticky notes on a wall expose hidden friction fast.

The purpose is to avoid the most common failure: an elegant platform that solves a problem nobody has.

#### Build, buy or partner

1.  Is this a core competency or a competitive advantage? Then build. A trading firm builds its own low-latency trading system.
2.  Does something existing solve 80% of it? Then lean towards buying or partnering. The lifetime cost of building and maintaining in-house is usually far more than the licence.
3.  Can you adopt an off-the-shelf product and spend your engineering on the unique last mile? Often the most practical answer. Less engineering, though never none.

#### The capability roadmap

A roadmap is a communication tool. It says which problems you will solve and why, and it is neither a release plan nor a backlog. Write outcomes (“enable self-service database provisioning”), not features (“build database API v1”).

1.  **Now**: Being built. High confidence
2.  **Next**: In discovery
3.  **Later**: Direction only. No promised solutions

### The lifecycle

| Phase                         | What to do                                                                                                                                         | Antipattern                                                                                    |
|-------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------|
| 1 · Conception                | State a hypothesis: by solving X for developer Y we get outcome Z. Test it cheaply with a hand-run MVP (below)                                     | Vanishing for six months to build a perfect first version                                      |
| 2 · Ramp                      | Turn what worked by hand into a self-service **golden path**: the opinionated, documented, supported way. Sell it with examples, demos and pairing | Mandates without a good product, which produce resentment and malicious compliance             |
| 3 · Maturity                  | The platform is the default. Open safe extension points so others can build on it                                                                  | Tyranny (a rigid path nobody may leave) or chaos (so much customisation it can’t be supported) |
| 4 · Evolution and end of life | Keep scanning for what is changing. Retire things deliberately                                                                                     | The ghost ship: an old platform left to decay with no owner                                    |

#### The MVP you run by hand

Want to build a deployment pipeline? Write no code yet. Find a friendly team and do their deployments for them for two weeks: run the scripts, provision the infrastructure, watch the logs. It doesn’t scale and isn’t meant to. It shows you every edge case and last-mile problem a whiteboard would miss. You are looking for a problem so basic that developers hit it several times a day. Write code only after a handful of hand-served teams are happy.

#### From golden path to town square

A mature platform is less like one road and more like a town square. The platform team provides the paving, lighting and plumbing, meaning reliability, security and core APIs, and keeps the main roads that take 80% of people where they need to go. Around the square, other teams build their own shops through plugins, extension points and contribution models. The community solves its long-tail problems and the platform team stays on the core.

> **“Adoption is voluntary, even when it’s mandatory”.** The chapter’s best line. You can order people to use a platform. You can’t order them to use it well. A top-down mandate without a product worth choosing gets obedience to the letter and workarounds in spirit.

#### Deprecation is a launch in reverse

1.  A plan: a timeline, a migration path and a reason people will accept.
2.  Communication, early and repeated, in several channels.
3.  Tooling and support. Automate the migration where you can.
4.  A final off switch. Until the old system is turned off, you haven’t collected the benefit.

To find out who still depends on an old service, run a **brownout**: break it deliberately for a short time and see who notices.

### A scorecard with three views

| View     | Question                          | Metrics                                                                                                                                                       |
|----------|-----------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------|
| User     | Do developers use it and like it? | Adoption and retention, satisfaction scores, first-attempt task success, time to “hello world”, themes from feedback                                          |
| System   | Is it healthy and affordable?     | Reliability against SLOs; cost of goods sold: infrastructure cost per active user, per service or per build                                                   |
| Business | Does it move the organisation?    | Delivery metrics for adopters, time to market, security and compliance (fewer vulnerabilities per service; share of services meeting a supply-chain standard) |

Read them in that order. If developers don’t use the platform, the other two views don’t matter. Rising cost per user without more adoption or capability is a warning. And beware vanity metrics: “total deployments” says nothing about whether anyone is better off.

### Say it in an interview

I run a platform as a product, not a project. That means named customer segments, a value proposition measured against whatever they use today, and a lifecycle that includes retirement. I find the job behind each feature request, validate it by doing the work by hand for a couple of teams, then pave it as a golden path and earn adoption. I report three views: whether developers use it, whether it is reliable and affordable, and whether teams on it deliver faster and safer.

### On AWS

A golden path on AWS is a template that produces a repository, a pipeline, IAM roles, alarms and dashboards in one step, published through Backstage or Service Catalog and built from shared CDK constructs or Terraform modules. Extension points are versioned constructs teams can compose, with Service Control Policies marking what can’t be changed. For the scorecard: adoption from tags or template usage, cost per service from Cost and Usage Reports with cost allocation tags, platform SLOs in CloudWatch, and delivery metrics from pipeline events. For deprecation, use CloudTrail and access logs to find remaining callers, then a scheduled brownout with a 4xx response that names the replacement.

### Practice question

**You’ve been asked to build an internal developer platform from scratch. What are your first ninety days?**

I’d spend the first weeks not building. I’d interview and shadow developers across a few team types to find where their time goes between writing code and seeing it in production, and I’d map one or two workflows end to end with every wait and hand-off.

From that I’d pick one job that is painful and frequent, probably something like “get a new service safely to production”. I’d write the hypothesis down: solving this for these teams should cut their lead time by this much.

Then I’d run it by hand. For two or three friendly teams, my team does the work for them for a couple of weeks. That shows the edge cases and tells me whether the problem is real before I’ve built anything.

In the second month I’d automate what worked into a thin golden path: a template that gives a repository, pipeline, permissions and monitoring with good defaults, and documentation with a working example. I’d measure time to first deploy and first-attempt success from day one.

In the third month I’d widen to more teams by invitation, with pairing sessions and a champion in each. I’d publish a now-next-later roadmap and the first numbers.

I’d decide build against buy for each piece as I go. Most of the pieces exist; my engineering should go into the integration and the last mile that is specific to us.

What I’d avoid: a six-month build in isolation, a mandate before the product is good, and features nobody asked for.

### Practice question

**How do you retire a platform that 40 teams still use?**

I treat it as a product launch run backwards, and I start with the replacement. If the new path isn’t clearly better and ready, the deprecation will fail however well I communicate.

I’d publish a plan with a timeline, the reason, and a migration path for each kind of user. I’d find out who really uses the old system from logs, since the list of who says they do is always wrong.

I’d make migration cheap: automated tooling where possible, pairing for the hard cases, and visible tracking so teams can see where they stand.

I’d communicate early and repeatedly, in the channels teams read, and to their managers as dates approach.

Before the end I’d run brownouts: short, announced outages of the old system that surface the callers nobody knew about.

And I’d turn it off on the date. A platform that is deprecated and still running is a ghost ship: it keeps costing money, carries security risk and has no owner.

### Key takeaways

- A product has customers, a value proposition and a lifecycle. A project has a deadline.
- Find the job behind the request, and prove it by hand before automating.
- Golden path first, then extension points; retire old platforms on purpose.
- Score it from three views: user, system, business.

## Chapter 22: AI and platform engineering: a dual mandate

*Author: Isaac Albarran with Konrad Dryja. Code: POC 19.*

### The big picture

- **Platforms for AI**: Infrastructure, abstractions and workflows for the whole life of a model. Usually called MLOps.
- **AI for platforms**: Using AI to improve how the platform itself is designed, automated, observed and run. Usually called AIOps.

The two feed each other. A well-abstracted platform is what lets an organisation use AI at scale, and the intelligence that produces is then turned on the platform. The chapter is written from Google’s position: the same investments that made Search and Gmail possible, in cluster management, distributed storage and custom accelerators, are what made training very large models possible.

> **A naming point.** The chapter refers to Google Cloud’s managed AI service as “Agent Platform”, with components for pipelines, a feature store, a model registry and experiment tracking. I use generic names here, since the ideas apply on any cloud.

### Why AI needs its own platform

An AI system is more than code. It is code, data and model configuration bound together, and that three-way coupling multiplies complexity. In ordinary software a person writes the logic. In machine learning the logic is learned from data.

The chapter’s instruction is the **abstraction imperative**: servers were abstracted into virtual machines and containers to free application developers, and now accelerators, data pipelines and training workflows must be abstracted to free ML engineers.

1.  **Data**: Ingest, clean, track lineage
2.  **Experiment**: Non-linear. Failure is normal
3.  **Train**: Days or weeks on accelerators
4.  **Productionise**: Version, canary, roll back
5.  **Serve**: Latency and throughput
6.  **Monitor**: Drift, then retrain

*Each stage has a reliability problem ordinary web services don’t. Data is treated as a liability as much as an asset.*

One term to know: the **configured model** is the complete set of code, data and hyperparameters. An experiment can be reproduced only if all three are captured.

#### Hiding the hardware

| Abstraction             | What it means                                                                                        |
|-------------------------|------------------------------------------------------------------------------------------------------|
| Resource virtualisation | Model code doesn’t name hardware. The platform schedules onto whatever accelerators are free         |
| Fault tolerance         | Automatic checkpoints and restarts. A node failing in a week-long run loses nothing and needs nobody |
| Scalability             | Training across hundreds of chips without anyone wiring up the interconnect by hand                  |

A researcher should be thinking about the model. The topology of an accelerator pod and the driver versions of a GPU cluster belong to the platform.

#### The well-lit path for ML

- **Standard pipelines**: Preprocess, train and evaluate as defined steps that run the same way every time.
- **A central feature store**: One source for feature values, so the value used in training is exactly the value used in serving. This is the main defence against training-serving skew.
- **A model registry**: The source of truth for models: versions, lineage, and which version is the default for prediction.

### The quality attributes, applied to AI

#### Efficiency

Training one large model can use enormous amounts of energy and compute. Managing accelerators centrally lets the platform scale predictively and right-size from usage history, where teams would otherwise hold expensive hardware idle. And an improvement to a shared piece, such as the data-loading library or the serving protocol, reaches every AI team at once. The chapter calls it a flywheel.

#### Reliability: the silent failure

In ordinary software, a fast “200 OK” usually means the service works. A model endpoint can return a fast 200 with an answer that is wrong or harmful. So model and data quality become first-class reliability signals.

| Signal                    | What can go wrong                                                                                                    | Example                                                                            |
|---------------------------|----------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| Model freshness           | A model starts ageing the moment it ships, because the world moves                                                   | A stale fraud model is a reliability incident even while the API is healthy        |
| Data quality              | Inputs drift away from what the model was trained on. Different from integrity, which asks whether a file is corrupt | A fraud model tuned on transactions of \$10 to \$500 starts receiving \$5,000 ones |
| Probabilistic correctness | Outputs aren’t deterministic, so you can’t assert on them                                                            | Use confidence thresholds and safety filters, and block low-confidence answers     |

That last row contains a trade worth naming: the platform chooses to refuse an answer, giving up some availability, to avoid a confident wrong one. It is fail closed, applied to a model.

#### Safety and security

- **Supply chain.** Scan containers, and deploy only signed and verified models.
- **Protecting the weights.** Model weights are often core intellectual property. Confidential computing keeps data and models encrypted while in use, shielding them even from platform operators and the infrastructure provider.
- **Adversarial defence.** Input and output guardrails deployed as gateways in the infrastructure, working independently of the model, to catch prompt injection, jailbreak attempts and toxic output.
- **Safe change.** Canary a new model version on a fraction of traffic and roll back automatically if metrics fall.

#### The middle layer

Between feature teams and the AI backends sits integration glue. Done badly it slows everyone down or gets ignored. Done well it saves feature teams from repeating integration work and lets the backends scale without their effort growing in step. Because AI changes so fast, the chapter sets three rules for it.

1.  **Iterate quickly.** Prefer small prototypes, with a plan to harden the parts that prove themselves.
2.  **Velocity first.** The layer exists to remove overhead. Any part that slows teams without a clear benefit destroys its own value.
3.  **Expect pivots.** Deliver something partial early. A command-line tool this month can beat a polished web application next quarter, and is easier to change.

ML engineers are also a distinct kind of customer. Their work is iterative and lives in notebooks, so offer SDKs before command lines, and visual tools for lineage, training curves and comparing experiments.

### AI for platforms

Modern platforms produce more telemetry than people can read. The chapter describes AIOps as the highest-leverage form of shifting down: expert operational knowledge encoded into tools that watch, predict and act.

1.  **Make sense of the noise.** One failure can set off thousands of alerts across dependent services. Models correlate them, narrow down the source and produce one targeted alert.
2.  **Predict.** Learn normal behaviour in place of fixed thresholds. Catch memory leaks and failing hardware early, and forecast capacity shortfalls in time to provision.
3.  **Assist the operator.** Ask in plain language what caused a latency spike. Have incident chat summarised and the postmortem drafted. Get a probable cause and a suggested playbook, with a person still deciding.
4.  **Act.** Schedule workloads against performance, cost and energy together. Restart a stuck process or roll back safely without waiting. Scale ahead of demand using history and upstream traffic.

#### Agentic platforms

Platforms now have a second kind of user. Consoles, APIs and SDKs serve people. Agents need structured, intent-based APIs and tool definitions they can discover and reason about.

When agents do the operating, the platform’s role moves from supplying tools to supplying **controls and policies**. An autonomous agent may wander from what was intended, so the platform has to be the physics of the environment: the security, compliance and reliability limits that hold whatever the agent tries.

> **Back to pace layers.** The chapter closes with the layers model from lesson 2. AI applications are the fast layer, changing constantly. The platform is the slow, stabilising layer. It absorbs the shocks and gradually takes in what has proven itself above.

### Say it in an interview

There are two jobs. One is building the platform AI teams need: hide the accelerators, give them standard pipelines, a feature store and a model registry, and treat freshness, drift and confidence as reliability signals, because a model can return a 200 and be wrong. The other is using AI to run the platform: correlate alerts, predict problems, assist responders and, with guardrails, act. In both, the platform’s part is the controls that hold regardless of what a model or agent does.

### On AWS

For the ML path: SageMaker Pipelines for standard workflows, Feature Store against training-serving skew, Model Registry with approval status as the source of truth, managed training with checkpointing and Spot for fault-tolerant jobs, and Model Monitor for data and quality drift. For generative workloads, Bedrock Guardrails act as the input and output gateway independent of the model, and Nitro Enclaves or confidential instances protect weights in use. Sign model artifacts and gate deployment on the signature, as with any other binary. For AIOps: CloudWatch anomaly detection and investigations, DevOps Guru for correlated insights, predictive scaling, and agents whose permissions are bounded by IAM and Service Control Policies so the limits hold whatever the agent decides.

### Practice question

**A model endpoint has 100% availability and low latency, and the business says predictions have got worse. How should the platform have caught this?**

This is the silent failure that ordinary monitoring can’t see. The four golden signals measure whether the service answered. They don’t measure whether the answer was good.

The platform should treat three more things as reliability signals. Freshness: how old is the model and the data it learned from, against a target for this use case. Data quality: are the live inputs still distributed like the training data? I’d compare feature distributions continuously with a drift measure and alert on a threshold. Output quality: track confidence, the rate of low-confidence answers, and wherever ground truth arrives later, accuracy against it.

I’d also check for training-serving skew, where a feature is computed one way in training and another way in serving. A central feature store prevents that by serving the same value to both.

Then I’d connect the signals to action: a drift alert opens a retraining pipeline; a new model version goes out as a canary with automatic rollback; and for high-stakes predictions a confidence gate declines to answer when the model is unsure, which gives up a little availability to avoid confident mistakes.

I’d give the model an SLO in those terms, alongside the latency one. If quality isn’t in the objective, nobody is paged when it fails.

### Key takeaways

- Two mandates: build platforms for AI, and use AI to run platforms.
- A model can be up and wrong. Monitor freshness, drift and confidence.
- Abstract the hardware; give ML engineers pipelines, a feature store and a registry.
- With agents operating, the platform’s job is the controls that always hold.

## Chapter 24: Education: why teaching belongs to the platform team

*Author: Titus Winters.*

### The big picture

The chapter opens with a rule from its author that is worth memorising: if something is accidentally complex, simplify it; if it is inherently complex, educate.

Its argument has three steps. Engineering performance comes from culture. The root of good culture is learning and growth. And somebody has to be responsible for the learning that can’t be left to chance, which is most naturally the platform organisation.

### A culture of learning

Management thinkers, academic researchers, Google’s own team studies and the DORA research all point the same way: culture is at the root of performance. The culture they describe is **psychological safety**, where it is safe to be wrong, safe not to know, and safe to make an honest mistake.

The chapter makes a sharper point than “people work better when they aren’t afraid”. Safety is what lets information move and makes learning valued.

> **What psychological safety does not excuse.** A sceptic once told the author that it just lets people off for failing. His answer: it excuses *honest, novel* mistakes. Repeating the same error, or doing something plainly careless, should still count against you. The aim is that an organisation learns each hard lesson once, not once per engineer because everyone hides their failures.

#### Who gets the next task?

An old model from the 1970s, the “surgical team”, gives the critical work to the best engineer and has everyone else support them. The chapter explains why that no longer fits, in game-theory terms. It was a strategy for a single game: assemble a team, build one system, disband. Modern engineering is an endless stream of projects with people moving between teams.

1.  **Single game**: Give everything to your best person
2.  **Endless game**: Give the next task to the most junior engineer who can do it with some guidance

*The second rule values growth, and frees senior people for new problems and mentoring.*

#### Brittle productivity

Research by Cat Hicks describes what happens without a learning culture. Only submitted code counts. Investigating, understanding and explaining look like waste. Teaching isn’t rewarded. Engineers come to define productivity as effort, hours and solitary work, which the chapter calls performative hustle. Her terms are **learning debt** and **brittle productivity**.

It suggests a reframing borrowed from her: stop saying “developer productivity” and say “developer problem solving”. That makes it obvious that skills and understanding are the thing to build.

Documentation is where this shows. It is the one factor in the DORA research that may matter even more than team culture, and it is the most visible, measurable sign of whether a team values the group’s output over individual output.

> **A thought experiment.** Which team would you rather lead? One that is forbidden from using any IDE or AI assistant and keeps everything else. Or one with every modern tool that can never learn anything beyond what its members were taught at university. Tools help. Without learning, engineering stops.

### Why universities can’t do it for us

- **The field is young.** Certification works for disciplines that are centuries old. Software engineering is about fifty years old and still finding its best practices.
- **There aren’t enough hours.** All the lectures, labs and homework in a computing degree add up to less than 18 months of full-time work, and less than a third of the popular “10,000 hours to mastery” figure.
- **The content is skewed.** Students learn to implement a linked list more than they learn when to use one.
- **Software engineering is programming plus time plus people.** Version control, testing and design patterns exist to cope with change over time and with other engineers. A course can’t make either of those real.
- **Student teams aren’t teams.** Real teams mix experience levels, have authority structures and face a stream of work.
- **Nobody reads the code.** Enrolment in the US grew about fivefold in 15 years and teaching staff didn’t, so early courses are graded automatically on whether the output is right. Some graduates have never had a person comment on their code.

At Google a new hire’s first code review is treated as a rite of passage. It teaches the difference between “it seems to work” and “it is done to a quality we can afford to maintain”.

### Why education belongs with the platform

A company’s business strategy is to diversify into many products, each with its own specialists. Its infrastructure strategy should be to keep one platform. So the platform organisation is the one part of engineering that sees the whole enterprise and works on what all teams share.

- **Expertise accumulates there.** Being the Java expert on a team of ten is one thing. Being the person 10,000 Java engineers bring their questions to is another. That depth is learned from answering the same questions and collecting the edge cases.
- **The platform chooses what is easy.** If it has made one way standard, it owes people an explanation of that way. Managing the community actively beats hoping good practice spreads by itself.
- **The missions match.** Education increases engineering capacity and reduces waste, misuse and misconfiguration of expensive systems. That is the platform’s purpose too.

#### How to staff it

| Option                          | Verdict                                                                                                                                                                                         |
|---------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Everyone teaches, with targets  | No. Good educators are rare, and the wrong person in that role does harm                                                                                                                        |
| A separate education department | No. It drifts away from current practice and real problems                                                                                                                                      |
| Matrixed                        | Yes. On each component team, a few engineers who like to write or teach get part of their time for community support, writing up best practice, and building and delivering training. Reward it |

The chapter compares this to how SRE treats toil. When you are tired of answering the same question, write the essay, record the talk or build the class. Done well, education reduces the support load the same way automation reduces operational load.

Keep the scope tied to what the platform supports. A company standardised on Go, Kubernetes and a managed Git service should teach those, and should not branch into unrelated topics. For general material, **curate** instead of producing. Popularity is a poor guide: studies in physics education found that students’ own rating of how much they learned tracks how much they liked the instructor, and has little to do with measured learning.

### Education and AI

The chapter quotes the 2025 DORA finding that AI is an **amplifier**. It magnifies the strengths of organisations that work well and the dysfunction of those that don’t. The returns come from the underlying system: the quality of the internal platform, clear workflows, aligned teams.

- **Clean up your documentation**: Your tools are internal, so a general model doesn’t know them. You point it at your docs. If they are current, the assistant is useful. If they are stale, it repeats stale answers and invents the rest. AI can’t tell an outdated page from a current one.
- **Teach specification**: Writing new code is no longer the bottleneck. Describing precisely what is needed is: requirements, contracts, constraints, architecture.
- **Teach verification**: The other bottleneck is checking that the result is fit for purpose: reading code, reviewing, testing, thinking critically.

Both onboarding and retraining need this. The chapter’s closing view is that software engineering can’t really be separated from education, and AI has made a long-postponed investment urgent.

### Say it in an interview

I think of education as part of the platform’s job. The platform team sees every team’s problems and decides what the standard way is, so it should also explain that way. I’d give a few engineers on each platform component real time for support, writing and teaching, and I’d treat repeated questions as toil to automate with documentation. With AI in the picture it matters more: assistants answer from our docs, and the scarce skills are now specifying what we want and verifying what we got.

### On AWS

Make documentation part of the golden path: every template ships a README, a runbook and architecture notes in the repository, rendered in the developer portal. Keep them current with ownership metadata and a staleness check in CI, because that corpus is what an internal assistant (Amazon Q Business or a Bedrock knowledge base) will answer from. Scope training to what the platform supports, and curate AWS Skill Builder paths instead of writing general cloud courses yourself. Use game days and Well-Architected reviews as teaching moments, not audits.

### Practice question

**We’re rolling out AI coding assistants to 500 engineers. What would you do to make that pay off?**

I’d start from the finding that AI amplifies whatever is already there. If our platform, workflows and documentation are in good shape, assistants will help a lot. If they aren’t, we’ll produce confusion faster. So part of the rollout is fixing the foundations.

First, documentation. Our internal tools aren’t in any public model’s training, so the assistant will answer from our docs. I’d audit the most-used pages, delete or fix the stale ones, give every page an owner and a review date, and make the content structured enough for a machine to use.

Second, guardrails in the platform, so generated code is safe by construction: safe APIs it must compile against, signed builds, policy checks at deploy. Then review doesn’t have to catch everything.

Third, training, aimed at the new bottlenecks. Writing code is cheap now. Specifying precisely what we want and verifying what comes back are the scarce skills, so I’d teach requirements and contracts, code reading, review and testing, to juniors and seniors alike.

Fourth, I’d protect how juniors learn. If the assistant does every task a junior would have learned from, we’ll have no seniors in five years. I’d keep giving juniors real tasks with guidance and make explaining the result part of review.

I’d measure delivery metrics and satisfaction before and after, by team, and expect the gain to be largest where the foundations were strongest.

### Key takeaways

- If it is accidentally complex, simplify. If it is inherently complex, educate.
- Give the next task to the most junior engineer who can do it with guidance.
- Education fits the platform team: it sees everything and sets the standard way.
- AI answers from your docs, and makes specification and verification the scarce skills.
