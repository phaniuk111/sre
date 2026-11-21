# Prometheus chapter 3 (promql): PromQL: selecting, combining and computing

*Mastering Prometheus (William Hegedus, Packt, 2024). Course lesson: `#m-3q`. Code: POC 20 · 7. Read: full text, one pass; all figures seen.*

## Summary

PromQL works on vectors of series, not on rows. A **selector** picks series by name and labels. An **instant vector** holds one sample per series at one moment. A **range vector** holds every sample in a window, like `[5m]`, and only functions accept it. An **instant query** evaluates once; a **range query** (what Grafana graphs use) evaluates the same expression at every step across a time range.

At any evaluation time an instant selector returns the newest sample of each series that is at most five minutes old. When a target disappears, Prometheus writes a **staleness marker** so its series end immediately rather than lingering for five minutes. That lookback is also why a missing scrape doesn’t make a graph gap, and why an alert can reset when the series vanishes for longer.

`sum by (namespace) (…)` keeps only the listed labels. `sum without (pod, instance) (…)` drops the listed ones and keeps everything else. The book prefers **without**, because it preserves labels you didn’t think about, such as `cluster` or `job`, which later joins and alert routing often need.

Arithmetic between two vectors pairs up elements with **identical label sets** (ignoring the name). Anything without a partner is dropped silently, which is the most common reason a ratio returns nothing.

## Key ideas

- Instant vectors, range vectors, instant and range queries, staleness
- Aggregation with by and without, and when to prefer without
- Vector matching: on, ignoring, group_left, group_right, and info-metric joins
- and, or, unless, and why unless is the alerting favourite
- rate, irate, increase, changes and delta, including how rate extrapolates

## What the lesson covers

- The big picture
- Aggregation: by versus without
- Vector matching
- Functions on counters and gauges
- Extrapolation, exactly

## Claims and numbers

- Head block, WAL and blocks : Two hours in memory with a write-ahead log, then immutable blocks compacted up to 31 days.

## Terms

selector, instant vector, range vector, instant query, range query, staleness marker, without, identical label sets, info metric, rate, then sum, Across the books, Series and cardinality, rate, increase and irate

## Interview line

A selector returns an instant vector of the newest sample per series within five minutes; a range selector returns every sample in a window, and functions like rate turn that back into an instant vector. Binary operators match on all labels unless I narrow them with on or ignoring, group_left copies labels from an info metric, and unless is how I suppress an alert in a known condition. For counters I always rate first and aggregate second.

## On AWS

AMP and Amazon Managed Grafana speak standard PromQL, so everything here works unchanged: point the Grafana Prometheus data source at the AMP query endpoint with SigV4 enabled. CloudWatch has its own metric math and Metrics Insights for AWS service metrics; for application metrics PromQL is the more portable skill. AMP query limits (samples per query, query time) play the role of Prometheus’ `--query.max-samples`.

## Takeaways

- Instant vectors for values, range vectors for functions, five-minute lookback with staleness markers.
- Matching is on all labels by default; on, ignoring and group_left are how you join.
- Rate first, aggregate second; irate for graphs, rate for alerts.
