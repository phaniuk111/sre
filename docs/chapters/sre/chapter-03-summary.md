# SRE chapter 3: Trends in production: what the cloud changed

*Site Reliability Engineering, 2nd Edition. Course lesson: `#ch-3`. Read: full text, re-read in a third pass.*

## Summary

The cloud swapped physical constraints for financial and logical ones. Capacity planning becomes financial engineering (FinOps): pay for just-in-time elasticity around Black Friday instead of holding idle hardware all year, and trade the stability of long-term commitments against cheap but interruptible Spot.

- **Compute from location**: Orchestrators place workloads; VMs stop being pets
- **Storage from compute**: Warehouses and query engines over object storage
- **Network from hardware**: Defined by software and identity

Managed services push the abstraction boundary up, so you stop patching hypervisors and focus on failure modes unique to your business. Open standards (Kubernetes, OpenTelemetry) reduce lock-in.

Troubleshooting now involves **shared state**: the first question is "is it us or the provider?", so treat providers as partners, use account-specific health dashboards and integrated telemetry, and see their SLA as a floor.

Architecture moved from long-lived VM "pets" to workloads, with three decouplings: compute from location (orchestrators), storage from compute (warehouses over object storage), and networking defined by software and identity (eBPF-style kernel hooks).

## Key ideas

- why capacity planning became financial engineering
- the three decouplings behind modern architecture
- why RTO and RPO alone can’t describe reliability

## What the lesson covers

- The big picture
- How platforms evolved
- Details from the full chapter

## Claims and numbers

- They can't express gray failures like "30% slower for 10% of users", and they only start counting after a disaster.
- On-premises, you bought for the peak and the hardware sat idle 51 weeks a year.
- They can’t describe a gray failure such as “30% slower for 10% of users”.
- More than 3.2 quadrillion tokens a month by mid-2026, accelerator use up fifteen-fold in two years, and machine learning used to predict hardware failures and tune cooling.

## Terms

Compute from location, Storage from compute, Network from hardware, shared state, intent-based, About 2010 · Tickets, Colossus, Byte storage, digital sovereignty, autonomous optimisation, Platformisation, Compliance shifted left, AI at scale, Data ingestion, Training, Deployment

## On AWS

The AWS Health Dashboard is the shared-state tool; Savings Plans, Spot and on-demand are the FinOps levers; EKS/ECS/Lambda are the workload-centric compute; S3 + Athena/Redshift are storage-compute separation; Control Tower and Service Catalog are the self-service platform; ADOT is the open standard for telemetry.

## Takeaways

- The cloud swapped physical limits for financial and logical ones (FinOps).
- Treat providers as partners and their SLA as a floor, not a promise about your service.
- RTO and RPO see the world as up or down. SLOs capture the partial failures that are far more common.
