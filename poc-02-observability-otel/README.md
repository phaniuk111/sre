# POC 02: Observability with OpenTelemetry on AWS (ADOT, CloudWatch, X-Ray)

**Book chapters:** 9 (Observability & Monitoring), 8 (CUJs, failure concentration), Appendix F/G

## Pieces
| Path | Book idea | AWS service |
|---|---|---|
| `app/app.py` | RED metrics, structured logs carrying trace IDs, CUJ name in OTel **baggage**, version header for client-focused change supervision | Runs on ECS/EKS/EC2 |
| `collector/adot-config.yaml` | OTel Collector pipeline; drops high-cardinality attributes before they become metric labels | ADOT → CloudWatch EMF + X-Ray |
| `synthetics/` + `aws_synthetics_canary` | Probe the **whole** journey (search → cart → checkout) and validate payloads ("successfully failing" servers) | CloudWatch Synthetics |
| `aws_cloudwatch_metric_alarm.latency_anomaly` | Learned baseline instead of static thresholds | CloudWatch Anomaly Detection |
| `aws_cloudwatch_log_metric_filter` | Logs → SLI | CloudWatch Logs |
| `aws_xray_group` | Slice traces by CUJ | X-Ray groups + Insights |
| `detectors/cohort_latency.py` | Appendix F: cohort baselines, z-scores, "excess of outliers" regression detection | Run in Lambda on a schedule, publish as custom metric |
| `detectors/failure_concentration.py` | Information gain to find the cohort a single SLO number hides | Athena / Logs Insights export → Lambda |

## Run it
```bash
# unit tests for the detectors
pip install pytest && python -m pytest -q

# local stack that ships real telemetry to your AWS account
AWS_PROFILE=sandbox AWS_REGION=eu-west-2 docker compose up --build
# then look at: CloudWatch > Metrics > SRE/Checkout, X-Ray > Traces (group checkout-cuj)

# infra
cd terraform && terraform init && terraform apply -var base_url=https://your-alb.example.com
```

## High-availability vs analytics telemetry on AWS
| Book category | Needs | AWS fit |
|---|---|---|
| High-availability (alerting, control loops, probers) | seconds of latency, few dependencies, freshest data first | CloudWatch metrics/alarms, Synthetics, Route 53 health checks |
| Analytics (trends, capacity, investigations, audits) | high cardinality, cheap long retention, complex queries | CloudWatch Logs Insights, S3 + Athena, Amazon Managed Prometheus/Grafana, OpenSearch |

Keep the alerting path free of dependencies on the thing it monitors: e.g. don't host the only copy of your alert routing inside the same VPC/account that is failing.

## Interview talking points
* Monitoring tells you *whether* it's broken; observability lets someone without tribal knowledge work out *why*.
* Golden signals (latency, traffic, errors, saturation) / RED / USE are starting points; CUJ-based SLIs are the goal.
* Correlation in OTel: **resource** (where), **context propagation** (trace IDs, baggage), **instrumentation scope / stack traces** (which code).
* Cardinality is the cost driver: user IDs belong in logs/traces, never in metric dimensions.
* Treat an observability vendor choice as a 10-year decision (the Waze migration story).
