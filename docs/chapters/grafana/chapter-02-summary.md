# Grafana chapter 2: Instrumenting applications and infrastructure

*Observability with Grafana (Rob Chapman and Peter Holmes, Packt, 2024). Course lesson: `#g-2`. Code: POC 27 · 6. Read: full text, one pass; all figures seen; lesson covers chapters 2–3.*

## Summary

A metric is a name, a value and dimensions. The four types behave differently, and protocols define them slightly differently: StatsD resets counters on every flush, Prometheus only when the process restarts. Know which one you are using.

Best practice from the book: decide what you want metrics for first (it feeds SLIs and SLOs), manage cardinality (labelling by server gives hundreds of series, by user millions, and you pay for each), and add context with exemplars so a data point links to a trace.

A trace is a directed acyclic graph of spans. The trace has an ID, a name and start and end times. Each span has the trace ID, its own span ID, its parent’s span ID, a name and timings. If a service receives no trace ID it starts a new one; otherwise it passes the one it received to every call it makes.

**Automatic instrumentation** is fast to adopt and gives visibility in minutes, by bytecode manipulation in Java or monkey patching in Python and JavaScript; without care it costs performance and money. **Manual instrumentation** gives exactly the telemetry you want but needs code and API knowledge. The industry is converging on OpenTelemetry SDKs; Spring Boot 3’s Micrometer exports OTLP by default.

## Key ideas

- Structured, semi-structured and unstructured logs, and seven common formats
- Counters, gauges, histograms and summaries, and how metric protocols differ
- Spans, traces and tracing protocols, and best practice for each signal
- Automatic versus manual instrumentation; infrastructure telemetry through syslog and SNMP
- The book’s lab: Grafana Cloud plus the OpenTelemetry demo

## What the lesson covers

- Logs
- Metrics
- Traces
- Libraries
- Infrastructure
- The lab

## Terms

Automatic instrumentation, Manual instrumentation

## Interview line

I prefer structured logs in JSON or logfmt so nobody depends on fragile parsing, histograms over summaries because they aggregate across instances, and OpenTelemetry SDKs for traces with context propagated on every call and sampling decided at the root. Before instrumenting I decide what questions the data must answer, because that drives which SLIs I need and keeps cardinality, and cost, under control.

## On AWS

The ADOT SDKs and collector are AWS’s OpenTelemetry distribution; auto-instrumentation agents exist for Java, Python, .NET and Node.js and are injected by the ADOT operator on EKS. CloudWatch embedded metric format turns structured JSON logs into metrics for CloudWatch-native setups. For network gear, run an SNMP exporter or the collector’s SNMP receiver in a VPC that can reach devices, and syslog into CloudWatch Logs or Loki through Fluent Bit.

## Takeaways

- Prefer structured logs; know which format each source uses.
- Know your metric types and your protocol’s definitions of them.
- Traces depend on propagation; sample at the root.
