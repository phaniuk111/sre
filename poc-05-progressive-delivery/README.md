# POC 05: Progressive delivery, canaries and config safety on AWS

**Book chapters:** 14 (Testing: canaries, config tests, VOIS), 17 (change management), 13 (regional rollouts), 9 (CUJ change supervision)

| Path | What |
|---|---|
| `terraform/` | Lambda published versions + `live` alias, **CodeDeploy** `LambdaCanary10Percent5Minutes` with **alarm-based auto rollback**; **AppConfig** feature flags with a linear deployment strategy, bake time and the same alarm as rollback monitor |
| `src/handler.py` | Reads flags through the AppConfig extension and falls back to an **explicit safe default** if config is unavailable; returns `x-served-by-version` |
| `canary_analysis.py` | Canary vs control judgment: two-proportion z-test on errors, p95 ratio + Mann-Whitney on latency, minimum-traffic guard → PASS / FAIL / INCONCLUSIVE |
| `appspec.yml` | Wires the judge in as an `AfterAllowTraffic` hook |

```bash
python -m pytest -q
cd terraform && terraform apply -var appconfig_extension_layer_arn=<arn for your region>
```

## Concept map
| Book | AWS |
|---|---|
| Progressive rollout across failure domains | CodeDeploy canary/linear; for multi-Region, deploy Region by Region (CodePipeline stages with waits) |
| Change supervision | CloudWatch alarms attached to the deployment group / AppConfig environment monitor |
| Change concurrency: one change at a time | Separate code (CodeDeploy) and config (AppConfig) deployments; don't bundle schema + code |
| **VOIS** config invariants | Versioned (hosted config versions), Observable (AppConfig deployment events), Independent (no code deploy needed), Safe (validators + safe defaults in code) |
| Feature flags & emergency stop | AppConfig feature flags; `StopDeployment` rolls back immediately |
| Risk tolerance / change freezes | CodePipeline disabled transitions, AWS Organizations SCPs during peak periods, Change Calendar (SSM) |
| Client-focused change supervision | Clients emit metrics keyed by `x-served-by-version`, so a backend canary that hurts *callers* is caught |

## Interview talking points
* Most outages are triggered by **changes**, so make change small, gradual, supervised and reversible.
* Compare the canary with a **control receiving the same traffic at the same time**, not with yesterday.
* A canary that receives no traffic must **not** pass. Treat it as inconclusive or as a failure.
* Config is as dangerous as code (often more so, because it changes faster and skips review). Test it at three levels: syntax, semantic, dynamic.
* Rollback is the safest generic mitigation, unless the new version has already written data the old version can't read. Use expand/contract schema migrations to keep rollback possible.
