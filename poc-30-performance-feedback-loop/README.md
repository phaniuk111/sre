# POC 30: performance feedback loops: load tests, deployment gates, Web Vitals and flame graphs

**Books:** *Observability with Grafana* chapters 12 (real user monitoring and Web Vitals), 13 (Pyroscope continuous profiling and k6 load testing) and 14 (observability through the DevOps life cycle, automated deployment verification)

These are the parts of observability that feed back into development rather than into on-call. `perf.py` covers four of them.

| In `perf.py` | Idea |
|---|---|
| `profile()` | k6 `stages` for the six test types: smoke, average, stress, spike, breakpoint, soak |
| `thresholds_from_slo()`, `gate()` | use the team's SLOs as k6 thresholds (`http_req_failed: rate<0.001`, `http_req_duration: p(95)<300`) and fail the pipeline on the summary export |
| `k6_script()` → `k6/checkout-average.js` | a generated k6 script with the init / `setup()` / default / teardown life cycle and a `check()` |
| `verify_deployment()`, `DEPLOY_CHECKS` | chapter 14's "let the CD job watch the dashboard": query error ratio from logs, login success from a smoke test and downstream errors; two bad readings in a row roll back, a single blip doesn't |
| `VITALS`, `rate_vital()` | Web Vitals scored at the 75th percentile: LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1, FCP ≤ 1.8 s, TTFB ≤ 0.8 s are "good" |
| `parse_collapsed()`, `top_table()`, `flame()` | Pyroscope's Top Table (self vs total) and flame-graph widths; the x-axis is not time |

```bash
python -m pytest -q
k6 run k6/checkout-average.js --summary-export=summary.json   # if you have k6
```

## On AWS
| Need | Service |
|---|---|
| Real user monitoring | CloudWatch RUM (Web Vitals, JS errors, sessions, X-Ray linking), or Grafana Faro to Grafana Cloud |
| Synthetic checks | CloudWatch Synthetics canaries; the Prometheus blackbox exporter on EKS |
| Load testing at scale | k6 on EKS with the k6 operator, Grafana Cloud k6, or the *Distributed Load Testing on AWS* solution |
| Deployment gates | CodeDeploy or Argo Rollouts analysis runs that query AMP / CloudWatch alarms and roll back automatically |
| Deployment markers | post a Grafana annotation from the pipeline; CloudWatch dashboards can show deployment events through Application Signals |
| Continuous profiling | Pyroscope on EKS (eBPF DaemonSet or language SDKs) or Grafana Cloud Profiles |

## Interview talking points
* Load-test thresholds should be your SLOs, so "passed the load test" and "won't page in production" mean the same thing.
* Six test shapes answer six questions: does it work, normal load, sustained peak, sudden spike, where it breaks, leaks over time.
* Keep load-test telemetry out of production stacks; it is high volume and low value.
* Automated verification after a deploy (error ratio, a smoke-tested login, downstream errors) with automatic rollback cuts MTTR for bad releases.
* Profiles answer "why is it slow or expensive": self time finds hot functions, total time finds hot call paths.
* Web Vitals are judged at p75 of real page loads; INP replaced FID as a Core Web Vital in March 2024.
