# SRE chapter 20: How SRE supports AI

*Site Reliability Engineering, 2nd Edition. Course lesson: `#ch-20`. Read: full text, two passes.*

## Summary

AI systems are layered (accelerators, a shared inference layer, models, applications and agents) and need clear control and data planes, careful accelerator management, observability and a clean artifact lifecycle (versions, deployment, rollback).

- **Availability**: Hardware, the training control plane, attestation.
- **Throughput**: ML goodput: the share of allocated time doing useful work.
- **Latency**: Time to first token, scheduling delay, data staleness.
- **Quality**: Is the answer right? The defining pillar for AI.

Agents are usually supported by the existing product SRE team. SLOs rest on four pillars: availability, throughput (training), latency (including time to first token) and **quality**, which is the defining one. Evaluation scores act as SLIs, alongside model-as-judge checks, data lineage and statistical drift detection.

Responses run on a spectrum from server error through "gave up" and low quality to high quality, so HTTP status codes aren't enough. Launch AI features with phased experiments, monitoring of both system and model quality, capacity plans, fast rollback to the previous model, and feedback loops.

Qualification covers new hardware generations (a continuous test matrix of workload, architecture and topology; accelerators become "SLO-eligible" only once proven) and every model submission (compatibility, performance and quality regressions across its lifecycle).

## Key ideas

- the four SLO pillars for AI systems, with quality as the new one
- how models and accelerators are qualified for production
- the six losses that explain idle accelerators
- power as a first-class constraint, and the new security risks

## What the lesson covers

- The big picture
- Three pictures from the chapter
- The stack and engagement
- Four SLO pillars
- Reliability is a spectrum
- Qualification
- The loss framework
- Power
- Security

## Claims and numbers

- Going from 30% to 35% costs far more power than going from 75% to 80%.So a half-idle fleet wastes the hardware and still pays most of the power bill.
- Monitor 7-day 95th-percentile occupancy against targets .
- The loop is the ordinary capacity loop from chapter 15; what changes is that supply takes months to arrive and can’t be bought on demand.
- Google's first ML SRE team started in 2009 for ad click prediction.
- Utilisation is measured as duty cycle (for example, P95 occupancy over seven days).
- Starting from 100%, six losses explain the gap:.
- Max utilisation : real-time serving may queue at around 50%, batch at around 90%.
- An ML machine draws roughly 3× a CPU machine, and a 1,000-machine job needs one grid, so its smallest useful footprint is about 3,000× larger.
- On AWS Bedrock (provisioned throughput, guardrails, model evaluation, cross-Region inference), SageMaker endpoints and inference components, EC2 Capacity Blocks for ML, CloudWatch metrics for TTFT and tokens per second.

## Terms

Availability, Throughput, Latency, Quality, utilisation losses, Power, Develop and version, Qualify automatically, Readiness gate, Progressive rollout, Serve and monitor, Runtime policy enforcement, Reasoning-based defences, Continuous assurance, Demand, Forecast

## On AWS

Bedrock (provisioned throughput, guardrails, model evaluation, cross-Region inference), SageMaker endpoints and inference components, EC2 Capacity Blocks for ML, CloudWatch metrics for TTFT and tokens per second.

## Takeaways

- A successful response with a wrong answer is still a failure, so quality needs an SLO.
- Qualify hardware, models and prompts continuously, and canary all three.
- Accelerators are scarce. Explain idle capacity with the six losses before buying more.
