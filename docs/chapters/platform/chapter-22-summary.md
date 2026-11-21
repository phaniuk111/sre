# Platform chapter 22: AI and platform engineering: a dual mandate

*Platform Engineering at Google (early release). Course lesson: `#pe-9`. Code: POC 19. Read: full text, one pass; all figures seen.*

## Summary

- **Platforms for AI**: Infrastructure, abstractions and workflows for the whole life of a model. Usually called MLOps.
- **AI for platforms**: Using AI to improve how the platform itself is designed, automated, observed and run. Usually called AIOps.

The two feed each other. A well-abstracted platform is what lets an organisation use AI at scale, and the intelligence that produces is then turned on the platform. The chapter is written from Google’s position: the same investments that made Search and Gmail possible, in cluster management, distributed storage and custom accelerators, are what made training very large models possible.

An AI system is more than code. It is code, data and model configuration bound together, and that three-way coupling multiplies complexity. In ordinary software a person writes the logic. In machine learning the logic is learned from data.

The chapter’s instruction is the **abstraction imperative**: servers were abstracted into virtual machines and containers to free application developers, and now accelerators, data pipelines and training workflows must be abstracted to free ML engineers.

One term to know: the **configured model** is the complete set of code, data and hyperparameters. An experiment can be reproduced only if all three are captured.

## Key ideas

- Platforms for AI and AI for platforms
- Why the ML lifecycle needs its own abstractions and well-lit path
- How efficiency, reliability and security change for AI workloads
- The stages of AI in operations, up to agentic platforms

## What the lesson covers

- The big picture
- Why AI needs its own platform
- The quality attributes, applied to AI
- AI for platforms

## Terms

Platforms for AI, AI for platforms, A naming point, abstraction imperative, Data, Experiment, Train, Productionise, Serve, Monitor, configured model, Standard pipelines, A central feature store, A model registry, Supply chain, Protecting the weights

## Interview line

There are two jobs. One is building the platform AI teams need: hide the accelerators, give them standard pipelines, a feature store and a model registry, and treat freshness, drift and confidence as reliability signals, because a model can return a 200 and be wrong. The other is using AI to run the platform: correlate alerts, predict problems, assist responders and, with guardrails, act. In both, the platform’s part is the controls that hold regardless of what a model or agent does.

## On AWS

For the ML path: SageMaker Pipelines for standard workflows, Feature Store against training-serving skew, Model Registry with approval status as the source of truth, managed training with checkpointing and Spot for fault-tolerant jobs, and Model Monitor for data and quality drift. For generative workloads, Bedrock Guardrails act as the input and output gateway independent of the model, and Nitro Enclaves or confidential instances protect weights in use. Sign model artifacts and gate deployment on the signature, as with any other binary. For AIOps: CloudWatch anomaly detection and investigations, DevOps Guru for correlated insights, predictive scaling, and agents whose permissions are bounded by IAM and Service Control Policies so the limits hold whatever the agent decides.

## Takeaways

- Two mandates: build platforms for AI, and use AI to run platforms.
- A model can be up and wrong. Monitor freshness, drift and confidence.
- Abstract the hardware; give ML engineers pipelines, a feature store and a registry.
- With agents operating, the platform’s job is the controls that always hold.
