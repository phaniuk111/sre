# SRE chapter 14: Testing for reliability

*Site Reliability Engineering, 2nd Edition. Course lesson: `#ch-14`. Code: POC 05. Read: full text, two passes.*

## Summary

Testing stands in for a perfect model of the world, and production is the only fully accurate environment, which is why testing in production keeps growing. Know the types: unit, integration, system, smoke, performance, regression, resilience, production tests (canaries above all), fuzzing, property-based, mutation, static analysis and agentic. Infrastructure for testing means version control, reproducible central runs and hermetic environments.

- **Versioned**: There is always a known version to roll back to.
- **Observable**: You can tell whether a change is live.
- **Independent**: Config can change, and soft-launch, separately from code.
- **Safe**: There is an explicit safe default for emergencies.

**Configuration is as dangerous as code.** The **VOIS** invariants: Versioned, Observable, Independent of code deploys, Safe with explicit safe defaults. Test config at three levels: syntax (cheap, and invaluable in an emergency), semantic and dynamic.

Watch for drift. **Canaries** send production traffic to a subset during an incubation period and run continuous statistical analysis; they are especially valuable for config. Even emergency rollouts need a fast tested path.

**DiRT** began as a yearly week-long exercise and became a continuous programme. It works top-down and bottom-up, it's framed as making systems better rather than compliance, and it's marketed internally. It found entangled systems, recovery plans that couldn't be carried out, and workflows that lived on one person's workstation.

## Key ideas

- why configuration needs the same testing discipline as code
- the VOIS properties and the layers of config tests
- what canaries, DiRT and fault injection each prove
- where formal methods and agent testing fit

## What the lesson covers

- The big picture
- The hierarchy of tests
- Philosophy
- Configuration is the sharpest edge
- Canaries and emergencies
- DiRT
- Client-focused change supervision
- Formal methods and agents

## Claims and numbers

- From a footnote in the chapter: begin at 0.1% of traffic and grow roughly ten-fold every 24 hours, moving across server locations as you go.
- At 0.1% a bad release hurts almost nobody, so move quickly.
- At 50% a bad release is a major outage, so bake longer.
- One more honest detail: the old claim that a bug costs 100 times more to fix in production is more nuanced than the slogan.
- Watch for performance creep: a run of small regressions took one service from 50 to 250 ms in a year.

## Terms

Versioned, Observable, Independent, Safe, VOIS, Canaries, DiRT, Client-focused change supervision, Fault injection, Formal methods, Agentic testing, Client-focused supervision, Syntax, Semantic, Dynamic, Canary

## On AWS

CodeDeploy canaries, AppConfig validators and deployment strategies, FIS, Synthetics, Distributed Load Testing on AWS, and CodeGuru Reviewer / Inspector for static analysis. See POC 05 and 06.

## Takeaways

- Testing measures how wrong your mental model is.
- Config must be versioned, observable, independent and safe, and checked in layers.
- A canary is an A/B comparison and the first integration test of production config with new code.
