# POC 01: SLOs, error budgets and burn-rate alerting on AWS

**Book chapters:** 8 (SLOs), 9 (statistics for alerting), Appendix E (composing SLOs)

## What you'll learn
| Concept | Where |
|---|---|
| SLI as `good/valid`, SLO, error budget, burn rate | `slo/budget.py` |
| Multi-window multi-burn-rate alerts (Google's 2%/1h page and 10%/3d ticket rules, plus the Workbook's 4-rule version) | `slo/alerting.py` |
| Low-traffic alerting with the Wilson score interval (reproduces the book's 173/42/24 examples) | `slo/stats.py` |
| Serial vs hedged dependency composition, k-of-n quorum | `slo/composition.py` |
| Bad-minute SLOs for noisy client telemetry and CUJ aggregation | `slo/bad_minutes.py` |
| The same maths as CloudWatch metric-math + composite alarms | `terraform/` |

## Run the maths locally
```bash
pip install pytest
python -m pytest -q
python - <<'EOF'
from slo import ErrorBudget, min_failures_to_alert, serial_availability
print(ErrorBudget(0.999).allowed_downtime_minutes)      # 43.2
print(min_failures_to_alert(200, 0.144))                # 42  (book example)
print(serial_availability([0.9995, 0.9999, 0.9999]))    # API GW -> Lambda -> DynamoDB ceiling
EOF
```

## Deploy the alarms
```bash
cd terraform
terraform init
terraform apply -var alb_arn_suffix=app/my-alb/0123456789abcdef -var slo_target=0.999
```
Then subscribe PagerDuty/Opsgenie (or AWS Incident Manager, see POC 03) to the `-slo-page` topic and Jira/email to `-slo-ticket`.

### How the AWS pieces map to the theory
| Book concept | AWS implementation |
|---|---|
| SLI = good / valid | Metric math: `1 - (Target5xx + ELB5xx) / RequestCount` |
| Long window AND short window | Two `aws_cloudwatch_metric_alarm` → one `aws_cloudwatch_composite_alarm` |
| Page vs ticket | Separate SNS topics |
| Latency SLO | `TargetResponseTime` `p99` alarm (percentile stat) |
| Native SLO objects | CloudWatch **Application Signals** SLOs (period or request-based, with burn-rate alarms); use them if your services are instrumented with ADOT/Application Signals |
| Error-budget review in sprint retro | CloudWatch dashboard `<service>-slo` |

## Interview talking points
* **Why not 100%?** Cost grows steeply and users can't tell the difference past a point; the gap is the budget you spend on velocity (deploys, experiments).
* **Why two windows?** The long window shows the burn is *significant*; the short window proves it's *still happening* so the alert clears minutes after recovery.
* **Why the Wilson interval?** On 20 req/min a single failure looks like 5% errors; a static threshold pages on noise. Page only when the *lower bound* of the confidence interval is above your threshold.
* **SLO ceiling:** a service can't be more available than its serial hard dependencies multiplied together, unless you add redundancy (hedging, fallbacks, caches) and the failures really are independent.
