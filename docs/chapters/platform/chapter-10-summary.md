# Platform chapter 10: Layers: parts of a platform change at different speeds

*Platform Engineering at Google (early release). Course lesson: `#pe-2`. Read: full text, one pass; all figures seen.*

## Summary

Abstractions give you reusable components. Coupling describes how they connect. Layers add time: which parts of a platform change quickly, which change slowly, and how they influence each other.

That matters because a platform team is always balancing two speeds. Product teams want to ship this week. Governance, security and compliance move on a scale of quarters and years. A layered view tells you which speed belongs where, so the fast parts can move without shaking the slow ones.

Brand’s summary of how fast and slow layers relate is the line to remember. The fast layers learn and propose. The slow layers remember and decide. Shocks are absorbed by the fast layers at the top, and stability comes from each layer respecting the pace of its neighbours.

The chapter follows an internal screenshot tool called SnipIt through every layer. It is a good story to retell because it shows the layers pushing on each other in both directions.

## Key ideas

- What the OSI model, shearing layers and pace layers each teach about platforms
- The six-layer framework for platform engineering, from fastest to slowest
- How the layers push on each other, told through one internal tool

## What the lesson covers

- The big picture
- Three earlier ideas about layers
- Six layers of platform engineering
- One tool, six layers
- Using the layers in practice
- Names to recognise

## Claims and numbers

- Prototype Started in 2009 as a 20% project.
- Product For more than 15 years a tiny team, often one person part-time, kept it running.
- Infrastructure It reached 8 billion screenshots with no major rework, because it ran on App Engine.

## Terms

SnipIt, App Engine, Pace layers, Shearing layers

## Interview line

I think about a platform as layers that change at different speeds. Experiments and products at the top change in days or months. Infrastructure, technical directives, culture and regulation below them change over quarters and years. The fast layers are where we learn; the slow layers are where we keep what we learned. Most platform arguments get easier once you agree which layer a decision belongs to.

## On AWS

A workable mapping: sandbox accounts for experiments (layer 1), product accounts and services (layer 2), the shared platform of landing zone, EKS or ECS base, pipelines and golden-path templates (layer 3), Service Control Policies, Config conformance packs and tagging standards as technical directives (layer 4), and compliance frameworks tracked in Audit Manager and Security Hub standards at the bottom (layer 6). Use AWS Organizations to give the layers different rates of change: sandbox OUs with loose guardrails, production OUs with strict ones.

## Takeaways

- Layers describe rates of change. Match each decision to the layer it belongs on.
- Fast layers learn and propose; slow layers remember and decide.
- Changes at the bottom cascade upward, so plan how a new rule becomes a directive and then a platform feature.
