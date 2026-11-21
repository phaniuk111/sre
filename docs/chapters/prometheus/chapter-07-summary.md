# Prometheus chapter 7: Keeping Prometheus fast: cardinality, recording rules, jitter, profiling and GC

*Mastering Prometheus (William Hegedus, Packt, 2024). Course lesson: `#m-7`. Code: POC 21 · 7. Read: full text, one pass; all figures seen.*

## Summary

*Status → TSDB Status* lists the top ten in four tables. **Label names by value count** is the important one; ignore `__name__`, which is always first. **Series count by metric name** shows which metrics are expensive to query (the book’s top metric was four times slower than `up`). **Label names with high memory use** factors in value length. **Series count by label pair** mostly finds labels that are the same everywhere, such as `env="production"`, which belong in external labels.

Drop what you don’t need in `metric_relabel_configs` (or `metricRelabelings` on a ServiceMonitor): whole metrics with `action: drop` on `__name__`, or individual histogram buckets by matching `__name__` and `le` together, as the chart already does for API server latency buckets. `labeldrop` works too, but the remaining series must still be unique or the scrape is rejected.

Then prevent the next one with **limits**, set globally or per job: `sample_limit`, `label_limit`, `label_value_length_limit` and `label_name_length_limit`. They are checked after metric relabeling, and any breach fails the **whole** scrape, so pair them with an alert on `up == 0`. Limits are what let you give teams self-service onboarding without fearing one bad deploy.

A recording rule evaluates PromQL on a schedule and stores the result as a new series, so dashboards read one cheap series instead of recomputing an expensive query on every refresh.

## Key ideas

- Reading /tsdb-status and finding the label that causes the damage
- Dropping series safely and setting scrape limits
- Recording rule naming and the cost of too many rules
- Scrape jitter, pprof and promtool debug, query logs and limits
- GOGC and GOMEMLIMIT

## What the lesson covers

- Finding cardinality
- Fixing it
- Recording rules
- Scrape jitter
- pprof and promtool debug
- Query logs and limits
- GOGC and GOMEMLIMIT

## Claims and numbers

- Prometheus snaps timestamps within 2 ms by default; --scrape.timestamp-tolerance raises that, up to 1% of the scrape interval.
- In-flight queries are always tracked in queries.active in the data directory and logged after a crash. --query.max-concurrency (default 20, low for big setups) and --query.max-samples (default 50 million samples loaded, not returned) stop runaway queries.

## Terms

limits, whole, Across the books, Series and cardinality, Scrape limits, Observability cost

## Interview line

I find cardinality on the TSDB status page, look for label names with the most values, drop what nobody uses with metric relabeling, and put sample and label limits on scrape jobs so a bad deploy fails one scrape instead of the server. I precompute dashboard queries with recording rules named level:metric:operations, check scrape jitter when disk usage grows, and on big servers set GOGC to 50 and GOMEMLIMIT to about 90% of memory.

## On AWS

On AMP you don’t tune GC or TSDB flags, but cardinality still matters because you pay per sample ingested and per active series: drop at the scraper (Prometheus agent, ADOT, or the AMP managed collector all accept relabeling) and watch AMP’s CloudWatch usage metrics against your quotas. Recording rules run in AMP rule groups namespaces. If you self-manage on EKS, set memory requests from head-series counts, set `GOMEMLIMIT` through an environment variable, and keep `promtool debug all` output in S3 before restarts.

## Takeaways

- TSDB Status finds the label; metric relabeling removes it; limits stop it returning.
- Recording rules make dashboards cheap but cost the server constantly.
- Jitter inflates disk; GOMEMLIMIT prevents GC-driven OOMs.
