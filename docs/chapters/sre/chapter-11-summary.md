# SRE chapter 11: Learning from incidents

*Site Reliability Engineering, 2nd Edition. Course lesson: `#ch-11`. Code: POC 03. Read: full text, two passes.*

## Summary

An outage is an unplanned investment, and the postmortem collects the return. Foundations: put learning first (timeline, impact, contributing causes, lessons), stay blameless, collaborate across teams, and have executives model the behaviour and give it visibility.

In practice: study the incident thoroughly to find the earliest point it could have been detected, ask open questions without judgment, don't let temporary fixes become permanent, give every action item an owner and close it out, and share widely (weekly outage digests, a company-wide newsletter).

What has changed in a decade: safety science and systems thinking (STPA and CAST), storytelling, analysis of communication logs and responders' mental models, an **independent postmortem lead** who wasn't in the response, accountability that keeps the people closest to the decisions involved in fixing them, customer-centric impact analysis, and **layered reviews** at peer, team, organisation and executive level.

The chapter also leans on safety science: Swiss cheese, Rasmussen, Safety-II, Cook, Woods and STAMP. Each gets a line in the section on safety-science models below.

## Key ideas

- what a good postmortem contains and who should write it
- the safety-science models interviewers expect you to know
- the Paris data centre outage, start to finish, and what it changed

## What the lesson covers

- The big picture
- Rasmussen’s boundaries, drawn
- What a postmortem must contain
- How the practice evolved
- Safety-science models to name-drop correctly
- Case study: Paris, April 2023

## Claims and numbers

- A cooling-pipe water leak in europe-west9 led to a battery-room fire, and the fire brigade ordered power off for one of the region's three buildings.
- 16:46 A cooling pipe starts leaking above one zone.
- 19:00 Next day: control plane restored across the region.
- Customers' complaints were nearly 12 hours of recovery after power returned, and slow, vague updates; one awkward phrase in an update became a media joke.
- In March 2025, a power loss in us-east5-c stayed local and took about 6 hours instead of more than 11.

## Terms

independent postmortem lead, layered reviews, Across the books, Blameless postmortem, Restorative accountability, Swiss cheese (Reason), Rasmussen, Hollnagel's Safety-I vs Safety-II, Cook, Woods, decompensation, Leveson's STAMP, product-level incident commanders, On AWS

## On AWS

Incident Manager's post-incident analysis with custom templates (use the CAST template in POC 03), action items tracked through OpsCenter or Jira, and Correction of Error (CoE), Amazon's own postmortem format with its "5 whys", which is worth comparing with CAST in an interview.

## Takeaways

- An independent lead, several contributing factors, and what went right as well as what went wrong.
- Know one line each on Swiss cheese, Rasmussen, Safety-II, Cook, Woods and STAMP.
- Paris led to product-level incident commanders and auto-paged comms leads, and the next similar outage took about half the time.
