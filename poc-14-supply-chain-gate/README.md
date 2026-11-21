# POC 14: Supply-chain deploy gate with break-glass

**Book:** *Platform Engineering at Google* (early release), chapters "Security" (final chapter 15), "Deep Dive: Reliability" (16) and "Shared Fate and Responsibility" (12)

The supply-chain goal from the security chapter: every binary running under a production identity was built from trustworthy source that reflects what the organisation intended. Three properties support it: provenance, integrity and authorisation. The mechanism is **signed attestations** checked by a **deploy gate** (Google calls it binary authorization).

| Path | What it shows |
|---|---|
| `gate.py` | `attest()` signs a statement about an artifact; `evaluate()` is the gate. Policy: trusted builder, expected source repository, minimum SLSA build level, approvals from someone other than the author, a recent scan with no critical findings, and no change marked "bad" |
| `tests/` | Tampered or foreign attestations prove nothing; a laptop build is denied; each policy clause; a bad change blocks every rollout that contains it; break-glass |
| `terraform/` | AWS Signer profile and a Lambda code signing config in `Enforce` mode; ECR with immutable tags and scan-on-push; a break-glass role whose use raises an alert through CloudTrail, EventBridge and SNS |

```bash
python -m pytest -q
```

## Break-glass, done properly
From the reliability chapter. During an outage a responder may need to deploy a fix before review and scanning finish. The gate allows it only with a named person, an incident reference and a reason, and returns an audit record with the violated clauses, an alert, and `review_required`. It is a platform feature with accountability. It is never a silent bypass.

## What SLSA build levels do and don't say
| Level | Requires | Protects against |
|---|---|---|
| L0 | nothing | nothing |
| L1 | provenance exists | mistakes such as building the wrong commit; easily forged |
| L2 | signed provenance from a hosted build platform | tampering after the build |
| L3 | hardened builds: isolated runs, protected signing keys | tampering during the build |

They establish *how and from what* an artifact was built. They say nothing about whether the source or its dependencies are free of flaws. That needs source controls (second-person review, protected branches) and dependency management (CodeArtifact as a curated repository, Inspector for vulnerabilities).

## Shared fate
In the shared-fate chapter's terms this gate is a **guardrail**, not a resource: the safe artifact is the only one that can run. A registry alone is a resource; it helps and enforces nothing.

## Interview talking points
* The gate trusts signatures, not people. Self-approval doesn't count as review.
* Marking one change as bad and having the deploy system refuse every build containing it is cheap, fast mitigation.
* The demo signs with HMAC to stay dependency-free. In production use AWS Signer, KMS asymmetric keys or Sigstore.
