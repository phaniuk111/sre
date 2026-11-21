# Platform chapter 19: Platform as a product: from good intentions to an operating model

*Platform Engineering at Google (early release). Course lesson: `#pe-8`. Code: POC 18. Read: full text, one pass; all figures seen.*

## Summary

The previous lesson said developer experience decides whether a platform succeeds. That is a goal. This lesson is the method: run the internal platform with the discipline of product management, as if it were something you sold.

The chapter says much of the friction Google Cloud sees in customers adopting platform engineering comes from running it as a project. Three pillars define the alternative.

The value proposition comes from the **job** a developer is trying to get done, which is rarely the feature they ask for. “I need a deploy button” is a request. “I need to get my change to production quickly and with confidence” is the job.

The chapter’s example: a developer asks for a dashboard of build logs. The job is “when my deployment fails, I need to find the cause quickly so I can fix it.” Seen that way, the better answer may be clearer error messages, a chat notification that links straight to the failing step, or detecting the failure before they notice.

## Key ideas

- Project thinking against product thinking, and the three pillars of the product model
- The product surface area, for humans and for AI agents
- What a platform product manager does, and the tools: jobs to be done, build-buy-partner, capability roadmaps
- The four lifecycle phases and the antipattern in each
- A three-view scorecard

## What the lesson covers

- The big picture
- Projects and products
- The product surface area
- The platform product manager
- The lifecycle
- A scorecard with three views

## Claims and numbers

- The platform team provides the paving, lighting and plumbing, meaning reliability, security and core APIs, and keeps the main roads that take 80% of people where they need to go.

## Terms

A defined customer, A clear value proposition, An indefinite lifecycle, Shape the vision, Be the customer’s voice, Translate in both directions, Prioritise, golden path, brownout

## Interview line

I run a platform as a product, not a project. That means named customer segments, a value proposition measured against whatever they use today, and a lifecycle that includes retirement. I find the job behind each feature request, validate it by doing the work by hand for a couple of teams, then pave it as a golden path and earn adoption. I report three views: whether developers use it, whether it is reliable and affordable, and whether teams on it deliver faster and safer.

## On AWS

A golden path on AWS is a template that produces a repository, a pipeline, IAM roles, alarms and dashboards in one step, published through Backstage or Service Catalog and built from shared CDK constructs or Terraform modules. Extension points are versioned constructs teams can compose, with Service Control Policies marking what can’t be changed. For the scorecard: adoption from tags or template usage, cost per service from Cost and Usage Reports with cost allocation tags, platform SLOs in CloudWatch, and delivery metrics from pipeline events. For deprecation, use CloudTrail and access logs to find remaining callers, then a scheduled brownout with a 4xx response that names the replacement.

## Takeaways

- A product has customers, a value proposition and a lifecycle. A project has a deadline.
- Find the job behind the request, and prove it by hand before automating.
- Golden path first, then extension points; retire old platforms on purpose.
- Score it from three views: user, system, business.
