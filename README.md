# SRE 2nd Edition → AWS: hands-on POCs for interview prep

Proofs of concept that turn the ideas in *Site Reliability Engineering, 2nd Edition* (O'Reilly, 2026) into **working code and Terraform on AWS**. Each POC has a README with a concept-to-AWS map and interview talking points, Python you can run and test locally, and Terraform for the AWS side.

> These are my own implementations and explanations, written as study material. They don't reproduce the book. Buy or borrow it for the full argument and case studies.

## Map: chapter → POC → AWS services
| Book part / chapter | POC | AWS services used |
|---|---|---|
| III · 8 SLOs, App. E composing SLOs | [`poc-01-slo-error-budget`](poc-01-slo-error-budget) error budgets, multi-window burn-rate alerts, Wilson-interval low-traffic alerting, SLO composition, bad-minute SLOs | CloudWatch metric math, composite alarms, dashboards, SNS (Application Signals SLOs as alternative) |
| III · 9 Observability, App. F/G | [`poc-02-observability-otel`](poc-02-observability-otel) OTel instrumentation with CUJ baggage, ADOT pipeline, CUJ synthetic probe, anomaly detection, cohort z-score regression detector, failure-concentration finder | ADOT, CloudWatch (EMF, Logs, Anomaly Detection, Synthetics), X-Ray |
| III · 10–12 Incidents, learning, STPA/CAST | [`poc-03-incident-management`](poc-03-incident-management) IMAG playbook, CAST postmortem template, STPA worksheet, incident metrics beyond MTTR | Systems Manager Incident Manager (contacts, escalation, response plans), SSM Automation |
| V · 17 Designing for resilience | [`poc-04-resilience-patterns`](poc-04-resilience-patterns) jittered backoff, retry budgets, adaptive throttling, circuit breaker, criticality load shedding, hedging + a cascading-failure simulator | SDK retry modes, API Gateway throttling, WAF, Route 53 ARC |
| IV · 14 Testing, V · 17 change mgmt | [`poc-05-progressive-delivery`](poc-05-progressive-delivery) canary vs control statistics, Lambda canary with alarm rollback, feature flags with gradual rollout & safe defaults | Lambda versions/aliases, CodeDeploy, AppConfig |
| IV · 14 DiRT / fault injection | [`poc-06-chaos-fis`](poc-06-chaos-fis) AZ-loss and dependency-latency experiments with SLO stop conditions, DiRT test catalog, evidence verifier | AWS FIS, CloudWatch |
| IV · 15 Capacity planning | [`poc-07-capacity-planning`](poc-07-capacity-planning) forecasting with backtested uncertainty, N+1 supply plans, peak-of-sums pooling | EC2 Auto Scaling (target tracking, predictive, scheduled), Spot, capacity reservations |
| IV · 16 Data management | [`poc-08-data-resilience`](poc-08-data-resilience) data tiers with RPO/RTO/RWO, backup SLO report | AWS Backup (plans, cross-Region copy, Vault Lock, restore testing), DynamoDB PITR, S3 Object Lock |
| IV · 13 Automation & toil | [`poc-09-toil-automation`](poc-09-toil-automation) toil measurement & prioritisation, approval-gated generic mitigation runbook | SSM Automation, Route 53 ARC zonal shift |
| V · 18 Platform engineering | [`poc-10-platform-policy`](poc-10-platform-policy) policy-as-code with exemptions, CloudFormation Guard rules | Service Catalog, Config, Control Tower, SCPs, cfn-guard |
| VI · 19–23 AI & SRE | [`poc-11-ai-ops-guardrails`](poc-11-ai-ops-guardrails) autonomy levels L0–L4, reversible atomic actions, progressive authorization | Bedrock / Q Developer agents, ARC, Lambda |
| I–II · 1–7 Context, culture, org | [`docs/`](docs) concept map, culture/org cheat sheet, interview question bank | n/a |

## Study guide
An interactive tutor for every chapter (explanations, AWS mapping, labs, flashcards, quiz, interview drills) is published as a private Claude artifact: https://claude.ai/artifact/Q35uEdK1hrKUhbZ15vWvVy (share it from its page if you want others to see it).

## Quick start
```bash
pip install -r requirements-dev.txt
make test          # runs every POC's tests
make validate      # HCL syntax check for all Terraform (run `terraform validate` per POC in CI with providers)
```
Each Terraform folder is standalone: `cd poc-XX/terraform && terraform init && terraform apply`. Start in a sandbox account. Several POCs create billable resources (Synthetics canaries, Incident Manager, FIS, Backup).

## Suggested learning path
1. `poc-01` (SLOs are the language everything else uses)
2. `poc-02` → `poc-03` (detect, respond, learn)
3. `poc-05` → `poc-04` → `poc-06` (change safety, resilience, proving it)
4. `poc-07` → `poc-08` (capacity and data)
5. `poc-09` → `poc-10` → `poc-11` (automation, platforms, AI)
