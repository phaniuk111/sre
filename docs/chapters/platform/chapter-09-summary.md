# Platform chapter 9: Coupling: decide what depends on what

*Platform Engineering at Google (early release). Course lesson: `#pe-1`. Code: POC 12. Read: full text, one pass; all figures seen.*

## Summary

Coupling is how much the parts of a system depend on each other. It is usually talked about as a defect. This chapter’s position is more useful: some coupling is unavoidable, some is valuable, and the real failure is coupling nobody chose.

**Cohesion** is the mirror image: how closely related the things inside one module are. A module with low cohesion does many unrelated jobs, so either it depends on many things or many things depend on it. Low cohesion and high coupling tend to arrive together.

Google has a name for what you give up: **retargetability**, the ability to reuse a part of the system for a different purpose. The trade is engineering efficiency against retargetability.

One warning on performance. Couple for speed only after other options are exhausted. Tight coupling can block later optimisation, because speeding up one module may break a timing assumption in another.

## Key ideas

- Explicit and implicit coupling, tight and loose, and how cohesion relates
- Four reasons to couple on purpose and four costs of doing it
- Five patterns that loosen coupling and four antipatterns that tighten it by accident
- Four ways to find coupling nobody intended

## What the lesson covers

- The big picture
- When coupling pays
- When coupling costs
- Finding the balance
- Five kinds of coupling
- Patterns that loosen coupling
- Antipatterns that tighten it by accident
- Finding coupling nobody intended

## Claims and numbers

- When many people left Twitter in 2022, they overwhelmed Mastodon’s servers.

## Terms

Cohesion, Efficiency, Performance, Atomicity, Traceability, retargetability, Reuse, Extensibility, Robustness, Freedom of choice, Google’s own trade, Shared database, Distributed monolith, Megamorphic artifact, Control coupling, Stuck flows

## Interview line

I don’t treat coupling as good or bad. I ask what it buys and what it costs. It buys efficiency, performance, atomicity and traceability, and it costs reuse, extensibility, robustness and freedom of choice. So I decide which of those my users care about, couple deliberately for that, and then go looking for the coupling nobody chose, with dependency analysis, tracing and fault injection.

## On AWS

The loose patterns map directly: SNS and EventBridge for publish-subscribe, Kinesis and Step Functions for pipelines, API Gateway and versioned APIs between services, IAM Identity Center for federation. For the shared-database antipattern, give each service its own DynamoDB table or Aurora cluster behind an API and let AWS Backup carry the common concerns. To discover hidden coupling, use the X-Ray or Application Signals service map for runtime calls, CloudTrail to see who touches which table or bucket, and Fault Injection Service to remove an Availability Zone and watch what fails.

## Takeaways

- Coupling should be a decision. The dangerous kind is the kind nobody chose.
- It buys efficiency, performance, atomicity and traceability, and costs reuse, extensibility, robustness and choice.
- Shared databases, distributed monoliths, junk-drawer configs and behaviour flags are how it sneaks in.
