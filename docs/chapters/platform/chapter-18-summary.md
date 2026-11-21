# Platform chapter 18: Developer experience: platforms nobody uses are worth nothing

*Platform Engineering at Google (early release). Course lesson: `#pe-7`. Code: POC 18. Read: full text, one pass; all figures seen.*

## Summary

Organisations spend heavily on internal platforms that are robust, scalable and technically impressive, and then watch adoption stall. Developers keep their old scripts or build unofficial tools around the official one. The platform team is frustrated that nobody appreciates what they built. Developers feel burdened by tools that make their work harder.

The chapter calls this the **platform paradox**. Its explanation is that a platform succeeds or fails less on what it technically provides than on what it is like to use.

This is the belief that a technically superior platform attracts users by itself. It misreads developers in three ways.

The costs go beyond wasted investment: lower productivity and morale, burnout, less experimentation, and unofficial tooling that adds debt and security risk.

## Key ideas

- The platform paradox and the “build it and they will come” fallacy
- What “broccoli” means in this book
- Three dimensions and seven pillars of developer experience
- How to cultivate it, and how to measure it

## What the lesson covers

- The big picture
- “Build it and they will come”
- What developer experience is
- Why it is a business matter
- Cultivating it: build with, not for
- Measuring it
- Names to recognise

## Claims and numbers

- One survey cited in the chapter found developers spend more than 15 hours a week on tasks other than writing application code.

## Terms

platform paradox, It ignores their workflow, The broccoli problem, broccoli, Feedback loops, Cognitive load, Flow state, Productivity, People, Innovation, Risk, champions, Broccoli Man, DevEx framework, HEART, Across the books

## Interview line

A platform is only worth what its adoption is worth, and adoption depends on how it feels to use. I look at three things: how fast and clear the feedback is, how much a developer has to hold in their head, and how often they’re interrupted. I’d build with the users, watching them work, then measure time to first deploy, first-attempt success, and delivery metrics for teams on the platform against teams off it.

## On AWS

Give the platform one API and let every interface sit on it: a Backstage portal or Service Catalog for discovery, the same actions available through the CLI, CDK constructs or Terraform modules, and tool definitions agents can call. Golden-path templates should arrive with a pipeline, IAM roles, alarms, dashboards and tracing already configured, so the first deploy takes minutes. Measure it: emit pipeline events through EventBridge to compute lead time, deployment frequency and failure rate per team, and track time from repository creation to first production deploy. Provide an escape hatch as a documented, supported extension point instead of leaving teams to fork the template.

## Takeaways

- Adoption depends on the experience of use more than on technical merit.
- Three dimensions: feedback loops, cognitive load, flow.
- Build with your users, give them a way out for special cases, and measure adopters against non-adopters.
