"""Attestation-based deploy gate with break-glass (binary authorization).

Security chapter: only artifacts built by a trusted builder, from the intended
source, reviewed and scanned, may run under a production identity. Each fact is
a signed *attestation*; the gate trusts signatures, not people.
Reliability chapter: sometimes the gate must be bypassed to restore service.
Break-glass is allowed, loud and recorded. Also: a change marked "bad" blocks
every rollout that contains it.

Signatures here are HMAC-SHA256 with one key per signer, standing in for AWS
Signer / KMS asymmetric keys / Sigstore. The policy logic is the point.
"""
from __future__ import annotations

import hashlib
import hmac
import json
from datetime import datetime, timedelta


def _canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def attest(kind: str, digest: str, predicate: dict, signer: str, key: bytes) -> dict:
    body = {"kind": kind, "subject": digest, "predicate": predicate, "signer": signer}
    return {**body, "signature": hmac.new(key, _canon(body), hashlib.sha256).hexdigest()}


def verify(att: dict, keys: dict) -> bool:
    key = keys.get(att.get("signer"))
    if key is None:
        return False
    body = {k: att[k] for k in ("kind", "subject", "predicate", "signer")}
    return hmac.compare_digest(att.get("signature", ""), hmac.new(key, _canon(body), hashlib.sha256).hexdigest())


def evaluate(digest: str, attestations: list, policy: dict, keys: dict, now: datetime, break_glass: dict | None = None) -> dict:
    """Return {'decision': allow|deny|allow-break-glass, 'reasons': [...], 'notes': [...], 'audit': {...}|None}."""
    reasons, notes, hard = [], [], False
    valid = [a for a in attestations if a.get("subject") == digest and verify(a, keys)]
    dropped = len(attestations) - len(valid)
    if dropped:
        # an invalid attestation proves nothing; it is ignored, and the policy must still be met by the valid ones
        notes.append(f"{dropped} attestation(s) ignored: wrong subject or bad signature")
    by_kind = {a["kind"]: a for a in valid}

    prov = by_kind.get("provenance")
    if not prov:
        reasons.append("no valid build provenance")
    else:
        p = prov["predicate"]
        if prov["signer"] not in policy["trusted_builders"]:
            reasons.append(f"builder {prov['signer']} is not trusted")
        if p.get("source_repo") != policy["source_repo"]:
            reasons.append(f"built from {p.get('source_repo')}, expected {policy['source_repo']}")
        if p.get("slsa_build_level", 0) < policy["min_slsa_build_level"]:
            reasons.append(f"SLSA build level {p.get('slsa_build_level', 0)} is below {policy['min_slsa_build_level']}")
        bad = sorted(set(p.get("commits", [])) & set(policy.get("bad_changes", [])))
        if bad:
            reasons.append(f"contains change(s) marked bad: {', '.join(bad)}")
            hard = True  # a change marked bad is itself an incident mitigation: break-glass cannot override it

    review = by_kind.get("review")
    if not review:
        reasons.append("no valid code-review attestation")
    else:
        r = review["predicate"]
        approvers = set(r.get("approvers", [])) - {r.get("author")}
        if len(approvers) < policy["min_approvals"]:
            reasons.append(f"{len(approvers)} approval(s) from someone other than the author, need {policy['min_approvals']}")

    scan = by_kind.get("scan")
    if not scan:
        reasons.append("no valid vulnerability-scan attestation")
    else:
        s = scan["predicate"]
        if s.get("critical", 1) > 0:
            reasons.append(f"{s.get('critical')} critical vulnerabilities")
        age = now - datetime.fromisoformat(s["scanned_at"])
        if age > timedelta(hours=policy["max_scan_age_hours"]):
            reasons.append(f"scan is {int(age.total_seconds() // 3600)}h old, limit {policy['max_scan_age_hours']}h")

    if not reasons:
        return {"decision": "allow", "reasons": [], "notes": notes, "audit": None}

    if break_glass and not hard:
        missing = [f for f in ("who", "incident", "reason") if not break_glass.get(f)]
        if missing:
            return {"decision": "deny", "reasons": reasons + [f"break-glass refused: missing {', '.join(missing)}"], "notes": notes, "audit": None}
        audit = {"event": "BREAK_GLASS_DEPLOY", "at": now.isoformat(), "artifact": digest, **{k: break_glass[k] for k in ("who", "incident", "reason")},
                 "policy_violations": reasons, "alert": "page security and service owner", "review_required": True}
        return {"decision": "allow-break-glass", "reasons": reasons, "notes": notes, "audit": audit}
    return {"decision": "deny", "reasons": reasons, "notes": notes, "audit": None}

