import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, ".."))

from gate import attest, evaluate, verify  # noqa: E402

NOW = datetime(2026, 11, 21, 12, 0, tzinfo=timezone.utc)
KEYS = {"codebuild-prod": b"k-build", "review-system": b"k-review", "inspector": b"k-scan", "laptop": b"k-laptop"}
TRUST = {k: v for k, v in KEYS.items() if k != "laptop"}  # the gate does not know the laptop key
POLICY = {"trusted_builders": ["codebuild-prod"], "source_repo": "github.com/acme/orders", "min_slsa_build_level": 3,
          "min_approvals": 1, "max_scan_age_hours": 24, "bad_changes": ["c0ffee1"]}
DIGEST = "sha256:1111"


def good(digest=DIGEST, commits=("abc1234",), critical=0, scanned="2026-11-21T06:00:00+00:00", approvers=("bea",), level=3):
    return [
        attest("provenance", digest, {"source_repo": "github.com/acme/orders", "commits": list(commits), "slsa_build_level": level}, "codebuild-prod", KEYS["codebuild-prod"]),
        attest("review", digest, {"author": "amir", "approvers": list(approvers)}, "review-system", KEYS["review-system"]),
        attest("scan", digest, {"critical": critical, "scanned_at": scanned}, "inspector", KEYS["inspector"]),
    ]


def test_fully_attested_artifact_is_allowed():
    assert evaluate(DIGEST, good(), POLICY, TRUST, NOW)["decision"] == "allow"


def test_tampered_or_foreign_attestations_prove_nothing():
    atts = good()
    atts[0]["predicate"]["slsa_build_level"] = 4  # edited after signing
    assert not verify(atts[0], TRUST)
    out = evaluate(DIGEST, atts, POLICY, TRUST, NOW)
    assert out["decision"] == "deny" and "no valid build provenance" in out["reasons"]
    # attestations for a different artifact are ignored too
    assert evaluate("sha256:2222", good(), POLICY, TRUST, NOW)["decision"] == "deny"


def test_built_on_a_laptop_is_denied():
    atts = good()
    atts[0] = attest("provenance", DIGEST, {"source_repo": "github.com/acme/orders", "commits": ["abc1234"], "slsa_build_level": 3}, "laptop", KEYS["laptop"])
    assert evaluate(DIGEST, atts, POLICY, TRUST, NOW)["decision"] == "deny"


def test_each_policy_clause():
    deny = lambda atts: evaluate(DIGEST, atts, POLICY, TRUST, NOW)["reasons"]  # noqa: E731
    assert any("below 3" in r for r in deny(good(level=2)))
    assert any("critical" in r for r in deny(good(critical=2)))
    assert any("old" in r for r in deny(good(scanned="2026-11-19T06:00:00+00:00")))
    assert any("approval" in r for r in deny(good(approvers=("amir",))))  # self-approval does not count


def test_bad_change_blocks_every_rollout_that_contains_it():
    out = evaluate(DIGEST, good(commits=("abc1234", "c0ffee1")), POLICY, TRUST, NOW)
    assert out["decision"] == "deny" and "c0ffee1" in out["reasons"][0]


def test_break_glass_is_allowed_loud_and_recorded():
    atts = good()[:1]  # emergency fix: built, but review and scan have not finished
    bg = {"who": "oncall-priya", "incident": "INC-4821", "reason": "hotfix for checkout outage"}
    out = evaluate(DIGEST, atts, POLICY, TRUST, NOW, break_glass=bg)
    assert out["decision"] == "allow-break-glass"
    assert out["audit"]["event"] == "BREAK_GLASS_DEPLOY" and out["audit"]["review_required"]
    assert len(out["audit"]["policy_violations"]) == 2
    # no incident reference, no bypass
    assert evaluate(DIGEST, atts, POLICY, TRUST, NOW, break_glass={"who": "x", "reason": "y"})["decision"] == "deny"


def test_break_glass_cannot_ship_a_change_marked_bad():
    bg = {"who": "oncall-priya", "incident": "INC-4821", "reason": "hotfix"}
    out = evaluate(DIGEST, good(commits=("c0ffee1",)), POLICY, TRUST, NOW, break_glass=bg)
    assert out["decision"] == "deny"
