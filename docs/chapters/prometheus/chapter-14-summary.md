# Prometheus chapter 14: OpenTelemetry, and the signals Prometheus doesn’t cover

*Mastering Prometheus (William Hegedus, Packt, 2024). Course lesson: `#m-14`. Code: POC 27, 28 · 6. Read: full text, one pass; all figures seen; lesson covers chapters 14–15.*

## Summary

OpenTelemetry (OTel) is not a program you run; it is a **specification**. It came from a rare event: two competing projects, Google’s OpenCensus (2017) and the CNCF’s OpenTracing (2016), merged in 2019 instead of becoming the fifteenth competing standard in the xkcd strip the book reprints.

Many teams still use Prometheus client libraries for metrics, partly because OTel’s model differs: an OTel “counter” need not be monotonic. In the collector a Prometheus counter becomes a **Sum**, a gauge a **Gauge**, and labels become **data point attributes**.

The `prometheus` receiver accepts a normal `scrape_configs` block, service discovery included. The collector exposes its own metrics on port 8888.

From 2.47, Prometheus can receive OTLP with `--enable-feature=otlp-write-receiver`; the collector’s `otlphttp` exporter points at `http://prometheus:9090/api/v1/otlp` and adds `/v1/metrics` itself. The author’s caution: the `up` series you see then comes from the collector’s own scrape, not from Prometheus, so it says nothing about whether delivery works. Have Prometheus scrape the collector and watch `otelcol_exporter_send_failed_metric_points_total`, and ask whether mixing push and pull is worth it; Prometheus is still pull-first.

## Key ideas

- What OpenTelemetry is: specification, API, SDKs, semantic conventions and OTLP
- The collector’s receivers, processors and exporters, core and contrib
- Scraping Prometheus metrics with the collector, and pushing OTLP into Prometheus
- Logs, traces and exemplars: where metrics stop being enough

## What the lesson covers

- OpenTelemetry in one picture
- The collector
- OTLP into Prometheus
- What metrics can’t do

## Claims and numbers

- Traces The newest core signal and the best signal-to-noise, once sampled: keep 1% of normal requests, half of slow ones and all errors.

## Terms

specification, Gauge, data point attributes, Receivers, Processors, Exporters, Logs, Traces, Exemplars, Across the books, Trace context, Collector topology

## Interview line

OpenTelemetry is a vendor-neutral specification: APIs, SDKs, semantic conventions and the OTLP protocol, with a collector that receives, processes and exports all three signals. I scrape Prometheus metrics with the collector’s prometheus receiver or remote-write from it, and I’m careful with OTLP push into Prometheus because the up series no longer tells you delivery works. Metrics can’t answer every question, so I add logs and sampled traces with shared labels, and exemplars to jump from a metric to a trace.

## On AWS

AWS Distro for OpenTelemetry (ADOT) is AWS’s supported collector and SDKs: OTLP in, Prometheus remote write with SigV4 to AMP, `awsxray` to X-Ray, `awscloudwatchlogs` to CloudWatch Logs, installed on EKS as an add-on. X-Ray propagates its own header, which ADOT’s SDKs handle alongside W3C. CloudWatch Application Signals builds service maps and SLOs on top. POC 28 is a full ADOT architecture for EKS with a validator; POC 27 covers propagation, sampling and TraceQL.

## Takeaways

- OTel is a specification; semantic conventions and OTLP are its most useful parts.
- The collector is receivers, processors and exporters; scraping Prometheus is a receiver like any other.
- Logs and traces cover what metrics can’t; shared labels and exemplars connect them.
