# SRE chapter 18: Platform engineering in SRE

*Site Reliability Engineering, 2nd Edition. Course lesson: `#ch-18`. Code: POC 10. Read: full text, two passes.*

## Summary

A production platform is the organisation's abstraction layer over infrastructure (RPC, CI/CD, observability, orchestration, capacity, load balancing, storage). Designed well, it's a self-service product; left undesigned, it's a mess.

- **Golden path**: The easy, supported route
- **Hint**: A nudge in the editor
- **Warning**: Flagged, but allowed
- **Error**: Blocked, with a break-glass path

Building one involves policy decisions: who gets access, how many instances and where, whether you need permission to depend on something, chargeback, standards, control-plane access, reuse versus rebuild, and whether it should be hard to get things wrong or easy to experiment.

Google shifted from "bring me requirements" to **requirements plus curated solutions**, encoding reliability principles into the tools (for example, the approved deployment system has canary analysis, progressive rollout and SLO monitoring built in). Policies are like style guides, enforced by compliance checkers at different levels.

Useful lenses: the **garden** metaphor (direct versus indirect control); **Cynefin** (move production problems from chaotic and complex towards complicated and clear); cybernetics (Meadows's leverage points, Ashby's requisite variety, Bainbridge again).

## Key ideas

- what a platform is, and why curated solutions beat requirements alone
- golden paths, guardrails, exceptions and incentives
- shifting down, legibility, and handling brownfield systems

## What the lesson covers

- The big picture
- The effectiveness zone
- What a platform is
- Policy as a style guide for production
- Models to cite
- Choices, incentives and paths
- Exceptions and feedback
- Shift down, effectiveness zones, frameworks
- Legible risk and brownfield exemptions

## Claims and numbers

- “Shift down” means moving a practice from type 2, where every feature team has to know and do it, to type 3 or 4, where the platform does it.
- A platform moves accidental complexity towards clear, making the routine 90% easy so experts can focus on the hard 10%.

## Terms

Golden path, Hint, Warning, Error, requirements plus curated solutions, garden, Cynefin, golden paths, desire paths, Shift down, legible, Build horizon, Across the books, Systems thinking, Direct versus indirect control, Legibility

## On AWS

Service Catalog, Proton or Backstage for golden paths; Control Tower controls, SCPs and RCPs for guardrails; Config conformance packs and Resilience Hub for legibility; CDK constructs for shifting down; cfn-guard in CI. See POC 10.

## Takeaways

- A good platform makes the reliable way the easy way.
- Golden paths over mandates: change the game so the good outcome is the rational one.
- Block new violations, exempt old ones explicitly with an expiry, and make the remaining risk visible.
