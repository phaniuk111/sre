# POC 22: service discovery, relabeling and sharding

**Books:** *Mastering Prometheus* chapters 4 (service discovery, relabeling, HTTP SD) and 6 (sharding with `hashmod`); *Observability with Grafana* chapter 7 (Prometheus receiver with `kubernetes_sd_configs`)

Service discovery returns *candidates* with hidden `__meta_*` labels. Relabeling is where the work happens: it filters candidates, builds the labels you keep, and can even split targets between Prometheus servers. This POC implements the relabel actions exactly as Prometheus defines them, applies them to EC2 discovery output, serves a custom HTTP SD endpoint, and shards targets.

| In `relabel.py` | Idea from the books |
|---|---|
| `ec2_discovery()` | what `ec2_sd_configs` returns: `__address__` and `__meta_ec2_*` labels, one per tag |
| `relabel()` | `replace`, `keep`, `drop`, `hashmod`, `labelmap`, `labeldrop`, `labelkeep`; regexes are anchored; replacing with an empty string deletes the label |
| `finalize()` | after relabeling `instance` defaults to `__address__` and every `__` label is removed |
| `EC2_RELABEL`, `discover()` | keep running, tagged instances; job from the `Service` tag; friendly `instance` name while still connecting by IP |
| `http_sd_app()`, `validate_http_sd()` | a custom HTTP SD endpoint and its contract: HTTP 200, `application/json`, UTF-8, a list of `{targets, labels}` |
| `shard_config()`, `shard()` | the two steps the Prometheus Operator adds for `spec.shards`; `hashmod` is md5 of the source labels, last 8 bytes, modulo N |
| `moved_when_resharding()` | going from 2 to 3 shards moves more than half the targets: plan resharding, and put Thanos or remote storage in front so users don't care where a series lives |

`prometheus-ec2.yml` is a full scrape config using the same rules, with scrape limits and a metric-relabel drop. `terraform/iam.tf` is the IRSA role it needs on EKS: `ec2:DescribeInstances`, `ec2:DescribeAvailabilityZones` and `aps:RemoteWrite`.

```bash
python -m pytest -q
```

## On AWS
| Need | Service |
|---|---|
| Discover EC2 instances | `ec2_sd_configs` with IAM `ec2:DescribeInstances`; filter on tags server-side with `filters` |
| Discover pods and services on EKS | `kubernetes_sd_configs`, or ServiceMonitor/PodMonitor with the Prometheus Operator |
| Agentless scraping on EKS | the AMP managed collector (scraper) takes a Prometheus scrape config and writes to an AMP workspace |
| CMDB or custom inventory | `http_sd_configs` backed by a small Lambda behind a function URL or an internal ALB |
| Cloud Map services | `consul_sd`-style patterns aren't built in; expose Cloud Map through HTTP SD |
| Single pane over shards | Amazon Managed Service for Prometheus as the remote-write target for every shard |

## Interview talking points
* Two kinds of relabeling: `relabel_configs` before the scrape (which targets, which labels) and `metric_relabel_configs` after it (which series to keep).
* Debug with `/service-discovery`: it shows discovered labels before and after relabeling and which targets were dropped.
* Label targets by a stable name but connect by IP so a DNS outage doesn't become a monitoring outage.
* Sharding by service is predictable for humans; `hashmod` sharding balances load but nobody knows which shard has a series, so pair it with Thanos or remote write.
* HTTP SD replaced cron jobs writing `file_sd` files; it is the supported way to plug in your own source of truth.
