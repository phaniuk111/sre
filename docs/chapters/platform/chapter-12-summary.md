# Platform chapter 12: Shared fate and shared responsibility

*Platform Engineering at Google (early release). Course lesson: `#pe-3`. Code: POC 14. Read: full text, one pass; all figures seen.*

## Summary

In a mature engineering ecosystem, components are connected on purpose. One team’s library update, security patch or shortcut reaches everyone who builds on it. The book calls this **shared fate**. It is what makes fleet-wide improvements possible, and it is also what makes fleet-wide failures possible.

Shared fate without **shared responsibility** ends in a tragedy of the commons. Each team does what is locally sensible, such as adding a risky dependency or ignoring a deprecation notice, and the common ground everyone depends on gets worse.

The whole chapter rests on one equation. **The more an ecosystem limits a developer’s architectural choices, the more liability it can take on for that developer.**

Two of Google’s numbers show the dividend. A central improvement to the C++ memory allocator reached every team at once and saved a significant share of fleet CPU, with no team changing a line. And safe-by-design query APIs produced zero SQL injection in more than a decade in one ecosystem. Neither result came from training thousands of engineers.

## Key ideas

- What shared fate means and why it needs shared responsibility
- The economic trade: architectural choice for platform liability
- Resources, rights and responsibilities: the three Rs of the social contract
- Why guardrails matter even more when AI agents write the code

## What the lesson covers

- The big picture
- The economics: choice for liability
- Governance: from policing to stewardship
- Guardrails: the path of least resistance
- The three Rs
- Why this matters more with AI agents
- Names to recognise

## Terms

shared fate, shared responsibility, resource, guardrail, friction is a directive, large-scale change, Resources, Rights, Responsibilities, permeability, guardian of intent, google3, Green-at-head, Large-scale change (LSC), TrustedSqlString, Across the books

## Interview line

Shared fate means one team’s choices land on everyone, so it has to come with shared responsibility. I frame it as a trade: the more a platform limits your choices, the more liability it can carry for you. I make that explicit with three Rs: what resources the platform gives, what rights the team has, and what responsibilities they keep. The failure I watch for is a team wanting free choice of stack and automatic guarantees at the same time.

## On AWS

AWS publishes its own shared responsibility model, and your internal platform needs one too. A type 2 account gets raw services and a registry (ECR, CodeArtifact) and owns everything else. A type 3 landing zone adds Control Tower guardrails, Config rules, Inspector scan results and Security Hub scores that teams must act on. A type 4 golden path makes the safe choice the only one: Service Control Policies block the risky APIs, CodeArtifact serves only vetted packages, pipelines are the sole route to production, and Lambda code signing or an EKS admission policy refuses unsigned artifacts. Publish a coverage dashboard so every team lead can see their own posture.

## Takeaways

- Limit choice and the platform can carry liability. That is the trade.
- Make it explicit with resources, rights and responsibilities.
- Guardrails must make the safe path the easy one, and that matters most when agents write the code.
