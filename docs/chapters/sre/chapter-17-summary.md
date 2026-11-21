# SRE chapter 17: Designing for resilience

*Site Reliability Engineering, 2nd Edition. Course lesson: `#ch-17`. Code: POC 04. Read: full text, two passes.*

## Summary

Resilience is keeping adequate service quality during failures, including ones nobody anticipated, or degrading clearly when you can't. Handle high-probability failures cheaply, prioritise by severity, and decide deliberately about rare but high-impact ones (some aren't worth the cost).

- **Normal**: Rich tools, many dependencies, used by everyone.
- **Emergency**: Low-dependency fallbacks with the same interfaces. Most responders, little training. Invest here first.
- **Disaster**: Zero-dependency command-line tools and direct access, for small trained teams.

Responses can be manual, automated or **architectural**, and architectural is best because it removes the need to react at all.

Google's principles cover risk management, change management, dependency management, failure domains, overload management, input validation, data resilience, qualification and emergency mode, and they're enforced through common platforms, with exceptions sought explicitly and remaining risks escalated.

**Change management:** small, progressive changes across failure domains, including data and config; one change at a time; supervision; and safe mitigations: **drain, roll back, upsize, degrade, block** (a query of death). Mitigations obey the same rules and must be tested.

## Key ideas

- how reliability and resilience differ, and how to prioritise rare risks
- the rules for safe change, dependencies and failure domains
- how to survive overload and bad input
- incident modes and the response journeys to practise

## What the lesson covers

- The big picture
- Two pictures from the chapter
- Reliability vs resilience
- Enforce through technology
- Change management details
- Dependencies
- Failure domains and alignment
- Overload and input
- Data resilience and qualification
- Incident modes and response journeys

## Claims and numbers

- Failure domains and N+1 : Survive the loss of a zone or region; say which domain you mean.
- Alignment matters: two regions with two zones each lose 25% of capacity per zone, while one zone per region without anti-affinity loses 50%.
- Degrade to roughly 80% quality for 20% of the compute.
- On AWS Multi-AZ and cells; Route 53 ARC zonal shift and zonal autoshift; static stability; SDK adaptive retries; API Gateway and WAF throttles; SQS buffering; AppConfig flags; Incident Manager replicated across Regions; break-glass IAM roles.

## Terms

Emergency, Disaster, architectural, Change management, Dependencies, Failure domains, Overload, shed load, degrade gracefully, exponential backoff with jitter, adaptive throttling, Input validation, Data resilience, Qualification, Emergency mode, Risk register

## On AWS

Multi-AZ and cells; Route 53 ARC zonal shift and zonal autoshift; static stability; SDK adaptive retries; API Gateway and WAF throttles; SQS buffering; AppConfig flags; Incident Manager replicated across Regions; break-glass IAM roles. See POC 04.

## Takeaways

- A complex plan might work. Resilience has to work every time, so enforce it through the platform.
- Sized for X and receiving 10X, serve about X and recover without humans.
- Practise the emergency mode: fallbacks for comms, access, docs and reaching people.
