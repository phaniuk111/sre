# Grafana chapter 1: Observability, the signals, and the Grafana stack

*Observability with Grafana (Rob Chapman and Peter Holmes, Packt, 2024). Course lesson: `#g-1`. Read: full text, one pass; all figures seen.*

## Summary

Modern systems have moved from **complicated** (an engine: clear cause and effect) to **complex** (city traffic: behaviour emerges from interactions). Downtime is expensive; the book quotes an estimate of about $9,000 a minute from a 2016 Ponemon study. Observability is how you manage that risk, and done badly it is a cost of its own.

The term comes from control theory. James Watt’s steam-engine governor illustrates both ideas. Its spinning weights measure one predefined quantity, shaft speed, and adjust the throttle: that is **monitoring**. But if the governor spins oddly fast or slow, you can infer that the sliding ring is sticking or the adjustment is wrong, without having defined “too fast” in advance and without knowing the whole engine: that is **observability**, inferring internal state from external outputs.

The lesson: the same data that drives alerts also answers questions nobody thought to alert on.

A trace across the canal locks: the ship gets a trace ID at the first lock, each lock creates a span (entry, exit, events such as gates opening, attributes such as the ship’s ID) and passes the trace ID and its span ID on to the next lock.

## Key ideas

- Monitoring versus observability, from control theory and a steam engine
- Metrics, logs, traces, and the other signals: profiles and events
- What each part of the LGTM stack does, and what else Grafana Labs offers
- The alternatives, and the SaaS versus self-hosted choice

## What the lesson covers

- The big picture
- The signals
- The Grafana stack
- Alternatives and deployment

## Claims and numbers

- Downtime is expensive; the book quotes an estimate of about $9,000 a minute from a 2016 Ponemon study.
- Tempo Traces on object storage, aiming to keep 100% of the read path; 2M+ spans per second at 1.0.

## Terms

complicated, complex, monitoring, observability, Loki, Grafana, Tempo, Mimir, Faro, Pyroscope, Across the books

## Interview line

Monitoring watches for conditions you defined in advance; observability lets you infer internal state from outputs and answer new questions. I use metrics to know something is wrong, traces to find where, logs and profiles to find why, and events like deployments for context. In the Grafana world that is Mimir or Prometheus, Tempo, Loki and Pyroscope, all on object storage, with Grafana on top.

## On AWS

The AWS-native equivalents: CloudWatch metrics and Amazon Managed Service for Prometheus for metrics, CloudWatch Logs for logs, X-Ray (and Application Signals) for traces, CloudWatch RUM for the frontend, CloudWatch Synthetics for probes, and Amazon Managed Grafana to view them all. Many teams mix: AMP plus Amazon Managed Grafana for application metrics, CloudWatch for AWS service metrics, and Loki or CloudWatch Logs for logs.

## Takeaways

- Monitoring answers known questions; observability lets you ask new ones.
- Metrics, logs, traces, profiles and events each answer a different question.
- LGTM: Loki, Grafana, Tempo, Mimir, all on object storage.
