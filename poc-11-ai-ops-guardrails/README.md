# POC 11: Guardrails for AI agents in operations (AIOps on AWS)

**Book chapters:** 21 (How AI Supports SRE), 10 (AI in incident response), 20 (How SRE Supports AI), 19/23 (outlook)

`agent_guardrails.py` is a small safety harness you can put between any LLM agent (e.g. one built on **Amazon Bedrock Agents** or **Amazon Q Developer** operational investigations) and production:

| Principle (book) | Implementation |
|---|---|
| Least privilege, dry run first | every action has `dry_run()`; run the agent with a read-only IAM role until it earns more |
| **Reversible operations**: don't act unless you know how to undo | actions without `undo()` are refused |
| Atomic change: action + validation + auto-rollback in one auditable transaction | `Guardrails.execute` |
| **Progressive authorization** based on evaluated performance | `earned_level()` promotes L1→L2→L3→L4 per *scenario* only after N evaluated cases at a success rate; a policy **ceiling** caps it |
| Transparency | refused unless the proposal has a rationale and evidence |
| Absolute human control | `kill_switch` |
| Human-in-the-loop at L2 | `human_approves` callback (wire to Slack / Incident Manager / SSM `aws:approve`) |

Example reversible AWS actions: **Route 53 ARC zonal shift** (auto-expires) and **Lambda alias rollback**.

```bash
python -m pytest -q
```

## Autonomy levels (ch. 21)
| Level | Monitor | Investigate | Approve | Actuate | Self-direct |
|---|---|---|---|---|---|
| L0 Manual | auto | human | human | human | human |
| L1 Assisted | auto | auto | human | human | human |
| L2 Partial | auto | auto | **human** | auto | human |
| L3 High | auto | auto | auto | auto | human (well-defined scenarios only) |
| L4 Full | auto | auto | auto | auto | auto |

## Where AI helps first (lowest risk → highest)
1. **Detection & triage** (worst-case framing; the risk is only over-escalation). Example: Google's *Detectr* clusters user complaints to find outages that metrics miss.
2. **Outage summaries** for people joining an incident, so the IC isn't interrupted.
3. **Dynamic investigation dashboards** (similar past incidents, playbook graphs, the alert's intent).
4. **Hypothesis generation** with verification steps.
5. **Mitigation is selection, not discovery**: choosing among known safe mitigations is a good first actuation use case. Root cause analysis stays deeper and human-led.

## SRE *for* AI systems (ch. 20) on AWS
* SLO pillars: availability, throughput, latency (**TTFT**, tokens/s), and **quality** (evaluation scores as SLIs, model-as-judge, drift detection).
* Capacity: accelerators are scarce. Watch for utilisation losses (max-utilisation headroom, unrealised demand, N+1, prefill/decode imbalance, load balancing, model fragmentation). On AWS: Bedrock provisioned throughput, SageMaker inference components and multi-model endpoints, EC2 Capacity Blocks for ML.
* Security: model weights are a theft target; supply chain (pretrained models/datasets); agent trust boundaries (MCP); the "lethal trifecta" of private data, untrusted content and external communication.
