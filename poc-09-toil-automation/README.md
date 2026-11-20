# POC 09: Toil measurement & safe automation on AWS

**Book chapter:** 13 (Automation and Tooling, Toil), plus 9 (automatic investigation) and 21 (autonomy levels)

| Path | What |
|---|---|
| `toil_report.py` | Turns a ticket/page export into: ops load % of team capacity (the 50% **threshold**), % unactionable alerts, top toil **classes**, and two automation orderings: ROI-first vs **snowball / fastest-first** |
| `runbooks/generic-mitigation.yaml` | **SSM Automation** document that collects common diagnostics on every incident (recent CodeDeploy & AppConfig deployments, alarms firing) and can then **drain an AZ** with a Route 53 ARC zonal shift, behind an `aws:approve` step. The shift is reversible and auto-expires. |

```bash
python toil_report.py examples/tickets.csv
python -m pytest -q
aws ssm create-document --name SRE-GenericMitigation-Diagnose --document-type Automation \
    --document-format YAML --content file://runbooks/generic-mitigation.yaml
```

## Decision framework for automating (ch. 13)
* **Quantifiable:** minutes saved per year vs build *and maintenance* cost. Engineers routinely underestimate the cost of adapting automation as the system changes.
* **Non-quantifiable:** strategic speed and consistency, the cost of mitigating the automation's own risks, ambiguous signals (automation is good at deterministic work), and the human annoyance of the toil.
* **Ironies of automation (Bainbridge):** automation creates new work (monitoring and repairing it), lets operator skills fade, and leaves the hardest cases to humans. Keep humans practised (Wheel of Misfortune) and keep the automation observable.
* **Pitfalls:** dangerous automation without rate limits or safety checks; automation that surprises operators; building on a broken foundation (auto-restarting a memory leak instead of fixing it); automating a moving target.
* **Don't stop at 90%.** Partial automation can *add* cognitive load.

## When toil is acceptable
To mitigate an incident, to learn a process before automating it, or where human judgment is required (e.g. starting a data recovery). It is not acceptable when it fills a product gap, grows with the system, or only exists because access was restricted. For the last case, build single-purpose, least-privilege tools.
