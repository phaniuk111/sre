# POC 20: PromQL semantics you can check by hand

**Books:** *Mastering Prometheus* (chapter 3, Data model and PromQL; chapter 5 for `unless` in alerts) and *Observability with Grafana* (chapter 5, PromQL and vector matching)

Most PromQL mistakes in interviews and in production come from five places: what an instant selector actually returns, how `rate()` handles resets and window edges, `irate()` against `rate()`, `histogram_quantile()` interpolation, and vector matching. `promql.py` implements each of them in a few lines of plain Python so you can see the arithmetic. It is not a parser; you pass series as data.

| Function | What it shows |
|---|---|
| `instant()` | an instant selector returns the newest sample at most 5 minutes old; older series are stale and vanish |
| `rate()`, `increase()` | a port of Prometheus' `extrapolatedRate`: counter resets add back the value before the drop, the result is extrapolated to the window edges (never below zero for a counter), so `increase()` of an integer counter can be fractional |
| `irate()` | only the last two samples: responsive for graphs, too jumpy for alerts |
| `delta()`, `changes()` | for gauges; `delta(count(up)[24h:])` catches targets that silently disappeared, `changes(kube_pod_start_time[24h])` counts restarts |
| `histogram_quantile()` | linear interpolation inside the bucket that holds the rank; a rank in `+Inf` returns the highest finite bound, which is why bucket choice matters |
| `aggregate()` | `by` keeps the listed labels, `without` drops them and keeps everything else |
| `binop()` | one-to-one matching on all labels, `on()`/`ignoring()`, and `group_left(extra)` for info-metric joins |
| `set_op()`, `compare()` | `and`, `or`, `unless` (the NTP-after-reboot alert) and `bool` for window-based SLOs |

The tests use the books' own examples: the blue/red/green vectors from the Grafana book, `kube_node_info` joins and the NTP `unless` alert from the Prometheus book.

```bash
python -m pytest -q
```

`promtool/rate.test.yml` checks the `rate`, `increase` and `irate` example against real Prometheus (106.67, 1.78 and 0.67 for one set of four samples). Change a sample, predict the results, and run `promtool test rules rate.test.yml`.

## On AWS
| Need | Service |
|---|---|
| Run these queries against managed storage | Amazon Managed Service for Prometheus (AMP) exposes the Prometheus query API (`/api/v1/query`, `/query_range`) with SigV4 auth |
| Visualise and alert | Amazon Managed Grafana with the AMP data source (SigV4 toggle on) |
| Precompute expensive queries | AMP rule groups namespaces hold recording and alerting rules in Prometheus format |
| CloudWatch-native equivalent | CloudWatch metric math and Metrics Insights (SQL-like); fine for AWS service metrics, but PromQL is the portable skill |

## Interview talking points
* `rate()` uses the whole window and is reset-aware; `irate()` uses the last two points. Alert on `rate()`.
* `rate()` then `sum()`, never `sum()` then `rate()`: summing counters first hides resets.
* The window must hold at least two scrapes; use at least four times the scrape interval, or `$__rate_interval` in Grafana.
* Arithmetic matches on every label by default; use `on()`/`ignoring()`, and `group_left` to copy labels from an info metric.
* `unless` is the cleanest way to suppress an alert in a known condition.
* `histogram_quantile` is an estimate whose accuracy depends on bucket boundaries; you can aggregate histograms across instances, you cannot aggregate summaries.
