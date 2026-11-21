# Grafana chapter 5: Metrics in Grafana: PromQL in practice, protocols, storage and exemplars

*Observability with Grafana (Rob Chapman and Peter Holmes, Packt, 2024). Course lesson: `#g-5`. Code: POC 20, 21 · 6. Read: full text, one pass; all figures seen.*

## Summary

The PromQL itself is covered in depth in the Prometheus track. This chapter adds how it feels in Grafana. Explore has a **builder** and a **code** editor; switching the result to a **table** shows every series and label, and clicking a value adds it as a filter. A query of type **Range** draws a graph; **Instant** returns the latest value; a range vector like `x[5m]` on its own only works as an instant query.

Use `$__rate_interval` in every `rate()`: Grafana picks a window at least four scrape intervals long for the current zoom. *Explain* walks through a query step by step, *Kick start your query* offers templates, and the *Query inspector* shows timings and raw data.

Prefer percentiles to averages: a p95 of 300 ms means 95% of requests were at least that fast, while an average hides the slow tail that users notice.

Grafana Cloud still accepts Graphite data for teams that use it. The rest of the detail on blocks is in the TSDB lesson.

## Key ideas

- How PromQL looks from Grafana’s Explore: builder, code, table view, query types
- Two PromQL queries every engineer writes: success rate and p95 latency
- Push and pull protocols: StatsD, OTLP, Prometheus, SNMP
- Graphite, Prometheus and Mimir storage compared
- Exemplars: from a metric point to a trace

## What the lesson covers

- PromQL from Grafana
- Two queries to know by heart
- Push and pull
- Where metrics are stored
- Exemplars

## Claims and numbers

- Prefer percentiles to averages: a p95 of 300 ms means 95% of requests were at least that fast, while an average hides the slow tail that users notice.
- Head block, WAL and blocks : Two hours in memory with a write-ahead log, then immutable blocks compacted up to 31 days.

## Terms

builder, code, table, Range, Instant, Across the books, Series and cardinality, rate, increase and irate, Remote write, Thanos, Mimir, VictoriaMetrics

## Interview line

In Grafana I write PromQL with $__rate_interval, check series in the table view, and choose range or instant query types deliberately. I compute success rates per instance so one bad pod isn’t averaged away, and latency as a histogram percentile. Prometheus pulls, StatsD and OTLP push; Mimir keeps Prometheus’ block format but in object storage with replicated ingestion. Exemplars link a metric point to the trace behind it.

## On AWS

Amazon Managed Grafana with an AMP data source gives the same Explore experience; enable SigV4. AMP stores exemplars sent by remote write, so exemplar stars work when your collector forwards them and the trace backend (X-Ray or Tempo) is configured as the exemplar link. CloudWatch metrics are queried at read time through the CloudWatch data source. POC 20 computes these queries by hand; POC 21 shows the block internals.

## Takeaways

- Use the table view, the right query type and $__rate_interval.
- Success rate by instance; latency by histogram percentile.
- Exemplars connect metrics to traces.
