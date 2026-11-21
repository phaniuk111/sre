# Grafana chapter 4: Logs with Loki and LogQL

*Observability with Grafana (Rob Chapman and Peter Holmes, Packt, 2024). Course lesson: `#g-4`. Code: POC 26 · 5. Read: full text, one pass; all figures seen.*

## Summary

Loki was built to be the Prometheus of logs: simple ingestion with no parsing at write time, an index of **labels only**, and everything in object storage. Each entry has a nanosecond timestamp, a label set and the raw line. Every unique label set is a **stream**; a stream’s lines are batched, compressed and stored as chunks. Labels are the index and the only thing you can use to find chunks.

A query is a **stream selector** followed by an optional **pipeline**. The selector uses Prometheus matchers and must include at least one that doesn’t match empty (`{app=~".+"}` is fine, `{app=~".*"}` isn’t). The pipeline runs line by line, left to right, dropping lines as it goes.

Loki runs as one binary, as a simple scalable deployment (read, write and backend targets) or as full microservices. Reads and writes scale independently. The ruler turns LogQL into recording rules and alerts; the compactor applies retention and deduplicates.

## Key ideas

- How Loki stores logs: streams, labels and chunks
- LogQL’s two halves: stream selectors and the pipeline
- Parsers, typed label filters, line and label formatting
- Metric queries over logs, including unwrap
- Loki’s architecture and the label rules that keep it cheap

## What the lesson covers

- The big picture
- LogQL
- Metrics from logs
- Architecture
- Labels are locators, not content

## Claims and numbers

- A bad label multiplies streams and chunks: twenty namespaces, sixty apps and three clusters is 3,600 streams; add a user ID with fifty thousand values and it is 180 million.

## Terms

labels only, stream, stream selector, pipeline

## Interview line

Loki indexes only labels, so a query is a cheap stream selector plus a pipeline that greps, parses and filters lines at read time. I keep labels to low-cardinality locators like namespace, app and cluster, put IDs and paths in the line, filter with |= before parsing, and use unwrap with quantile_over_time when the latency I need only exists in logs.

## On AWS

Self-managed Loki on AWS runs in simple scalable mode on EKS with chunks and the TSDB index in S3 and an IRSA role per component. Ship logs with Fluent Bit (the AWS for Fluent Bit image has a Loki output) or the OpenTelemetry collector’s filelog receiver. CloudWatch Logs with Logs Insights is the AWS-native alternative; POC 26 maps three LogQL queries to their Insights equivalents. Grafana Cloud’s AWS integration can forward CloudWatch Logs into Loki with a Lambda or Firehose.

## Takeaways

- Streams are label sets; labels are the only index.
- Selector, then line filters, then parsers, then typed label filters.
- Labels are locators: keep IDs, paths and codes in the line.
