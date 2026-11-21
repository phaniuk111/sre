# Platform chapter 16: Reliability: the platform turns SRE into a default

*Platform Engineering at Google (early release). Course lesson: `#pe-6`. Code: POC 16. Read: full text, one pass; all figures seen.*

## Summary

Reliability means meeting what users expect, consistently and correctly. Uptime is one part of it. A system can be up and too slow to use, or up and returning wrong data. The chapter lists six dimensions: availability, latency, correctness, freshness, durability and throughput. For AI services, correctness becomes probabilistic.

The central sentence of the chapter is this one, paraphrased: **SRE provides the blueprint for reliability, and platform engineering provides the machinery that produces reliable services at scale.** Asking every team to learn and apply SRE practices on their own doesn’t scale. The platform’s job is to capture those practices as code and APIs, so a team inherits them by using the standard path.

Feature teams are rewarded for shipping. That is a local measure. When a team skips resilience work to ship sooner, the cost doesn’t disappear. It moves to the organisation as cascading failures, firefighting and cross-team incident response. Economists call that an externality.

The chapter is kind about motive: teams rarely decide to trade reliability for speed. They assume everything will be fine. It names the result bluntly, though. Reliability becomes an **unfunded local mandate**, and everyone suffers.

## Key ideas

- Why reliability is a global cost that local teams underfund
- How a platform encodes the four SRE principles, including risk profiles
- What each extra nine requires, and why it can’t be funded team by team
- What to shift down: blast radius and the cost of a mistake
- Why the platform itself needs stricter SLOs than anything running on it

## What the lesson covers

- The big picture
- The economics: local savings, global costs
- Four SRE principles, encoded
- Getting the nines
- What belongs in the platform
- Six capabilities to shift down
- The reliability of the platform itself
- What the organisation gets

## Terms

unfunded local mandate, risk profile, Blast radius, Complexity, Cost of a mistake, Break-glass, done properly, joint cognitive system, bad change, Strict, published SLOs, Defence in depth, Conservative rollouts, Disaster practice, Sublinear scale, Lower cognitive load, Fast diagnosis, Fleet-wide remediation

## Interview line

SRE tells you what reliable looks like; the platform is how you get it for every team without each one learning it the hard way. I’d put into the platform anything with a wide blast radius or a catastrophic failure mode: safe rollouts with automated canary analysis, retry budgets, multi-zone placement, capacity, standard telemetry and SLO tracking. I’d tie deployment strictness to each service’s risk profile. And I’d hold the platform itself to tighter SLOs than its tenants, because when it fails everyone fails.

## On AWS

Risk profiles map well to CodeDeploy deployment configurations and AppConfig deployment strategies: pick linear or canary steps and bake times by service tier, with CloudWatch alarms for automatic rollback. Abstract infrastructure with EKS or ECS spread across at least three Availability Zones through topology constraints the golden path sets for you. Capacity: predictive and target-tracking Auto Scaling, Karpenter on EKS. Unsafe operations: Service Control Policies, Route 53 ARC safety rules that refuse to turn off too many cells at once, deletion protection and AWS Backup with Vault Lock. Observability: Application Signals for golden signals and SLOs on every service, X-Ray or OpenTelemetry tracing injected by the platform. Break-glass: a dedicated emergency role whose use is logged by CloudTrail and raises an EventBridge alert. For the platform itself, publish SLOs for pipeline success, deploy latency and telemetry lag, and test them with Fault Injection Service.

## Takeaways

- SRE is the blueprint; the platform is how every team gets it by default.
- Shift down what has a wide blast radius, needs rare expertise, or fails catastrophically.
- Each nine costs far more than the last, so only a shared platform can fund the top ones.
- The platform needs stricter SLOs than anything it hosts.
