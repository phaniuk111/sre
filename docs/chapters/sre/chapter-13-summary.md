# SRE chapter 13: Automation, tooling and toil

*Site Reliability Engineering, 2nd Edition. Course lesson: `#ch-13`. Code: POC 09. Read: full text, two passes.*

## Summary

You automate to save time in normal operations and in emergencies, and for consistency and scale. Automation moves through levels: none, then partial (where teams can get stuck), then full, which can be local, platform-wide, or best of all **inherent system behaviour** that removes the task altogether.

- **Detect and alert**: The automation only tells humans
- **Suggest**: It proposes an action; a human does it
- **Act and notify**: It acts and reports what it did

Capacity provisioning shows the progression: hardcoded replicas → autoscaling across locations → sizing by customer usage → continuously optimised placement, run by two layers of platform automation (minutes to hours, and days to months).

Bainbridge's **ironies of automation**: it creates new work (monitoring and fixing the automation), erodes operators' skills, and leaves humans the hardest cases. The pitfalls are dangerous automation without safety checks, deskilling, automation surprise, automating over a broken foundation (auto-restarting a memory leak), automating a moving target, and automating ambiguous decisions.

To decide, combine quantifiable costs and benefits (engineers underestimate maintenance) with strategic value, hidden risk costs, ambiguity and the human annoyance of the toil. Build up incrementally (the **automation snowball** of quick wins first earns trust), add extra safety to early versions, and don't stop at 90%. The Traffic Director and Pod story shows configuration sprawl turning into cascading failures.

## Key ideas

- the four reasons to automate and the levels of automation
- the ironies and pitfalls of automation
- how to decide what to automate, and how to do it incrementally
- what toil is, when it is acceptable, and what doesn’t fix it

## What the lesson covers

- The big picture
- Where automation fits in the incident loop
- Why and how far to automate
- Pitfalls and the ironies
- Deciding
- Incremental automation
- Traffic Director
- Toil

## Claims and numbers

- Build up incrementally (the automation snowball of quick wins first earns trust), add extra safety to early versions, and don't stop at 90%.
- For the pure time-saving case, the chapter points to the well-known xkcd chart (number 1205) that tells you how long you can spend automating a task before you lose more time than you save, counted over five years.
- The sum behind it is simple enough to do in an interview: time saved per run × runs per day × 1,825 days.
- The other traps are dangerous automation without rate limits, scope limits, do-no-harm checks and circuit breakers; deskilling (the 99% case); automation surprise; automating over a broken foundation; automating a moving target; and automating ambiguity.
- Don't stop at 90%, because half-automated processes confuse people and add cognitive load; give the automation readable logs and dashboards with linkable events.
- After an 18-month joint stabilisation effort with the platform team, the service moved to multi-tenancy.
- Keep engineering above 50% (for example, reduce toil from 50% to 30%).

## Terms

inherent system behaviour, Detect and alert, Suggest, Act and notify, ironies of automation, automation snowball, Toil, Detect, Triage, Mitigate, Resolve, Learn, Remediate, Across both books, inherent behaviour, relay

## On AWS

SSM Automation with `aws:approve` steps and rate controls; EventBridge to trigger it; Step Functions for multi-step workflows; Config auto-remediation. See POC 09.

## Takeaways

- Automate for emergencies, consistency and scale, not only to save time.
- Automation creates new work and erodes skills, so keep it observable, limited and reversible.
- Toil is defined by its properties. Fix whole classes of it, and keep engineering above 50%.
