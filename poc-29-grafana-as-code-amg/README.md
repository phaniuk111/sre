# POC 29: dashboards and alerts as code on Amazon Managed Grafana

**Books:** *Observability with Grafana* chapters 8 (dashboard purpose, layout, variables, annotations, folders and permissions, the Steven case study), 10 (Terraform for Grafana Cloud and Grafana, dashboards and rule groups as code) and 11 (RBAC: teams own their folders); *Mastering Prometheus* chapter 11 (monitoring mixins and `+:` overrides)

`dashboards_as_code.py` generates a golden-signals dashboard the way chapter 8 designs one for Steven the service manager: the four signals as Stats with sparklines across the top, most important first; a full-width breakdown; then one **collapsed** row per owning team that opens with a text panel saying how to reach them. Everything is parameterised with variables and the `$__rate_interval` window, and deployments appear as annotations.

The linter turns the chapter's advice into checks: dashboard and panel descriptions, units, no hard-coded `namespace`/`service` when a variable exists, `$__rate_interval` in `rate()`, collapsed detail rows, a relative default time range, deployment annotations, a panel budget.

`merge()` is the Jsonnet idea without Jsonnet: nested config merges, `name+` appends to a list, everything else replaces; the test reproduces the book's `monitoringStack+: ['thanos']` example and overrides the latency SLO the way a mixin's `_config` is overridden.

`terraform/amg.tf` creates the Amazon Managed Grafana workspace (IAM Identity Center sign-in, AMP/CloudWatch/X-Ray data sources), adds the AMP data source with SigV4, a folder whose team gets Edit and everyone else View, every JSON file in `dashboards/`, and a Grafana-managed alert rule group.

```bash
python -c "import dashboards_as_code as D, json; print(json.dumps(D.golden_signals_dashboard('checkout'))[:200])"
python -m pytest -q
```

## On AWS
| Need | Service |
|---|---|
| Hosted Grafana | Amazon Managed Grafana; sign-in through IAM Identity Center or SAML |
| Metrics | AMP data source with SigV4 (role on the workspace has `AmazonPrometheusQueryAccess`) |
| AWS service metrics and logs | CloudWatch data source (query-time; nothing copied) |
| Traces | X-Ray data source, or Tempo |
| Dashboards and alerts in Git | the `grafana` Terraform provider against the workspace endpoint; a service account token for CI |
| Who can edit what | folder permissions per team, Viewer for everyone else; Grafana teams synced from Identity Center groups |

## Interview talking points
* Start every dashboard with its audience, their question and where they will look at it (wall screen, laptop, PDF).
* Key indicators first, left to right; detail in collapsed rows (collapsed rows don't run their queries).
* Variables instead of hard-coded values, relative time ranges, `$__rate_interval`, units and descriptions on every panel.
* Deployment annotations turn "what changed?" into a glance.
* Teams own their dashboards in their folder through IaC; the platform team owns the Grafana instance, the data sources and the guard rails.
