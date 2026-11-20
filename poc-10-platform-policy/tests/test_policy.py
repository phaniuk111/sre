import os
import sys
from datetime import date

import yaml

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, ".."))

from policy_check import evaluate  # noqa: E402


def load(name):
    with open(os.path.join(HERE, "..", "examples", name)) as f:
        return yaml.safe_load(f)


def test_policy_report():
    rep = evaluate(load("catalog.yaml"), load("exemptions.yaml"), date(2026, 11, 20))
    blocks = {(f["service"], f["policy"]) for f in rep["block"]}
    exempt = {(f["service"], f["policy"]) for f in rep["exempt"]}
    # valid exemption -> exempt, expired exemption -> blocking again
    assert ("legacy-billing", "location/multi-az") in exempt
    assert ("legacy-billing", "release/progressive") in blocks
    assert ("legacy-billing", "alerting/routes-to-active-team") in blocks
    # greenfield service: a 'warn' policy becomes blocking
    assert ("new-recs", "slo/defined") in blocks
    # compliant service has no findings
    assert not any(f["service"] == "checkout" for lvl in rep.values() for f in lvl)
