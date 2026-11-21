# SRE chapter 2: The value of reliability

*Site Reliability Engineering, 2nd Edition. Course lesson: `#ch-2`. Read: full text, re-read in a third pass.*

## Summary

Present SRE as an investment with a return, not as a cost centre. The headline mechanism is **sublinear scaling**: by automating and standardising, operating costs grow more slowly than the service does. Traditional ops teams are rewarded for stability and so resist change. SRE uses the error budget so that stability and velocity are traded deliberately and both sides share the goal.

- **Customers**: Reliability is the feature every other feature depends on. Not 100%, though: that is always the wrong target.
- **The CFO**: Software leverage. Code runs again and again at almost no extra cost, and shared platforms spread the gain.
- **Product teams**: Objective targets and less cognitive load.
- **The SRE team**: Protection from burnout, including the right to hand a pager back.

Different stakeholders get different value. Customers get reliability as the feature everything else depends on (but not 100%, which is always the wrong target). The CFO gets software leverage: code runs again and again at almost no extra cost, and shared platforms like one global load balancer spread the gains.

Product teams get objective targets and less cognitive load. The SRE team gets protection from burnout; at Google, SRE can hand the pager back to a team whose service keeps missing its SLO.

The cost of unreliability is more than lost sales. There's churn, the opportunity cost of engineers firefighting, rising toil, slower velocity, expensive retrofits, SLA penalties, and a management fan-out of roughly 100 to 1000 engineer-hours per hour of major downtime once you count reviews, comms and remediation.

## Key ideas

- how to present SRE as an investment with a return
- what each stakeholder gets from it
- the full cost of unreliability, beyond lost sales

## What the lesson covers

- The big picture
- One hour of downtime, counted properly
- Details from the full chapter

## Claims and numbers

- Not 100%, though: that is always the wrong target.
- Customers get reliability as the feature everything else depends on (but not 100%, which is always the wrong target).
- The chapter’s most quotable table argues that a major outage costs 100 to 1,000 times its length in engineering time.
- The same chapter has a simple worked example for an internal system: a finance outage that idles 400 people for two days at $325 a day is $260,000 before anyone counts the knock-on effects.
- A number worth remembering Google’s research found that 53% of visitors give up on a task when a page takes more than three seconds to load.
- A sidebar describes a SaaS company growing revenue 200% a year while putting off basic production hygiene.
- Uptime went from 99.84% to 99.999%, which is the difference between about an hour of downtime a month and a few seconds.

## Terms

sublinear scaling, Customers, The CFO, Product teams, The SRE team, atrophy, A number worth remembering, Across the books, Error budget, The nines, Mature organisation

## Interview line

"For a startup I'd start with the cheap, high-return practices: automated tests, a CI/CD pipeline, symptom-based alerting, a simple incident process with clear roles and blameless reviews, and lightweight design reviews that look at failure domains, rate limits, rollbacks and data recovery. In a mature organisation, SLOs turn into the tool for deciding where reliability investment goes, and centralised platforms give everyone the same reliable building blocks."

## On AWS

Back the business case with SLA credits from your own customer contracts, AWS Cost Explorer for spend, and the time-to-mitigate trend from Incident Manager. A worked example from the book: 400 finance staff idle for two days at $325 a day is $260,000 in productivity alone.

## Takeaways

- The headline benefit is sublinear scaling: cost grows more slowly than the service.
- The error budget turns stability versus velocity into a deliberate, shared trade.
- Unreliability costs far more than lost sales, and systems atrophy without investment.
