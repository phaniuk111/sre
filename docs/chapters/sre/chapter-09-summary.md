# SRE chapter 9: Observability and monitoring

*Site Reliability Engineering, 2nd Edition. Course lesson: `#ch-9`. Code: POC 02. Read: full text, re-read in a third pass.*

## Summary

Traditional monitoring depended on tribal knowledge and on engineers correlating dashboards by hand. It answers questions you already knew to ask.

**Observability** combines time series, logs (including wide structured events), traces and continuous profiles so that someone *without* deep prior knowledge can test and reject hypotheses quickly, without shipping new code.

The metric that matters most is **time to mitigate**, from customer-centric detection to containment, followed by time to detect. The trend is towards knowledge graphs of assets and dependencies, AI-assisted investigation and views centred on customers instead of services.

Give users one SDK, one config and one query endpoint across both. Keep the alerting path independent of the systems it watches.

## Key ideas

- the difference between monitoring and observability
- Google’s three strategies for observability at microservice scale
- why alerting telemetry and analytics telemetry are separate systems
- how OpenTelemetry correlates signals

## What the lesson covers

- Monitoring versus observability
- Google’s three strategies at microservice scale
- Two kinds of telemetry
- OpenTelemetry
- What only clients can see
- Change, retention and privacy
- The statistics worth knowing
- From user goal to SLO
- The knowledge graph, drawn

## Claims and numbers

- Google keeps minute-level data in memory for hours, on disk for weeks, and as 30-minute rollups for years.
- Composing dependencies: in series, success multiplies (80% × 90% = 72%).
- With hedging, failure multiplies (1 − 0.2 × 0.1 = 98%).
- One error in twenty requests is a 5% error rate, and it is almost certainly noise.
- The observed rate can cross the line many times without the alert firing (Figure 9-7 shows exactly this).
- For latency, compare against the service’s own past: group requests into cohorts by method, customer and workload shape, keep a 30-day mean and standard deviation, and alert on z-scores.

## Terms

Observability, Latency, Traffic, Errors, Saturation, time to mitigate, Out-of-the-box dashboards, Intelligent alerting, Automatic mitigation, Resource, Context propagation, Instrumentation scope, A ten-year decision, Change supervision, Retention follows value, Privacy

## On AWS

ADOT collector → CloudWatch EMF metrics and X-Ray traces; CloudWatch Logs Insights and Athena for analytics; Anomaly Detection alarms; Synthetics and RUM; Managed Prometheus/Grafana; KMS CMKs for telemetry encryption. See POC 02.

## Takeaways

- Observability lets someone without tribal knowledge test and reject hypotheses quickly.
- The metric that matters most is time to mitigate.
- Keep the alerting path fast and simple, the analytics path complete and cheap, and one SDK in front of both.
