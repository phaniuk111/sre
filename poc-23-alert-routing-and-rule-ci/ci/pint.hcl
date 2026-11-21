# Pint lints rules against a live Prometheus (or an AMP workspace through a SigV4 proxy).
prometheus "prod" {
  uri     = "http://prometheus.monitoring.svc:9090"
  timeout = "30s"
}
ci {
  include    = ["monitoring/rules.*\\.ya?ml"]
  baseBranch = "main"
}
rule {
  match { kind = "alerting" }
  label "severity" {
    severity = "bug"
    value    = "(critical|warning|info)"
    required = true
  }
  annotation "summary" {
    severity = "bug"
    required = true
    value    = "[A-Z][^{.]+.\\."
  }
  annotation "description" {
    severity = "bug"
    required = true
    value    = "[A-Z{].+\\{\\{.*\\}\\}.*\\."
  }
  annotation "runbook_url" {
    severity = "warning"
    required = true
  }
}
