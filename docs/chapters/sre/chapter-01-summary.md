# SRE chapter 1: What SRE is, and the model behind it

*Site Reliability Engineering, 2nd Edition. Course lesson: `#ch-1`. Read: full text, re-read in a third pass.*

## Summary

The name breaks into three parts. *Site* is the reason SRE exists: users must be able to use the product, so the work ties back to business impact. *Reliability* is the single thing SREs own, and that narrow focus lets them build expertise generalists can't.

- **1 · Sociotechnical foundations**: Culture, people, how teams work
- **2 · Situational awareness**: SLOs and observability
- **3 · Continuous preparedness**: Incidents, learning, safety analysis
- **4 · Infrastructure design**: Automation, testing, capacity, data
- **5 · Resilient products**: Reliability designed in
- **6 · Emergent reliability**: Reliable by default

*Engineering* is the method: you solve operational problems with software and repeatable processes rather than heroics. A quick test for any project is whether it helps the business, improves reliability, and uses an engineering approach.

The book replaces the old Dickerson pyramid (monitoring, incident response, postmortems, testing, capacity, development, product) with a **hierarchy of production health**: sociotechnical foundations, then situational awareness, continuous preparedness, infrastructure design, resilient products and finally **emergent reliability**, where the platform makes systems reliable by default.

The old pyramid was mostly reactive and left culture and data integrity implicit. You grow the new one wider and taller at the same time; don't build the top before the base can hold it.

## Key ideas

- what each word in “Site Reliability Engineering” commits you to
- the hierarchy of production health and why it replaced the old pyramid
- a crisp answer to “how is SRE different from DevOps?”

## What the lesson covers

- The big picture
- Why the old pyramid was replaced
- Details from the full chapter

## Terms

hierarchy of production health, emergent reliability, The inverted pyramid, Across both books, Toil, Objective understanding, Automation, Dev and ops integrated, Length, Frequency, Scope

## Interview line

"SRE treats operations as a software problem. That gives you three things: you measure production health objectively with SLOs and observability, you automate for efficiency and for consistency, and you share a language with developers so feedback from production flows back into design. Toil has a ceiling of 50% of an SRE's time. That's a limit, not a goal, and good teams sit far below it."

## On AWS

The hierarchy maps neatly onto the Well-Architected Reliability pillar and its operational-excellence practices. Situational awareness means CloudWatch and X-Ray; preparedness means Incident Manager and game days; infrastructure design means multi-AZ, CodeDeploy, AWS Backup and FIS; emergent reliability means golden paths through Service Catalog or Control Tower guardrails.

## Takeaways

- SRE treats operations as a software problem, with reliability as the one thing it owns.
- The hierarchy of production health starts with culture and ends with platforms that make systems reliable by default.
- The 50% toil ceiling is a limit, not a target. Good teams sit far below it.
