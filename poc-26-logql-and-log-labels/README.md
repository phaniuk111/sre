# POC 26: LogQL, step by step, and how to choose Loki labels

**Books:** *Observability with Grafana* chapters 2 (log formats) and 4 (Loki, LogQL, architecture, label best practice); *Mastering Prometheus* chapter 15 (logs alongside metrics, don't derive metrics from fragile log parsing)

Loki indexes only labels; the log line is stored compressed and never indexed. Every query therefore has two halves: a stream selector that uses the index to pick streams, and a pipeline that greps, parses and filters the lines inside them. `logql.py` implements both halves so you can watch each stage, and a checker that shows why `user_id` must never be a Loki label.

| In `logql.py` | LogQL |
|---|---|
| `select()` | `{app="checkout", env=~"prod\|stage"}`; at least one matcher must not match empty, so `{app=~".*"}` is rejected |
| `line_filter()`, `ip_filter()`, `decolorize` | `\|=`, `!=`, `\|~`, `!~`, `\|= ip("10.0.1.0/24")`, `\| decolorize` |
| `json_parser`, `logfmt_parser`, `pattern_parser()`, `regexp_parser()` | `\| json` (nested keys joined with `_`, arrays skipped), `\| logfmt`, `\| pattern "<ip> - - ..."`, `\| regexp "(?P<x>...)"` |
| `label_filter()` | typed comparisons: `latency > 500ms` is a duration, `size > 2MB` bytes, `status >= 500` a number; failed conversions set `__error__` |
| `no_errors` | `\| __error__=""` |
| `line_format()`, `label_format()`, `drop()` | rewrite the line; `new=old` renames and drops, `new="{{.a}}"` templates and keeps |
| `count_over_time()`, `rate()`, `sum_by()`, `topk()` | metric queries from logs |
| `unwrap_quantile()` | `quantile_over_time(0.99, {...} \| json \| unwrap duration_seconds(latency) [5m]) by (app)` |
| `label_design()` | streams multiply: 20 namespaces × 60 apps × 3 clusters × 50,000 users is six billion streams |

The tests run the book's examples: the `emailservice` restart-count pipeline, typed filters on latency, a pattern parser over NCSA access logs, and the good and bad label lists.

```bash
python -m pytest -q
```

## On AWS
| Need | Service |
|---|---|
| Loki on AWS | Loki in simple scalable mode on EKS with chunks and index in S3 (TSDB index), or Grafana Cloud Logs |
| Ship container logs | Fluent Bit (the AWS for Fluent Bit image) or the ADOT/OTel collector filelog receiver; Fluent Bit has a Loki output |
| CloudWatch-native logs | CloudWatch Logs with Logs Insights; `CLOUDWATCH_INSIGHTS` maps three LogQL queries to their Insights equivalents |
| CloudWatch logs into Loki | the Grafana Cloud AWS integration's Lambda or Firehose forwarder |
| Metrics from logs without fragile parsing | emit the metric in the app; if you must, Loki ruler recording rules remote-write to AMP, or CloudWatch metric filters |
| Log-to-trace links | put `trace_id` in the log line (not as a label) and configure a derived field in Grafana that opens Tempo or X-Ray |

## Interview talking points
* Labels are locators (namespace, app, cluster, job, filename), not content. High-cardinality values make millions of tiny streams and chunks.
* Filter early: line filters before parsers, because parsing is the expensive step.
* Parse at query time with `json`, `logfmt`, `pattern` or `regexp`; that is what makes Loki cheap at ingest.
* LogQL borrows PromQL: range aggregations, `by`/`without`, `topk`; `unwrap` turns a label into a sample.
* Write path: distributor (validates and shards by labels) → ingester (WAL, builds chunks) → object storage; read path: query frontend splits, queriers read ingesters for recent data and storage for old.
