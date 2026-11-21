# POC 28: an OpenTelemetry collector architecture for EKS, and a validator for it

**Books:** *Observability with Grafana* chapters 7 (Kubernetes receivers and processors), 10 (Helm modes and presets, pipelines, connectors) and 11 (agentless, agent, gateway and the Kubernetes reference architecture; buffering for failure); *Mastering Prometheus* chapter 14 (receivers, processors, exporters; OTLP into Prometheus)

Three collector roles, three configs in `config/`, exported to AWS:

| Config | Runs as | Does |
|---|---|---|
| `node-agent.yaml` | DaemonSet | OTLP from pods on the node, `kubeletstats`, `hostmetrics`, `filelog` for container logs, `k8sattributes` enrichment, a disk-backed send queue; traces go through the `loadbalancing` exporter keyed on trace ID |
| `cluster-agent.yaml` | Deployment, **one** replica | `k8s_cluster` metrics and Kubernetes events (`k8sobjects` in watch mode). Two copies would duplicate every event |
| `gateway.yaml` | Deployment behind a Service, 3 replicas | `spanmetrics` and `servicegraph` connectors on all spans, then tail sampling (errors, slow, 1% baseline); metrics to AMP with SigV4, traces to X-Ray, logs to CloudWatch Logs |

`collector.py` checks a config against the rules the books give, plus standard collector practice:

* every component used in a pipeline is defined, and every connector is an exporter in one pipeline and a receiver in another;
* `memory_limiter` first, `batch` last, `health_check` enabled;
* per-node receivers only in a DaemonSet; cluster receivers only in a single instance;
* `filelog` excludes the collector's own logs (otherwise it reads what it writes, the book's "log cascade");
* host and kubelet metrics not every 10 s (the Helm preset default) unless you mean it;
* AMP exporters use the `sigv4auth` extension;
* `tail_sampling_needs_trace_routing()`: with several gateway replicas, agents must route spans by trace ID, or each replica samples fragments. The books don't cover this, and it is the most common tail-sampling bug;
* `buffer_size_mb()`: disk the queue needs to ride out an outage; the book suggests publishing that tolerance as an SLI of the collection layer.

```bash
python -m pytest -q
```

## On AWS
| Need | Service |
|---|---|
| Collector distribution | AWS Distro for OpenTelemetry (ADOT): the EKS add-on with the ADOT operator, or the OpenTelemetry Helm chart with the ADOT image |
| Credentials | IRSA or EKS Pod Identity for the gateway: `aps:RemoteWrite`, `xray:PutTraceSegments`, `logs:PutLogEvents` |
| Metrics | AMP via `prometheusremotewrite` + `sigv4auth` |
| Traces | X-Ray via `awsxray`, or OTLP to Tempo |
| Logs | CloudWatch Logs via `awscloudwatchlogs`, or Loki |
| Agentless metrics only | the AMP managed collector, if you only need Prometheus scraping |
| Container Insights | the CloudWatch Observability EKS add-on, if you prefer AWS's opinionated version |

## Interview talking points
* Agentless is fine for a demo; a local agent decouples apps from backends; a gateway concentrates connections, processing, sampling and credentials.
* In Kubernetes: DaemonSet for anything node-scoped, one instance for anything cluster-scoped, a gateway for the rest.
* `k8sattributes` adds pod, namespace, deployment and node to every signal: that shared metadata is what lets you jump between metrics, logs and traces.
* Connectors join pipelines: span metrics and service graphs come from traces without touching the application.
* Plan for failure: memory limiter, disk-backed queues sized from the outage you want to survive, retries with a cap.
