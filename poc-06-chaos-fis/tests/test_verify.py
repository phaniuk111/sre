import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from verify_experiment import verify_az_loss  # noqa: E402


def series(before, during, after, n_before=10, n_during=10, n_after=5):
    return [before] * n_before + [during] * n_during + [after] * n_after


def test_proven_when_fault_happens_and_load_moves():
    r = verify_az_loss(
        {"a": series(100, 0, 100), "b": series(100, 150, 100), "c": series(100, 150, 100)},
        errors=[0] * 25, fault_az="a", fault_start=10, fault_end=20,
    )
    assert r["verdict"] == "PROVEN"


def test_not_proven_when_fault_never_took_effect():
    r = verify_az_loss(
        {"a": series(100, 100, 100), "b": series(100, 100, 100), "c": series(100, 100, 100)},
        errors=[0] * 25, fault_az="a", fault_start=10, fault_end=20,
    )
    assert r["fault_took_effect"] is False and r["verdict"] == "NOT PROVEN"


def test_not_proven_when_users_hurt():
    r = verify_az_loss(
        {"a": series(100, 0, 100), "b": series(100, 100, 100), "c": series(100, 100, 100)},
        errors=[0] * 10 + [20] * 10 + [0] * 5, fault_az="a", fault_start=10, fault_end=20,
    )
    assert r["load_absorbed"] is False and r["within_slo"] is False
