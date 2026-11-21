"""Safe deployment: blueprints and conformance verification.

Security chapter, "Safe Deployment": nobody can keep every permission, network
rule and option in their head, and a misconfiguration is as dangerous as a code
bug. So express the invariants once and enforce them mechanically.

  blueprint     a pre-validated template for a common pattern. Teams fill in a
                few parameters and inherit a reviewed configuration.
  conformance   continuously compare what is deployed with the blueprint it
                claims to come from. Report drift, weakened invariants, and
                services pinned to an outdated blueprint version.

This is the deployment-time analogue of a type checker. POC 10 covers free-form
policy-as-code with exemptions; this one covers the template side.

AWS: blueprints are CDK constructs, Terraform modules or Service Catalog
products; conformance is AWS Config rules / CloudFormation drift detection /
cfn-guard in the pipeline; fleet posture rolls up in Security Hub.
"""
from __future__ import annotations

import copy

# name -> version -> (defaults, locked keys, allowed parameters)
BLUEPRINTS = {
    "external-web-service": {
        2: {
            "defaults": {
                "tls": {"min_version": "1.2", "redirect_http": True, "hsts": True},
                "network": {"public_ingress": "load-balancer-only", "egress": "allowlist"},
                "runtime": {"run_as_root": False, "read_only_fs": True, "cpu_limit": "500m", "memory_limit": "512Mi"},
                "placement": {"zones": 3},
                "identity": {"role": "least-privilege", "long_lived_keys": False},
                "observability": {"golden_signals": True, "tracing": True},
                "data": {"backups": True, "deletion_protection": True},
            },
            # invariants: a team may not change these, whatever the reason
            "locked": ["tls.min_version", "tls.redirect_http", "network.public_ingress", "runtime.run_as_root",
                       "identity.long_lived_keys", "data.deletion_protection"],
            # ordinary knobs
            "params": ["runtime.cpu_limit", "runtime.memory_limit", "placement.zones"],
        },
        3: None,  # filled in below: v3 = v2 with TLS 1.3 (a new policy propagated by updating the blueprint)
    }
}
_v3 = copy.deepcopy(BLUEPRINTS["external-web-service"][2])
_v3["defaults"]["tls"]["min_version"] = "1.3"
BLUEPRINTS["external-web-service"][3] = _v3

MIN_ZONES = 2  # even a tunable knob has a floor


def _get(cfg, dotted):
    for part in dotted.split("."):
        cfg = cfg[part]
    return cfg


def _set(cfg, dotted, value):
    parts = dotted.split(".")
    for part in parts[:-1]:
        cfg = cfg[part]
    cfg[parts[-1]] = value


def _flatten(cfg, prefix=""):
    for k, v in cfg.items():
        key = f"{prefix}{k}"
        if isinstance(v, dict):
            yield from _flatten(v, key + ".")
        else:
            yield key, v


def render(name: str, version: int, params: dict | None = None) -> dict:
    """Instantiate a blueprint. Only declared parameters may be set."""
    bp = BLUEPRINTS[name][version]
    cfg = copy.deepcopy(bp["defaults"])
    for key, value in (params or {}).items():
        if key not in bp["params"]:
            kind = "locked by the blueprint" if key in bp["locked"] else "not a parameter"
            raise ValueError(f"{key} is {kind}")
        if key == "placement.zones" and value < MIN_ZONES:
            raise ValueError(f"placement.zones must be at least {MIN_ZONES}")
        _set(cfg, key, value)
    cfg["blueprint"] = {"name": name, "version": version}
    return cfg


def latest(name: str) -> int:
    return max(BLUEPRINTS[name])


def conformance(service: str, deployed: dict) -> list:
    """Findings for one deployed configuration: [(severity, service, message)]."""
    meta = deployed.get("blueprint")
    if not meta:
        return [("block", service, "not created from a blueprint: no reviewed baseline to compare against")]
    name, version = meta["name"], meta["version"]
    bp = BLUEPRINTS[name][version]
    expected = dict(_flatten(bp["defaults"]))
    actual = dict(_flatten({k: v for k, v in deployed.items() if k != "blueprint"}))
    out = []
    for key, want in sorted(expected.items()):
        got = actual.get(key, "<missing>")
        if got == want:
            continue
        if key in bp["locked"]:
            out.append(("block", service, f"invariant weakened: {key} is {got!r}, blueprint requires {want!r}"))
        elif key in bp["params"]:
            if key == "placement.zones" and got != "<missing>" and got < MIN_ZONES:
                out.append(("block", service, f"placement.zones is {got}, below the floor of {MIN_ZONES}"))
        else:
            out.append(("warn", service, f"drift: {key} is {got!r}, blueprint default is {want!r}"))
    for key in sorted(set(actual) - set(expected)):
        out.append(("warn", service, f"drift: {key} is set but is not part of the blueprint"))
    if version < latest(name):
        out.append(("warn", service, f"pinned to {name} v{version}; v{latest(name)} is current"))
    return out


def fleet_report(fleet: dict) -> dict:
    findings = [f for svc, cfg in sorted(fleet.items()) for f in conformance(svc, cfg)]
    clean = [svc for svc in fleet if not any(f[1] == svc for f in findings)]
    return {
        "block": [f for f in findings if f[0] == "block"],
        "warn": [f for f in findings if f[0] == "warn"],
        "conformant_share": round(len(clean) / len(fleet), 2) if fleet else None,
    }
