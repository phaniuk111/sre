# SRE chapter 8: SLOs, error budgets and burn rate

*Site Reliability Engineering, 2nd Edition. Course lesson: `#ch-8`. Code: POC 01. Read: full text, first pass.*

## Summary

- **SLI**: An indicator: good events ÷ valid events
- **SLO**: An objective: a target for that ratio over a window
- **Error budget**: 1 − SLO: the failure you are allowed
- **Burn rate**: How fast you spend it. At 1× it lasts exactly the window

An **SLA** is different. It is the agreement about what happens, usually money, when a target is missed, and it is normally looser than the internal SLO.

A **critical user journey** (CUJ) is a task the user cares about, such as logging in or checking out. It usually spans several services, which is why SLOs written only by backend teams miss things.

The sum for 99.9% is 0.001 × 30 days × 1,440 minutes a day = 43.2 minutes. Be ready to do it on a whiteboard.

Alert on how fast the budget is burning, not on a raw error threshold. A long window proves the burn is significant. A short window proves it is still happening, so the page clears soon after you recover.

## Key ideas

- the vocabulary: SLI, SLO, SLA, error budget, burn rate, CUJ
- the numbers to know cold, and how to derive them on a whiteboard
- how to alert on burn rate, including for low-traffic services
- what the second edition adds, and where SLOs fall short

## What the lesson covers

- Four terms, each built on the last
- The numbers to know cold
- Choosing your first SLO
- Alerting on burn rate
- What the second edition adds
- Where SLOs fall short
- The error budget policy is a ramp, not a cliff

## Claims and numbers

- The sum for 99.9% is 0.001 × 30 days × 1,440 minutes a day = 43.2 minutes.
- 99% is relaxed, 99.9% is the common choice and 99.99% is demanding.
- Where 14.4 comes from: 2% of a 30-day budget in one hour is 0.02 × 720 hours ÷ 1 hour = 14.4 times the sustainable rate.
- At that pace the whole budget is gone in about 50 hours.
- Low traffic needs statistics With 200 requests in an hour, a handful of errors proves nothing.
- For a 14.4% threshold at 99% confidence, that takes 173 failures in 1,000 requests, 42 in 200, or 24 in 100.
- In one case a single 99.99% probe stayed green while small combinations of protocol and destination were completely broken.
- An aggregate burn of 10× could be one customer at 100× and nine at zero.
- Use bad minutes : a minute is bad if its error rate is above, say, 6% when the noise is 5%.

## Terms

Error budget, Burn rate, critical user journey, Pick an availability target, Pick a goodness threshold, Keep it small, Low traffic needs statistics, Adoption pitfalls, Critical user journeys, Per-customer SLOs, Implicit SLOs, Client-side SLOs, bad minutes, Tooling, Labels, Failure concentration

## On AWS

CloudWatch metric math gives you the SLI, composite alarms (long AND short window) give you burn-rate paging, and CloudWatch Application Signals offers native SLO objects. Use Synthetics canaries for CUJ probes and CloudWatch RUM for client-side SLIs. See POC 01 and 02.

## Takeaways

- An SLI is good events over valid events. The SLO is the target, and the error budget is what’s left over.
- 99.9% over 30 days is 43.2 minutes. Page at 14.4× burn, confirmed by a short window.
- The target is a business decision made by a cross-functional group, written down with an error budget policy.
