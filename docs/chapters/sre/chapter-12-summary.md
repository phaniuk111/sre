# SRE chapter 12: Safety engineering with STPA and CAST

*Site Reliability Engineering, 2nd Edition. Course lesson: `#ch-12`. Code: POC 03. Read: full text, two passes.*

## Summary

Some major outages happen without any single component failing, as when a large Maps data update for Japan broke search. The chain-of-events model ("the root cause was the bug") assumes that sequence means causation and stops at a simple story.

- **1 · Losses and hazards**: What must never happen, and the states that lead there
- **2 · Control structure**: Who controls what, and what feedback they get
- **3 · Unsafe control actions**: Missing, wrong, mistimed, or too long or short
- **4 · Causal scenarios**: Why a controller would do that

**STAMP** says accidents happen when the system's design fails to constrain its components' behaviour: missing tests, code too complex to review, global rollouts and aggressive deadlines are why a risky release looked reasonable.

**STPA** looks forward, and you can run it on a design doc. It has four steps:

Read the picture as four places to look for trouble: the control action can be wrong or late, the feedback can be missing or misleading, the controller’s mental model can be out of date, and the process can behave in a way nobody modelled.

## Key ideas

- why “no component failed” outages need a different model
- the four steps of STPA and the parts of a control loop
- how CAST analyses an incident without blame
- how to get a team to try it

## What the lesson covers

- The big picture
- The control loop, drawn
- Two ways to explain the same outage
- Why safety engineering
- Doing STPA well
- Maps in Japan
- CAST and misnamed cities
- Getting adoption

## Claims and numbers

- That is how the same incident produced 22 recommendations where the postmortem had 8.
- Google's diagrams usually have 5–10 boxes, roughly a tenth the size of a dataflow diagram, and drawing one together gives teams a shared language.
- The STPA took 2 engineers part-time for 5 weeks and covered more than 30 subsystems and over a dozen teams.
- It made 34 recommendations against the postmortem's 7.
- CAST took 5 people and 81 hours and produced 22 recommendations; the postmortem took 3 people and 16 hours and produced 8.

## Terms

STAMP, STPA, hazards, control structure, unsafe control actions, causal scenarios, CAST, The release includes it, Services crash, Adverse events, Controllers’ behaviour, Causal factors, Systemic factors, Why bother before launch, Census dataset arrives, Evaluated

## On AWS

Draw the control structure from your pipeline (CodePipeline → CodeDeploy → Lambda/ECS, with CloudWatch alarms as feedback). UCAs translate into requirements such as "rollback must work with only the on-call role" or "a canary with no data must not promote". See POC 03's worksheet.

## Takeaways

- Safety is an emergent property of the whole system. You can’t read it from one component.
- Model functional controllers, their process models and their feedback.
- Blame is the enemy of safety. Ask why the action made sense, then fix the system.
