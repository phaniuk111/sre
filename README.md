# SRE and platform engineering → AWS: hands-on POCs for interview prep

Proofs of concept that turn the ideas in two books into **working code and Terraform on AWS**: *Site Reliability Engineering, 2nd Edition* (O'Reilly, 2026), POCs 01–11, and the early release of *Platform Engineering at Google* (O'Reilly), POCs 12–19. Each POC has a README with a concept-to-AWS map and interview talking points, Python you can run and test locally, and Terraform for the AWS side.

> These are my own implementations and explanations, written as study material. They don't reproduce the books. Buy or borrow them for the full argument and case studies.

## Book 1 map: SRE chapter → POC → AWS services
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
| I–II · 1–7 Context, culture, org | [`docs/`](docs) concept map, culture/org cheat sheet, interview question bank, full-reading notes for chapters 4–23 | n/a |

## Book 2 map: *Platform Engineering at Google* chapter → POC → AWS services
The book is an early release: ten chapters were published when this was written, out of a planned thirty-one. Chapter numbers are the ones planned for the final book.

| Chapter | POC | AWS services used |
|---|---|---|
| 9 Coupling | [`poc-12-coupling-discovery`](poc-12-coupling-discovery) finds shared databases, implicit queue coupling, distributed monoliths, junk-drawer configs, call cycles and hidden physical dependencies from traces, access logs, deploy history and chaos results | X-Ray / Application Signals, CloudTrail, EventBridge, Schema Registry, FIS |
| 15 Security (Safe Coding) | [`poc-13-safe-coding`](poc-13-safe-coding) a `TrustedSql` type and safe database wrapper that make SQL injection inexpressible, plus a CI conformance checker | RDS Data API / Aurora / Athena parameters, CodeBuild |
| 15 Security (supply chain), 16 Reliability (break-glass), 12 Shared fate | [`poc-14-supply-chain-gate`](poc-14-supply-chain-gate) signed attestations, a deploy gate with SLSA-level policy, bad-change blocking, audited break-glass | AWS Signer, Lambda code signing, ECR, CloudTrail, EventBridge, SNS |
| 15 Security (Safe Deployment) | [`poc-15-safe-deployment`](poc-15-safe-deployment) versioned blueprints with locked invariants, drift and conformance report | CDK / Terraform modules, Service Catalog, Config, cfn-guard, Security Hub |
| 16 Deep dive: reliability | [`poc-16-risk-profile-rollouts`](poc-16-risk-profile-rollouts) rollout policy from service tier and error budget, drain invariants with break-glass, platform SLOs that count system-caused failures only | CodeDeploy deployment configs, AppConfig, Route 53 ARC safety rules, CloudWatch |
| 14 Deep dive: efficiency | [`poc-17-efficiency-apm`](poc-17-efficiency-apm) application productivity metrics, growth-or-regression classifier, on-by-default rollout decision, wasted-work estimate | CloudWatch EMF and metric math, Container Insights, CUR, Compute Optimizer, a continuous profiler |
| 18 Developer experience, 19 Platform as a product | [`poc-18-platform-scorecard`](poc-18-platform-scorecard) user, system and business scorecard; DORA metrics for adopters against non-adopters; deprecation brownout plan | EventBridge pipeline events, CUR with cost allocation tags, CloudTrail |
| 22 AI with platform engineering | [`poc-19-ai-platform-signals`](poc-19-ai-platform-signals) model freshness, drift (PSI), confidence gate, silent-failure SLO, model promotion gate | SageMaker Pipelines, Feature Store, Model Registry, Model Monitor, Bedrock Guardrails |
| 10 Layers, 12 Shared fate, 24 Education, and all of the above | [`docs/platform/`](docs/platform) full study notes for the ten chapters, a shared-fate contract (resources, rights, responsibilities), and product templates (jobs to be done, roadmap, deprecation, education plan) | n/a |

## Reading notes and synthesis
Built in passes: chapter summaries first, then a synthesis across both books. [`docs/progress.md`](docs/progress.md) records the state and how to rebuild.

| File | What it is |
|---|---|
| [`docs/executive-summary.md`](docs/executive-summary.md) | Both books on one page, and where they meet |
| [`docs/knowledge-map.md`](docs/knowledge-map.md) | 91 concepts in 12 themes, each with chapters and the POC that implements it |
| [`docs/requirements.md`](docs/requirements.md) | 57 things a team or platform should have in place, as a checklist with sources |
| [`docs/claims.md`](docs/claims.md) | Numbers to know cold, then figures extracted from every chapter |
| [`docs/chapters/`](docs/chapters) | One summary per chapter: 23 SRE, 10 platform |

The course page itself is in [`course/`](course): `index.html` opens in any browser, and `build.py` rebuilds it.

## Study guide
An interactive course with one lesson per chapter (diagrams, AWS mapping, interview practice, quick checks, exercises that point at these POCs) plus labs, flashcards, a quiz and interview drills is published as a private Claude artifact: https://claude.ai/artifact/Q35uEdK1hrKUhbZ15vWvVy (share it from its page if you want others to see it). It covers both books: all 23 SRE chapters and the 10 published platform engineering chapters, with redrawn versions of the key diagrams, 190 flashcards, 72 quiz questions and 21 interview drills. The diagram notes are also in [`docs/diagrams-and-rereads.md`](docs/diagrams-and-rereads.md).

The same deep-dive material is in [`docs/full-reading-notes.md`](docs/full-reading-notes.md): case studies (Paris outage, Maps STPA/CAST, Google Meet at COVID scale, Traffic Director, Persistent Disk, Azure, Disney, Spotify, Waymo), the numbers worth memorising, and an interview angle for each chapter.

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
6. `poc-13` → `poc-14` → `poc-15` (shift security down: code, supply chain, configuration)
7. `poc-16` → `poc-12` → `poc-17` (reliability by default, coupling, efficiency)
8. `poc-18` → `poc-19` (the platform as a product, and platforms for AI)
