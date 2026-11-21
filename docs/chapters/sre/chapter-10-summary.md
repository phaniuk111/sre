# SRE chapter 10: Incident management and on-call

*Site Reliability Engineering, 2nd Edition. Course lesson: `#ch-10`. Code: POC 03. Read: full text, two passes.*

## Summary

Define your terms. An **incident** means users are having a bad time, important properties are degraded, or an outage is happening or imminent; an **outage** means a service or critical feature can't do its job. Anyone may declare an incident or escalate it, and false positives get relabelled later, which keeps politics out. On-call is a mechanism for coordinating urgent work; paging a whole team triggers the bystander effect.

- **Incident Commander**: Holds every role until they delegate it. Directs, and in big incidents takes no hands-on tasks.
- **Communications Lead**: Keeps stakeholders and customers informed on a fixed cadence. May split into internal and external.
- **Operations Lead**: Runs the hands-on response: investigating and applying mitigations.

**Incident response teams** coordinate incidents that span many teams. Large organisations run a global IRT plus product-area IRTs with clear escalation triggers and one common command framework; small ones keep a volunteer pool with "inversion of authority" and avoid *incident theatre* (as large as necessary, as small as possible). Watch for coordination overhead, handoffs, late engagement and skill atrophy.

**AI in incident response:** start with detection and triage (the worst case is over-escalation), summaries, dynamic dashboards and hypotheses. Allow production changes only with guardrails, where each change is reversible and atomic (action, validation and automatic rollback in one audited transaction).

## Key ideas

- the IMAG roles and how an incident moves through its lifecycle
- why you mitigate before you understand, and the five generic mitigations
- how to design on-call that people can sustain
- what to measure instead of MTTR

## What the lesson covers

- The big picture
- Classify before you respond
- On-call design
- IMAG and IRTs
- Triage and mitigation
- Coordination costs
- AI in incidents and Etsy's model

## Claims and numbers

- Coverage that matches users: business hours is “on duty”, daylight across two sites gives about 21 hours, and follow-the-sun gives 24×7.
- Response time: three minutes or less needs two people; 30 minutes allows normal life.
- Schedule options include business hours, daytime (6am–8pm), a daylight span across sites of about 21 hours, and 24-hour coverage via follow-the-sun or compensatory time.
- Humans are poor at passive monitoring beyond about 30 minutes.

## Terms

incident, outage, Incident Commander, Communications Lead, Operations Lead, Rotation design, Load, Coverage that matches users, Response time, Customer constraints, Labour law, Incident response teams, The incident lifecycle, Detect, Triage, Investigate

## On AWS

Incident Manager (response plans, contacts, escalation plans, chat channels, timelines, post-incident analysis), AWS Chatbot, SSM Automation runbooks, AWS Health for provider-side events. See POC 03.

## Takeaways

- Clear roles first. The Incident Commander directs and delegates.
- Mitigate before you understand: drain, roll back, upsize, degrade or block.
- Risk tolerance for a mitigation scales with impact, and a reasonable mitigation that fails is never blameworthy.
