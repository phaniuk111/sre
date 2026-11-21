# SRE chapter 21: How AI supports SRE

*Site Reliability Engineering, 2nd Edition. Course lesson: `#ch-21`. Code: POC 11. Read: full text, two passes.*

## Summary

Scripts are brittle and AI is probabilistic, so adoption is organised around the production-health hierarchy. Foundations first: blamelessness becomes a prerequisite once automation is probabilistic. Humans aren't replaced; the Jevons paradox suggests demand for production expertise will grow.

The safety architecture rests on **transparency**, **contextual awareness** and **progressive authorization**, starting with least privilege and dry runs, keeping absolute human control, and following the **reversible operations** rule: no action unless the agent knows how to undo it.

In practice: Detectr clusters user feedback from social media, support and forums into outage reports; agents summarise incident chatter and build dashboards from similar past incidents, playbooks and the alert's intent. **Mitigation is selection** among known safe actions, which AI handles well; root-cause analysis is deep investigation.

AI also drafts postmortems, mines past incidents, clusters toil, tunes itself, verifies resilience tests (did traffic in the drained cluster really drop to zero?), and supports design and launch reviews. **Autonomy levels**, across monitor, investigate, approve, actuate and self-direct: L0 manual, L1 assisted, L2 partial (a human approves), L3 high (well-defined scenarios), L4 full.

## Key ideas

- the safety architecture for agents with production access
- how AI finds outages that metrics miss
- the five levels of autonomy, with a real example at each
- where the real value lies beyond toil reduction

## What the lesson covers

- The big picture
- The safety loop for an agent with production access
- Framing
- Safety architecture
- Situational awareness: Detectr
- Preparedness and infrastructure
- Force multiplier and autonomy

## Claims and numbers

- Probabilistic tools at production scale bring probabilistic failure at scale: a 1% error rate spread across all of production is a catastrophe.
- Give agents SLOs too: proposal latency, a helpfulness SLO (say 95% of suggestions accepted) and a safety budget that pauses autonomy when spent.
- At a 0.1% error rate, a customer making 1,000 calls per operation sees nearly every operation fail, and a 0.1% average might really be 1% of customers failing 10% of the time.
- It became core infrastructure in early 2026 and saved thousands of hours of customer impact.
- Toil reduction has a ceiling: with toil at 25%, even processing it 5× faster barely moves overall productivity.

## Terms

transparency, contextual awareness, progressive authorization, reversible operations, Mitigation is selection, Autonomy levels, reason, Progressive authorisation, transaction, Plan, Read server errors, Fetch job details, Check for anomalies, Is an incident open?, Find the owner, Escalate

## On AWS

Amazon Q Developer operational investigations, Bedrock Agents with read-only IAM to start, SSM Automation approvals for L2, ARC zonal shift as a reversible action. See POC 11.

## Takeaways

- Trust is earned: read-only, then proposing, then acting on narrow, reversible tasks.
- An agent may only do what it knows how to undo, as one validated transaction.
- Not every system should reach full autonomy. Match the level to the risk.
