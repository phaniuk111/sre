# Platform chapter 14: Efficiency: one optimisation, every team

*Platform Engineering at Google (early release). Course lesson: `#pe-4`. Code: POC 17. Read: full text, one pass; all figures seen.*

## Summary

When every team runs on the same foundations, two things become possible. You can see where resources go across the whole fleet. And when you improve a shared component, everyone gets faster at once. Seeing leads to improving, and improving pays for more seeing. The chapter calls it a virtuous cycle.

- **Common infrastructure**: Same scheduler, RPC layer and libraries
- **Fleet-wide observability**: A profiler on every machine
- **Central optimisation**: Fix the shared thing once
- **Savings**: Which fund more observability

The platform team prototypes an optimisation, canaries it on major workloads, evaluates it, and then turns it on for everyone. Teams pick it up at their next normal release and do nothing. This avoids the trap of building something and waiting for teams to discover it, and it keeps the decision with the people who understand the change.

Not every workload gets faster. The chapter is candid about how regressions are handled.

The judgement behind this: an imperceptible slowdown or a little opt-out work for one team can be better than not shipping a major win for hundreds.

## Key ideas

- Why a common platform turns performance work into leverage
- On by default, absorbed regressions and opt-outs
- Application productivity metrics: telling “busier” from “slower”
- Three lessons: take the long view, the platform is not fixed, build levers

## What the lesson covers

- The big picture
- Shifting optimisations down
- Connect efficiency to business value
- Three lessons

## Claims and numbers

- In 2015 the memory allocator accounted for about 8% of fleet usage, more than any single application.
- The problem: a service’s CPU use went up 20%.

## Terms

Common infrastructure, Fleet-wide observability, Central optimisation, Savings, The scheduler hides placement, The aggregate showed surprises, Profile-guided optimisation, made automatic, random on purpose, application productivity metric, Defaults make it practical, Outliers reveal bad metrics, Proxies and Goodhart, Take the long view

## Interview line

Efficiency at scale comes from leverage. If every team shares the same libraries and runtime, I can profile the whole fleet, find that some shared component is the biggest consumer, fix it once, and ship it on by default. I’d measure with useful work per unit of resource, because raw CPU can’t tell me whether a service got slower or just busier.

## On AWS

Start with visibility: Cost and Usage Reports with cost allocation tags, Compute Optimizer, and a continuous profiler across the fleet (CodeGuru Profiler or an open-source eBPF profiler). Build an application productivity metric in CloudWatch with metric math: a business counter from your service divided by vCPU-seconds from Container Insights. Shift down with shared base images, a common runtime and Graviton as the default, delivered through the golden-path pipeline so teams get improvements at their next deploy. For criticality, use Spot and scheduled scaling for work that can wait.

## Takeaways

- Shared foundations turn one optimisation into a fleet-wide saving.
- Ship on by default, absorb small regressions, and treat opt-outs as information.
- Measure useful work per unit of resource, or you can’t tell slower from busier.
