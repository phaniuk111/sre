# POC 21: inside the TSDB, compression, jitter, the index and cardinality

**Books:** *Mastering Prometheus* chapters 3 (TSDB internals), 6 (cardinality as a limit) and 7 (finding and fixing cardinality, scrape limits, scrape jitter); *Observability with Grafana* chapter 5 (blocks, chunks, index, head block and WAL)

Prometheus stores each sample in about one to two bytes instead of sixteen because regular scrapes and slowly changing values compress extremely well. That only holds while scrapes land on time, which is why the Prometheus book calls scrape jitter the most common cause of oversized blocks. And it finds series quickly because of an inverted index, which is exactly what high cardinality inflates.

| Function in `tsdb.py` | Idea |
|---|---|
| `timestamp_bits()` | delta-of-delta encoding with Prometheus' bucket sizes: 1 bit when the interval is unchanged, 16, 20 or 24 bits otherwise, 68 in the worst case |
| `value_bits()` | XOR of each float with the previous one, reusing the previous leading/trailing-zero window |
| `bytes_per_sample()` | the result: a counter scraped on time costs about a byte per sample; the same data with ±30 ms jitter costs more than twice as much |
| `snap_timestamps()`, `jitter_report()` | `--scrape.timestamp-tolerance` (default 2 ms, at most 1% of the interval) and a report like `oy-scrape-jitter` |
| `Index.select()` | postings lists per `label=value`, intersected starting from the shortest list with binary-search seeks, as the TSDB does |
| `compaction_ranges()` | 2 h head blocks, compacted in steps of three, capped at 31 days or 10% of retention |
| `cardinality_report()` | the four `/tsdb-status` tables: label value counts, series per metric, series per label pair, and labels present on every series (make those external labels) |
| `apply_limits()` | `sample_limit`, `label_limit`, `label_value_length_limit`, `label_name_length_limit`: any breach fails the whole scrape |

```bash
python -m pytest -q
```

## On AWS
| Need | Service or setting |
|---|---|
| Don't run the TSDB at all | Amazon Managed Service for Prometheus stores, compacts and replicates for you; you pay per sample ingested and per GB stored, so cardinality is now a line on the bill |
| Self-managed Prometheus on EKS | a StatefulSet on gp3 EBS volumes; one volume per replica, in different AZs |
| Ingestion limits | AMP has per-workspace quotas for active series and ingestion rate (see Service Quotas); `sample_limit` in the scrape config protects you before you hit them |
| Find cardinality in AMP | query `count by (__name__)({__name__=~".+"})` or the label-value-count pattern from this POC through Amazon Managed Grafana |
| Drop it before it costs | `metric_relabel_configs` in the scraper (Prometheus agent, ADOT collector or the AMP managed collector) |

## Interview talking points
* A series is a metric name plus a unique label set. Cardinality is the number of series, and each one costs head-block memory, index size and query time.
* Labels with unbounded values (user ID, request ID, full URL path, IP) belong in logs or traces, not metric labels.
* The head block keeps about two hours in memory, protected by a write-ahead log; blocks are immutable and compacted in the background.
* Delta-of-delta timestamps make regular scrapes nearly free; jitter breaks that, so check alignment when disks grow unexpectedly.
* Scrape limits turn a cardinality explosion into one failed scrape instead of an outage; pair them with an alert on `up == 0`.
