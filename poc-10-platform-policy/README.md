# POC 10: Platform engineering: policy-as-code, golden paths and exemptions

**Book chapters:** 18 (Platform Engineering in SRE), 23 ("shift left turns into shift down"), Foreword (reliability by default / Convergence)

| Path | What |
|---|---|
| `policy_check.py` | Reads a service catalog (what an IDP like Backstage or AWS Service Catalog AppRegistry knows) and applies platform policies at **advise / warn / block** levels. Greenfield services are held to a stricter bar; brownfield services get **legible, time-boxed exemptions** (policy, services, bug, `valid_until`, reason). Exits non-zero on blockers, so it can gate CI. |
| `guard/reliability.guard` | The same policies as **CloudFormation Guard** rules at template-review time: DynamoDB PITR + deletion protection, multi-AZ ASGs, Multi-AZ RDS, progressive CodeDeploy with rollback |

```bash
python policy_check.py examples/catalog.yaml examples/exemptions.yaml
python -m pytest -q
```

## Book idea → AWS mechanism
| Book | AWS |
|---|---|
| Golden path ("vending machine") | **AWS Service Catalog** products, **Proton**/Backstage templates, CDK constructs with reliability defaults |
| Guardrails (errors that block unsafe behaviour) | **SCPs** / Resource Control Policies, Control Tower **preventive** controls, cfn-guard in CI |
| Warnings / introspection (legibility of risk) | **AWS Config** rules & conformance packs, Control Tower **detective** controls, Security Hub, Resilience Hub assessments |
| Remediation | Config auto-remediation with SSM Automation |
| Exemptions / escape hatches | Tag-scoped exceptions in SCPs, Config rule scoping, plus a register like `exemptions.yaml` |
| Convergence: one system per class of reliability practice | One deployment system (CodePipeline/CodeDeploy), one SLO tool, one observability SDK (ADOT) |

## Interview talking points
* Platform as product: personas are developers (adoption, velocity), operators (cognitive load, toil) and the business.
* Make the right way the **easy** way, through incentives and strong defaults, not threats. *"Change the game so the good outcome is the rational one."*
* Learn from **desire paths**: when engineers route around the platform, ask why.
* **Shift down:** put reliability into shared frameworks and managed services so every team doesn't have to become an expert in everything.
* Cynefin: the platform's job is to move production problems from Chaotic/Complex towards Complicated/Clear.
