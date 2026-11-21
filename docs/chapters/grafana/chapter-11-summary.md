# Grafana chapter 11: Architecting an observability platform

*Observability with Grafana (Rob Chapman and Peter Holmes, Packt, 2024). Course lesson: `#g-11`. Code: POC 28 · 7. Read: full text, one pass; all figures seen.*

## Summary

The most undervalued step is articulating what the organisation is trying to solve, with leadership: customer-affecting incidents (a compliance, operational and reputational risk), visibility of KPIs, how customers use the product, and the cost to serve them (COGS and OPEX). The answers decide what data you need.

Observability systems are data systems, and their data is most valuable when it joins up with the rest of the organisation. Find whoever owns the organisation’s data model. The author’s cautionary tale: months spent arguing whether `tenantID` and `customerID` were the same thing, then months of rework in two systems and the logging platform, all avoidable with an owner and early requirements.

Translate external requirements into an observability requirements document, in MoSCoW form (must, should, could, won’t). Finance needing cost centres, for example, could be met by putting it on every signal, by requiring an `organization.costcenter` label on every service, or by a service-to-cost-centre lookup table. Pick one and write it down.

Libraries are well tested; your organisation-specific fields, like customer ID, are not, and executives may make decisions on them. Test them like any other output; the book recommends Martin Fowler’s article on domain-oriented observability.

## Key ideas

- Starting from the problem, and agreeing a data architecture with the organisation
- Which signal suits which data, and testing organisation-specific fields
- Data production standards and collection patterns: agentless, agent, gateway, Kubernetes
- Deployment modes for Loki, Mimir and Tempo, and planning for failure
- Proofs of concept, RBAC, and sharing telemetry with SIEM and BI

## What the lesson covers

- Start with the problem
- Data architecture
- System architecture
- Proving a design
- Access
- Other consumers

## Terms

unindexed, cluster agent, Across the books, Collector topology

## Interview line

I start an observability platform from the business problems and the organisation’s data model, decide which signal carries which field, and publish a production standard: OpenTelemetry SDKs, logs to stdout, metrics on a Prometheus endpoint and OTLP, traces over OTLP. Collection uses node agents, a gateway and a single cluster agent on Kubernetes, with buffers sized from the outage I need to survive; storage runs in microservices or simple scalable mode, or with a vendor; access is least privilege by folder and team.

## On AWS

A typical AWS reference: ADOT node agents and a gateway on EKS; metrics to AMP, traces to X-Ray or Tempo, logs to CloudWatch Logs or Loki on S3; Amazon Managed Grafana with IAM Identity Center groups mapped to Grafana teams and folders; cost allocation through EKS pod labels and AWS cost allocation tags; security logs forked to Security Lake or a SIEM in the collector; business aggregates exported from recording rules to S3 for Athena or QuickSight. Separate AMP workspaces or AMG data sources for load-test and CI environments.

## Takeaways

- Start from the business problem and the organisation’s data model.
- Put each field in the signal that suits it; test your organisation-specific fields.
- Agent, gateway and a single cluster agent; buffers sized for failure; least-privilege access.
