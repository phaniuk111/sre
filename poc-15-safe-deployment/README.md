# POC 15: Safe deployment — blueprints and conformance verification

**Book:** *Platform Engineering at Google* (early release), chapter "Security", section "Safe Deployment" (chapter 15 of the final book)

Safe Coding makes vulnerable code impossible to write. Safe Deployment applies the same idea to configuration: express invariants explicitly and enforce them mechanically, because no operator can keep every permission, network rule and option in mind.

| Idea from the chapter | In `blueprints.py` |
|---|---|
| **Configuration as code** | Configurations are data, rendered and checked by code |
| **Blueprints**: pre-validated templates for common patterns | `render("external-web-service", version, params)` returns a reviewed configuration: TLS, load-balancer-only ingress, non-root, resource limits, three zones, least-privilege identity, golden signals, backups |
| Invariants a team can't change | `locked` keys. Trying to set one raises an error at render time |
| Ordinary knobs, with floors | `params` (CPU, memory, zones; zones can't go below 2) |
| **Leverage when requirements change** | Version 3 raises the TLS floor. Services still on version 2 show up in the report |
| **Conformance verification** | `conformance()` compares a deployed configuration with its blueprint: weakened invariants block, other drift warns, hand-made configurations have no baseline |
| A fleet posture number | `fleet_report()["conformant_share"]` |

```bash
python -m pytest -q
```

## On AWS
* Blueprints: CDK constructs, Terraform modules or Service Catalog products, published by the platform team.
* Pre-deploy checks: CloudFormation Guard or OPA in the pipeline (see POC 10 for rules with exemptions).
* Drift: AWS Config rules and CloudFormation drift detection. Organisation-wide invariants: Service Control Policies.
* Posture: Security Hub with Config, which the chapter names as the AWS equivalent of Google's Security Command Center.

## Interview talking points
* A blueprint is leverage twice: teams start from a reviewed configuration, and one update propagates a new policy.
* Static templates aren't enough. Configurations drift and some services never used the template, so verify continuously.
* Rules such as "no container runs as root" are the deployment-time version of a type check.
* Measuring the *presence* of structural guarantees gives evidence of the *absence* of a class of defect. Scanners can only report problems they happen to find.
