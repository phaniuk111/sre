# SRE chapter 22: SRE in diverse environments

*Site Reliability Engineering, 2nd Edition. Course lesson: `#ch-22`. Read: full text, two passes.*

## Summary

Most SRE doesn't look like Google. A **solo SRE** focuses on keeping the service running and making developers self-sufficient, and may start at around 80% toil. Priorities: P0 stop the bleeding; P1 visibility (metrics, symptom-based alerts, logs); P2 automate the scariest task; P3 developer self-service.

- **P0 · Stop the bleeding**: Fix the outage that keeps repeating
- **P1 · Visibility**: Metrics, symptom alerts, structured logs
- **P2 · Automate the scariest task**: Usually deploys. Rollback first
- **P3 · Self-service**: Tools and docs so developers don’t need you

In the first 90 days, answer four questions: is it down, is it slow, is it broken, is it driving users away? Use one lightweight toolset, write playbooks for the five most recent outages, share on-call with developers, and make sure every change gets reviewed by at least one other person.

In **hybrid and legacy** estates, sort out responders' access and authority before incidents (formal break-glass), protect the time to act on postmortems, and wrap closed third-party systems in an anticorruption layer.

Use generic mitigations, adopt in stages, limit scope, set goals that fit each context, run drills for rigid systems, standardise the tooling that manages what you can't change, and keep humans in the loop where regulation demands it.

## Key ideas

- what to do first as the only SRE at a company
- how to apply SRE with legacy systems, silos and regulation
- lessons from a startup, a bank, a lender and Waymo
- how SRE skills carry over to security and privacy

## What the lesson covers

- The big picture
- Solo SRE
- Hybrid and legacy
- Case studies
- Waymo: crises, not just outages
- Security and privacy

## Claims and numbers

- A solo SRE focuses on keeping the service running and making developers self-sufficient, and may start at around 80% toil.
- You're the firefighter, the builder and the evangelist, often starting at 80% toil.
- P1, visibility : business and system metrics, symptom alerts switched on at the start of the day (never at home time), and structured JSON logs.
- Six months later, downtime across critical journeys was down about 60% and a major feature shipped 60 days early.
- It now has about a 7:1 developer-to-SRE ratio, and developers spend about 5% of their time on ops, down from nearly half.
- A central team offered issue-flow advice, 90-day engagements, one to three designated SREs at 50–75% for critical services, and a training rotation, then ran an eight-week enablement programme.

## Terms

solo SRE, P1 · Visibility, P3 · Self-service, hybrid and legacy, P0, stop the bleeding, P1, visibility, P3, developer self-service, anticorruption layer, B2B SaaS, Bank, Mortgage lender, weaponised blamelessness, incident coordinator, incident scribe, CrowdStrike, Log4j

## Takeaways

- Alone, prioritise ruthlessly: stop the bleeding, see, make deploys safe, enable developers.
- With closed or legacy systems, stabilise what surrounds them and standardise the layer above.
- Adapt the principles to your constraints. Don’t try to copy Google.
