# Prometheus chapter 12: CI for Prometheus: promtool, amtool and Pint

*Mastering Prometheus (William Hegedus, Packt, 2024). Course lesson: `#m-12`. Code: POC 23 · 5. Read: full text, one pass; all figures seen.*

## Summary

Prometheus and Alertmanager configuration lives in Git, and code review alone misses things: a typo in a rule, a route added at the bottom that never matches, an alert on a metric that doesn’t exist. CI takes the human error out. The chapter uses GitHub Actions, run locally with `act`, but the commands are the same in any CI system.

Run the Prometheus and Alertmanager checks inside the official container images so the tool versions match production. The author’s advice applies even if you are the only person changing the files: these steps have saved him repeatedly.

Pint comes from Cloudflare, which runs Prometheus at very large scale and didn’t want its monitoring team to be a bottleneck for every other team’s rules. Its key difference from promtool is that it **queries live Prometheus servers** while it lints, so it can say “this alert’s metric has had no series for a week”.

Pint is configured in HCL (`.pint.hcl`), can be silenced per rule with comments such as `# pint disable promql/series(probe_success)`, and in CI it checks only the files a pull request changes and comments on the exact lines. The mixin conventions it enforces are a severity of critical, warning or info, a one-sentence `summary`, and a `description` with templated detail.

## Key ideas

- GitHub Actions vocabulary and running workflows locally with act
- Validating Prometheus config and rules, and running rule unit tests
- Validating Alertmanager config and regression-testing routes
- Linting rules against a live server with Pint, and Pint in pull requests

## What the lesson covers

- The big picture
- Three layers of checks
- Pint

## Terms

queries live Prometheus servers, Across the books, Configuration as code

## Interview line

I put Prometheus config in Git and gate every pull request on promtool check config, check rules and test rules, amtool check-config plus a set of amtool routes tests that pin which receiver each label set reaches, and Pint linting against a live server so rules on non-existent metrics or with missing annotations never merge. That lets teams who aren’t Prometheus experts change alerting safely.

## On AWS

Run the same commands in CodeBuild or GitHub Actions using the official Prometheus and Alertmanager images. For Pint against AMP, put a SigV4 proxy (such as aws-sigv4-proxy) in front of the workspace query endpoint. Deploy rules after the checks pass with `aws amp put-rule-groups-namespace` or Terraform, and the Alertmanager definition with `aws amp put-alert-manager-definition`. POC 23 contains the workflow, a Pint config, rules, unit tests and an Alertmanager config with SNS receivers.

## Takeaways

- promtool for config, rule syntax and rule behaviour; amtool for config and routes.
- Pint lints against live data and comments on pull requests.
- CI is what makes self-service alerting safe.
