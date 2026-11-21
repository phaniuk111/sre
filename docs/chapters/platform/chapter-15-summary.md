# Platform chapter 15: Security: if it isn’t secure, it shouldn’t compile

*Platform Engineering at Google (early release). Course lesson: `#pe-5`. Code: POC 13 · 14 · 15. Read: full text, one pass; all figures seen.*

## Summary

The same kinds of vulnerability top the incident reports year after year: memory corruption, injection, broken access control. The industry’s list of the most dangerous weaknesses has barely changed in a long time, despite decades of secure-coding training.

This chapter’s diagnosis is that the problem is structural. We ask every developer to avoid every known mistake at every call site, forever, and we check afterwards with tools that can only find some of what went wrong. People make mistakes because the systems they work in make mistakes easy. So do AI coding tools, which now write more code than humans can review.

The platform answer: move security out of each developer’s head and into the things all code is built from, so whole classes of bug can’t be written.

That last point defines the goal. **Assurance** is confidence that a requirement holds for every behaviour of the program. **Continuous assurance** is keeping that confidence for every version you ship.

## Key ideas

- Why training and scanning can’t deliver assurance, however much you do
- Security as an emergent property, application archetypes and invariants
- Safe Coding: risky operations, safe abstractions and the two ways to build one
- Supply chain (SLSA, attestations), safe deployment and security observability
- What AI changes, and why prompt injection resists these techniques

## What the lesson covers

- The big picture
- Why the usual approaches fall short
- Shift down: the platform as a security control
- Safe Coding
- Memory safety
- The software supply chain
- Identity and insiders
- Web security: about twenty controls
- Safe deployment
- Measuring the guarantees
- Security with AI in the loop
- Assembling your own

## Claims and numbers

- Existing code is the expensive part, and the Android numbers show a way through: writing new code in memory-safe languages took memory-safety bugs from over 70% of the total to 24% in six years, without rewriting the old code.
- Between 60% and 70% of high-severity vulnerabilities in large C and C++ codebases are memory-safety bugs.

## Terms

What “platform” means here, Testing can’t show absence, Assurance, Continuous assurance, Initial and sustained velocity, If the platform doesn’t, Confine what is left, containment, archetype, invariant, risky operation, safe abstraction, Build visibility rules, Narrow static checks, Conformance rules, Ergonomics

## Interview line

I’d stop treating developers as the last line of defence. Training and scanners find some bugs and can’t show that none remain. I’d shift security down: pick the invariants that matter for our kind of application, and enforce them in the platform with safe APIs that make the vulnerable code impossible to write, signed builds with a deploy gate, and policy checks on configuration. Then I’d measure adoption of those guarantees, because that is evidence that whole classes of bug are absent.

## On AWS

Safe Coding is language-level, so it travels: a typed query wrapper over the RDS Data API or your database driver, plus a CI rule that bans raw query calls outside that module. Supply chain: CodeBuild or GitHub Actions producing signed provenance, AWS Signer with ECR image signing, and a gate at deploy time (Lambda code signing configurations, or Kyverno or Gatekeeper on EKS verifying signatures). Dependencies: CodeArtifact as the curated repository and Inspector for vulnerabilities. Identity: IAM Identity Center for people, IAM roles and EKS Pod Identity for workloads, VPC Lattice or a mesh for mutual TLS, and Amazon Verified Permissions for fine-grained, relationship-style authorisation. Web controls: terminate TLS centrally at CloudFront or ALB with ACM, and set HSTS, CSP and framing headers once with a CloudFront response headers policy. Safe deployment: CloudFormation Guard or OPA in the pipeline, Service Control Policies, and Config rules for drift. Posture: Security Hub with Config, which the chapter itself names as the AWS equivalent of Google’s Security Command Center.

## Takeaways

- Developers and AI both make mistakes. Design so the important ones can’t be made.
- A safe abstraction moves risk from thousands of call sites into one module an expert can review.
- Provenance, a deploy gate and policy checks carry the same idea into build and deployment.
- Measure adoption of the guarantees: it is evidence that a class of bug is absent.
