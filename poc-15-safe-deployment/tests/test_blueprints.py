import copy
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from blueprints import conformance, fleet_report, latest, render  # noqa: E402

BP = "external-web-service"


def test_render_gives_a_reviewed_configuration():
    cfg = render(BP, 3, {"runtime.memory_limit": "1Gi"})
    assert cfg["tls"]["min_version"] == "1.3" and cfg["runtime"]["run_as_root"] is False
    assert cfg["runtime"]["memory_limit"] == "1Gi" and cfg["placement"]["zones"] == 3
    assert conformance("orders", cfg) == []


def test_locked_invariants_cannot_be_parameterised():
    with pytest.raises(ValueError, match="locked"):
        render(BP, 3, {"runtime.run_as_root": True})
    with pytest.raises(ValueError, match="not a parameter"):
        render(BP, 3, {"observability.tracing": False})
    with pytest.raises(ValueError, match="at least 2"):
        render(BP, 3, {"placement.zones": 1})


def test_drift_after_deploy_is_detected():
    cfg = render(BP, 3)
    cfg["network"]["public_ingress"] = "open"       # someone "fixed" connectivity by hand
    cfg["observability"]["tracing"] = False         # and switched tracing off
    cfg["runtime"]["debug_port"] = 9229             # and added something of their own
    found = conformance("orders", cfg)
    assert ("block", "orders", "invariant weakened: network.public_ingress is 'open', blueprint requires 'load-balancer-only'") in found
    assert any(f[0] == "warn" and "observability.tracing" in f[2] for f in found)
    assert any("runtime.debug_port" in f[2] for f in found)


def test_blueprint_update_surfaces_services_left_behind():
    old = render(BP, 2)
    assert latest(BP) == 3
    assert conformance("legacy", old) == [("warn", "legacy", "pinned to external-web-service v2; v3 is current")]


def test_fleet_report():
    drifted = render(BP, 3)
    drifted["tls"]["redirect_http"] = False
    handmade = copy.deepcopy(render(BP, 3))
    del handmade["blueprint"]
    rep = fleet_report({"orders": render(BP, 3), "pricing": render(BP, 3, {"placement.zones": 2}), "web": drifted, "old-tool": handmade})
    assert rep["conformant_share"] == 0.5
    assert {f[1] for f in rep["block"]} == {"web", "old-tool"}
