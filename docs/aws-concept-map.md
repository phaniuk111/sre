# SRE concepts → AWS (one-page cheat sheet)

| SRE concept | What it means | AWS building blocks |
|---|---|---|
| SLI / SLO / error budget | good/valid ratio; target; allowed unreliability | CloudWatch metric math, Application Signals SLOs, composite alarms |
| Burn-rate alerting | page on fast budget burn, ticket on slow | Composite alarm (long AND short window) |
| CUJ / synthetic probe | measure what users do, end to end | CloudWatch Synthetics, RUM (client side) |
| Observability signals | metrics, logs, traces, profiles | ADOT/OpenTelemetry, CloudWatch, X-Ray, Managed Prometheus/Grafana, CodeGuru Profiler |
| Statistical alerting | baselines, not static thresholds | CloudWatch Anomaly Detection, Lookout for Metrics-style custom models |
| Incident command (IMAG/ICS) | IC, Comms, Ops roles | Systems Manager Incident Manager, Chatbot, Health Dashboard for provider-side issues |
| Generic mitigations | rollback, drain, upsize, degrade, block | CodeDeploy rollback, Route 53 ARC zonal shift, Auto Scaling, AppConfig flags, WAF |
| Progressive rollout | small, gradual, supervised, reversible | CodeDeploy canary/linear, AppConfig deployment strategies, per-Region pipeline stages |
| Failure domains | limit blast radius | AZs, Regions, cells, accounts; static stability |
| Overload protection | shed by criticality, back off, throttle | API Gateway throttles/usage plans, SQS buffering, Lambda reserved concurrency, SDK adaptive retries |
| Fault injection / DiRT | prove resilience | AWS FIS, Resilience Hub, game days |
| Capacity planning | forecast demand, plan supply, N+1 | Predictive scaling, scheduled scaling, capacity reservations, Savings Plans, service quotas |
| Data integrity & recovery | RPO/RTO/RWO, 3-2-1, restore tests | AWS Backup (Vault Lock, cross-Region, restore testing), PITR, S3 versioning/Object Lock |
| Toil reduction | automate the repetitive | SSM Automation, EventBridge, Step Functions, Lambda |
| Platform & policy | golden paths, guardrails | Service Catalog, Proton/Backstage, Control Tower, SCPs, Config, cfn-guard |
| Shared state with provider | "is it you or me?" | AWS Health (account-specific events), Support/TAM, provider SLAs |
| FinOps | capacity as financial engineering | Cost Explorer, Budgets, Compute Optimizer, tagging |
| AI for SRE | agents with guardrails | Bedrock Agents, Amazon Q Developer ops investigations |
| SRE for AI | quality SLOs, accelerator capacity | Bedrock (provisioned throughput, guardrails, evaluations), SageMaker endpoints, Capacity Blocks |
