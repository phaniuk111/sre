# POC 25: remote write, HA deduplication and Thanos

**Books:** *Mastering Prometheus* chapters 6 (HA pairs), 9 (remote write and read, agent mode, VictoriaMetrics, Mimir) and 10 (Thanos components); *Observability with Grafana* chapter 5 (Mimir architecture)

A single Prometheus has no clustering, no replication and local disk. The two ways out are sending samples elsewhere (remote write to Mimir, VictoriaMetrics or AMP) or leaving them where they are and querying across servers (Thanos). Both have to answer the same question: if two identical replicas scrape the same targets, which samples do you keep?

| In `longterm.py` | Idea |
|---|---|
| `remote_write_plan()` | `min_shards ≈ samples/s ÷ capacity`; capacity ≥ 3 × `max_samples_per_send`; an outage longer than the ~2 h WAL loses data |
| `backoff_schedule()` | retries start at 30 ms and double to 5 s |
| `dedup_thanos()` | query-time dedup on the replica label: follow one replica, switch where it has a gap, so a restart leaves no hole |
| `dedup_mimir()` | ingest-time HA tracker: accept only the elected leader; fail over after 30 s of silence, losing the gap |
| `dedup_victoria()` | replicas must have identical external labels; keep one sample per scrape interval |
| `downsample()`, `downsample_plan()` | 5 m aggregates after 40 h, 1 h after 10 days; count, sum, min, max and counter per window. It adds blocks: faster long queries, more storage |
| `queryable()` | different retention per resolution makes old data reachable only at coarse steps |
| `split_by_interval()`, `ResultCache` | Query Frontend splits a week into seven day-long queries and reuses cached days |
| `hashmod_ring()`, `ketama_ring()`, `write_quorum()` | Thanos Receive: Ketama moves far fewer series than plain modulo when you add a receiver; RF=3 needs 2 successful writes |
| `recommend()` | the decision in one function |

`config/prometheus-remote-write.yml` is kube-prometheus-stack values for two replicas writing to AMP with SigV4 and tuned queues; `config/thanos-objstore.yml` is the S3 bucket config for Thanos. `terraform/amp.tf` creates the AMP workspace, the IRSA role with `AmazonPrometheusRemoteWriteAccess`, and an S3 bucket with a lifecycle rule for Thanos blocks.

```bash
python -m pytest -q
```

## On AWS
| Need | Service |
|---|---|
| Remote-write target without running Mimir | Amazon Managed Service for Prometheus: Cortex-based, multi-AZ, object storage, SigV4 auth |
| HA pairs | AMP deduplicates replicas that share `cluster` and differ in `__replica__`, so set that as the replica external label |
| Stateless scrapers | Prometheus `--enable-feature=agent`, the ADOT collector, or the AMP managed collector |
| Thanos on AWS | sidecar uploads to S3; Store, Compactor and Query on EKS; S3 lifecycle to Standard-IA for old blocks |
| Query from Grafana | Amazon Managed Grafana with the AMP data source, or Thanos Query as a Prometheus data source |

## Interview talking points
* Federation is a stop-gap: only aggregated subsets, and it rebuilds the big-Prometheus problem centrally.
* Remote write sends everything by default; filter with `write_relabel_configs` and size queues from `prometheus_tsdb_head_samples_appended_total`.
* Thanos is à la carte: Sidecar plus Query gives a global view and HA dedup; add Store and Compactor for object-storage retention.
* Mimir and AMP store in object storage (cheap, years of retention); VictoriaMetrics uses local disk but is far more frugal.
* Know the dedup models: query-time (Thanos), leader election at ingest (Mimir), identical labels plus per-interval dedup (VictoriaMetrics).
* Downsampling is about query speed over long ranges, not saving space.
