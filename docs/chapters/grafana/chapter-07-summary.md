# Grafana chapter 7: Collecting from Kubernetes, AWS, GCP and Azure

*Observability with Grafana (Rob Chapman and Peter Holmes, Packt, 2024). Course lesson: `#g-7`. Code: POC 28 · 5. Read: full text, one pass; all figures seen.*

## Summary

The Helm chart has presets that wire these up with RBAC: `kubernetesAttributes`, `logsCollection`, `kubernetesEvents`, `clusterMetrics`, `kubeletMetrics`, `hostMetrics`. The attributes processor associates incoming data with a pod by trying sources in order: a `k8s.pod.ip` resource attribute, then `k8s.pod.uid`, then the connection’s source IP. It can also copy pod and namespace labels and annotations into attributes, such as an owning team.

## Key ideas

- The OpenTelemetry components for Kubernetes and where each must run
- Kubernetes attributes and how pod association works
- The two ways to see AWS telemetry in Grafana: query in place or ingest
- The GCP and Azure data sources and their query languages
- Performance, cost, limits and security when integrating clouds

## What the lesson covers

- Kubernetes
- AWS: query in place or ingest
- GCP and Azure
- Four considerations

## Interview line

On Kubernetes I run node-scoped receivers (kubelet stats, host metrics, container logs) as a DaemonSet, cluster-scoped ones (cluster metrics, events) as a single instance, and add Kubernetes attributes to everything so signals correlate. For clouds I choose per data set between querying in place, which avoids copies but costs latency and API calls, and ingesting into the same stores as everything else for speed and one query language.

## On AWS

On EKS the ADOT collector add-on or the OpenTelemetry Helm chart provides exactly these receivers; give the cluster-level collector a single replica and the node collector a DaemonSet with IRSA. For AWS services, Amazon Managed Grafana’s CloudWatch data source queries in place; when you want AWS service metrics alongside application metrics in AMP, scrape them with the CloudWatch exporter (YACE) or stream them out with CloudWatch metric streams. Container Insights (the CloudWatch Observability add-on) is AWS’s packaged version. POC 28 is the full architecture with a validator.

## Takeaways

- Node-scoped receivers in a DaemonSet; cluster-scoped receivers in one instance.
- Kubernetes attributes on every signal make correlation possible.
- Query in place or ingest: weigh latency, cost, limits and security per data set.
