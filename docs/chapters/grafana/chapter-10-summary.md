# Grafana chapter 10: Automating the observability platform with Helm, Ansible and Terraform

*Observability with Grafana (Rob Chapman and Peter Holmes, Packt, 2024). Course lesson: `#g-10`. Code: POC 28, 29 · 6. Read: full text, one pass; all figures seen.*

## Summary

The config block holds receivers, processors, exporters and **connectors**, which act as an exporter for one pipeline and a receiver for another. The book’s pipeline uses `spanmetrics` (RED metrics from spans, with dimensions such as HTTP method and status) and `servicegraph` (metrics describing calls between services) to feed the metrics pipeline from the traces pipeline. Extensions like `health_check` sit outside pipelines.

A useful Helm habit: split values across files, such as one for the pipeline and one for credentials, and pass several `--values` flags. The last file wins on conflicts and lists are replaced rather than merged, so arrange them carefully.

Running `helm upgrade` for every change means a central system with credentials for every cluster. The **OpenTelemetry Operator** instead defines collectors as Kubernetes resources, which CI can validate and GitOps can pull from Git into each cluster, handles some upgrades, and above all injects **auto-instrumentation** into pods through an annotation. Grafana has an Agent chart and an Agent Operator with resources for metrics and logs. On VMs, the collector ships as .deb, .rpm and .apk packages with its config at `/etc/otelcol/config.yaml`; Grafana maintains an Ansible collection with a `grafana_agent` role.

## Key ideas

- Why automate, and the four systems of an observability platform
- The OpenTelemetry Collector Helm chart: modes, presets, pipelines, connectors, values files
- The OpenTelemetry and Grafana Agent operators, and Ansible on VMs
- The Grafana Cloud API and the Grafana API, through Terraform and Ansible
- Dashboards and alert rules as code

## What the lesson covers

- Why automate
- The collector’s Helm chart
- Operators and VMs
- Two APIs

## Terms

golden path, connectors, OpenTelemetry Operator, auto-instrumentation, service accounts, Across the books, Configuration as code, Collector topology

## Interview line

I treat the observability platform as four systems: production owned by app teams, collection and storage by the platform team, visualisation shared. Collectors deploy through Helm or the OpenTelemetry Operator with node-scoped presets in a DaemonSet and cluster-scoped ones in a single replica; connectors like spanmetrics and servicegraph derive metrics from traces. Grafana itself, access policies, folders, dashboards and alert rules are all Terraform, with dashboards owned by teams in their own folders.

## On AWS

Terraform manages the AWS side (AMP workspaces, rule groups namespaces, Alertmanager definitions, the Amazon Managed Grafana workspace and its IAM role) and the grafana provider manages what is inside the workspace. On EKS, the ADOT add-on installs the OpenTelemetry Operator, which can inject auto-instrumentation into pods by annotation. Store collector tokens and Grafana service-account tokens in AWS Secrets Manager. POC 28 has the collector configs; POC 29 has the AMG Terraform with dashboards, folder permissions and an alert rule group.

## Takeaways

- Four systems, different owners: automate each where it lives.
- Collector modes and presets must match scope; connectors derive metrics from traces.
- Grafana Cloud and Grafana APIs through Terraform; teams own dashboards in their folders.
