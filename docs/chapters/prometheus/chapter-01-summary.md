# Prometheus chapter 1: Observability, the Prometheus architecture, and deploying it

*Mastering Prometheus (William Hegedus, Packt, 2024). Course lesson: `#m-1`. Code: POC 22 · 6. Read: full text, one pass; all figures seen; lesson covers chapters 1–2.*

## Summary

Monitoring means checking for conditions you decided in advance were bad. Observability means being able to ask a new question of a running system and get an answer without shipping new code. Metrics, logs and traces are the three classic signals; metrics are the cheapest to keep and the fastest to query, which is why they drive dashboards and alerts.

Prometheus is a metrics system with four ideas that set it apart. It **pulls** metrics over HTTP rather than waiting for them to be pushed. Every series is identified by **labels**, so you slice data by any dimension at query time. It has its own query language, **PromQL**. And it **discovers** what to scrape from Kubernetes, clouds and other sources, so targets come and go without config changes.

Two things in that picture matter later. First, **Alertmanager is a separate program**: Prometheus decides that an alert is firing, Alertmanager decides who hears about it. Second, everything leaves through the same storage, so a slow query and a heavy rule both compete with ingestion for memory and CPU.

The book deploys everything with the **kube-prometheus-stack** Helm chart, which installs the Prometheus Operator, a Prometheus server, Alertmanager, Grafana, node exporter, kube-state-metrics and a large set of ready-made rules and dashboards (the kubernetes-mixin, which lesson 11 explains).

## Key ideas

- Monitoring versus observability, and where metrics fit among the signals
- What makes Prometheus different: pull, labels, PromQL, service discovery
- The components inside one Prometheus server and how data moves between them
- How kube-prometheus-stack and the Prometheus Operator deploy it on Kubernetes

## What the lesson covers

- The big picture
- Why pull?
- Inside one server
- Deploying it on Kubernetes
- Small things worth knowing

## Terms

pulls, labels, PromQL, discovers, kube-prometheus-stack, Across the books, Observability

## Interview line

Prometheus pulls metrics over HTTP from targets it discovers, stores each series by name and labels in a local time-series database, evaluates recording and alerting rules on a schedule, and hands firing alerts to a separate Alertmanager. On Kubernetes I deploy it with the Prometheus Operator so teams declare ServiceMonitors and PrometheusRules in their own namespaces instead of editing a central config.

## On AWS

On EKS you have three options. Self-managed: kube-prometheus-stack on EKS with gp3 volumes for the TSDB. Hybrid: keep Prometheus (or Prometheus in agent mode, or the ADOT collector) as the scraper and remote-write to Amazon Managed Service for Prometheus, which stores, replicates and serves PromQL. Fully managed: the AMP managed collector scrapes the cluster agentlessly from a Prometheus-format scrape config. Amazon Managed Grafana reads AMP with SigV4. For alerting, AMP has rule groups namespaces and a managed Alertmanager whose receivers are SNS topics.

## Takeaways

- Pull, labels, PromQL and service discovery are what make Prometheus different.
- Prometheus decides alerts fire; Alertmanager decides who hears.
- On Kubernetes, the Operator turns ServiceMonitors and PrometheusRules into config; on AWS, AMP can take over storage and rules.
