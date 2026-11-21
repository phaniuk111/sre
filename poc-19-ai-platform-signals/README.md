# POC 19: AI platform signals — freshness, drift, confidence and a model promotion gate

**Book:** *Platform Engineering at Google* (early release), chapter "AI with Platform Engineering" (chapter 22 of the final book), with the AI sections of the reliability and security chapters

A model endpoint can be up, fast and wrong. The chapter calls that a **silent failure** and asks the platform to treat model and data quality as reliability signals, alongside the four golden signals.

| Function in `ai_signals.py` | Idea from the chapter |
|---|---|
| `freshness()` | a model starts ageing when it ships; a stale fraud model is an incident even while the API is healthy |
| `psi()` and `drift_status()` | data quality: are live inputs still distributed like the training data? The test uses the chapter's example of a model trained on $10–$500 transactions receiving $5,000 ones |
| `confidence_gate()` | probabilistic correctness: refuse low-confidence answers, and report what that costs in availability and saves in wrong answers |
| `model_slo()` | healthy needs infrastructure *and* model health; infrastructure-only health with a bad model is a `silent failure`, and it pages |
| `promotion_gate()` | the supply-chain idea applied to models: signed artifact, recorded lineage (code, data, hyperparameters: the "configured model"), evaluation, guardrail tests, canary |

```bash
python -m pytest -q
```

## On AWS
| Need | Service |
|---|---|
| Standard train-evaluate-register workflow | SageMaker Pipelines |
| Same feature value in training and serving (against training-serving skew) | SageMaker Feature Store |
| Source of truth for versions, lineage and approval | SageMaker Model Registry |
| Drift and quality monitoring | SageMaker Model Monitor, CloudWatch alarms |
| Fault-tolerant long training | managed training with checkpointing; Spot for interruptible jobs |
| Input and output guardrails independent of the model | Bedrock Guardrails |
| Protecting weights in use | Nitro Enclaves, confidential instance types |
| Canary a model version with automatic rollback | endpoint deployment guardrails with CloudWatch alarms |

The other half of the chapter, AI used to run the platform (alert correlation, prediction, assisted and automated response), is covered by POC 11.

## Interview talking points
* Dual mandate: platforms for AI (MLOps) and AI for platforms (AIOps).
* An AI system couples code, data and model configuration. The platform's job is to abstract accelerators, pipelines and training workflows the way servers were abstracted into containers.
* The well-lit path for ML: standard pipelines, a feature store, a model registry.
* Refusing a low-confidence answer is failing closed: a little less availability for fewer confident mistakes.
* Prompt injection can't be prevented by construction yet, because a model has no separate channel for data. Limit what an LLM-driven component may do.
* With agents operating the platform, its role becomes the controls and policies that hold whatever the agent tries.
