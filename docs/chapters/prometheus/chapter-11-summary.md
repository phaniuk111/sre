# Prometheus chapter 11: Jsonnet and monitoring mixins: configuration you can reuse and override

*Mastering Prometheus (William Hegedus, Packt, 2024). Course lesson: `#m-11`. Code: POC 29 · 5. Read: full text, one pass; all figures seen.*

## Summary

Prometheus configuration is YAML, and lots of it: thousands of lines of scrape config and rules files full of repeated label matchers and annotations. Templating YAML with Jinja or Go templates is fragile because whitespace is syntax. **Jsonnet**, released by Google in 2014 from its internal configuration language, is the Prometheus community’s answer. It is a superset of JSON (any JSON file is valid Jsonnet) with variables, functions, imports and inheritance, and it outputs JSON or YAML.

Two quirks to remember: output keys come out in alphabetical order, and `for` must be quoted because it is a keyword. Render files with `-o` (and `-c` to create directories), YAML with `std.manifestYamlDoc` and `-S`, and many files at once by making the top-level object a map of file names and running with `-m`. Use `jsonnetfmt` and `jsonnet-lint` once a team shares code, and leave real validation to `promtool`: Jsonnet is not a validation language (look at CUE or Nickel if you need one).

Started in 2018 by Tom Wilkie and Frederic Branczyk, the Monitoring Mixins project defines a minimal standard for packaging Prometheus alerts, recording rules and Grafana dashboards together, so that the people who write a piece of software can ship the monitoring for it.

Most users already run one without knowing: kube-prometheus-stack ships the kubernetes-mixin. The author’s complaint is exactly that ignorance, because unknown mixins with wrong selectors give you dashboards and alerts that silently don’t work.

## Key ideas

- Why templating YAML goes wrong and what Jsonnet does instead
- The Jsonnet features you need: locals, hidden fields, self, super and $, imports and +:, comprehensions, functions, errors and asserts
- Rendering YAML and multiple files
- What a monitoring mixin is and how to consume one with jsonnet-bundler

## What the lesson covers

- The big picture
- The language in one table
- Monitoring mixins

## Terms

Jsonnet, Across the books

## Interview line

Jsonnet is JSON with variables, functions, imports and inheritance, which makes large Prometheus and Grafana configs DRY and reviewable. A monitoring mixin packages alerts, recording rules and dashboards with a hidden _config you override; I vendor mixins with jsonnet-bundler, override selectors and disable what I don’t run, render them myself, and validate the output with promtool in CI.

## On AWS

Rendered mixin output goes wherever rules and dashboards go on AWS: alert and recording groups into AMP rule groups namespaces (`aws_prometheus_rule_group_namespace`), dashboards into Amazon Managed Grafana through the grafana Terraform provider. Run the render in CodeBuild or GitHub Actions and commit the output, so reviewers see the generated YAML diff. POC 29 shows the override pattern in Python and the Terraform that publishes dashboards.

## Takeaways

- Jsonnet makes config reusable; render it and validate with promtool.
- A mixin is alerts, rules and dashboards plus a _config you override.
- Know which mixins you already run, and check their selectors.
