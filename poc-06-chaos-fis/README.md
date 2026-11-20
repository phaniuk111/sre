# POC 06: Disaster & resilience testing with AWS FIS (DiRT on AWS)

**Book chapters:** 14 (DiRT, fault injection, service-level test dimensions), 17 (qualification), 21 (AI-assisted resilience verification)

| Path | What |
|---|---|
| `terraform/` | Two **AWS Fault Injection Service** templates: *AZ loss* (stop every checkout instance in one AZ for 10 min) and *dependency latency* (+300 ms to payments on 50% of hosts). Both use the **SLO fast-burn alarm as the stop condition**. |
| `dirt-catalog.yaml` | Test catalog across the book's dimensions (capacity, data, infra, dependencies, failure handling, operational, tooling, business continuity), each written as **X resilient to Y measured by Z** with the AWS tool that runs it |
| `verify_experiment.py` | Checks the evidence: the fault took effect, the other AZs absorbed the load, and the SLI stayed within SLO. A test where the fault never happened is **NOT PROVEN**. |

```bash
python -m pytest -q
cd terraform && terraform apply -var stop_condition_alarm_arn=<POC01 composite alarm arn>
aws fis start-experiment --experiment-template-id <id>
```

## How to run a DiRT-style programme on AWS
1. **Top-down and bottom-up:** leadership sets a yearly theme (e.g. "lose a Region"); each team adds its own tests from its postmortems.
2. Start in staging, then move to production with a small blast radius (`PERCENT(10)` of targets, one AZ) and always with a **stop condition**.
3. Include live-fire tests *and* tabletop exercises (Wheel of Misfortune).
4. Most DiRT tests turn up missing monitoring. Treat "did the right alert fire?" as part of every test.
5. Market the results internally. Present it as making systems better, not as compliance.

## Static stability (AWS term) ↔ book ideas
Pre-provision enough capacity in the surviving AZs (N+1 AZs) so an AZ loss needs **no control-plane action** to recover. The book's version: failure domains, N+1 redundancy loss, and not depending on recovery tooling that might be down too (emergency mode).
