"""Verify an AZ-loss experiment actually proved what it claims (ch. 21
'Verifying Resilience'): compare steady state with the fault window.

For "the system tolerates the loss of a whole AZ" the evidence must show:
  1. traffic served by the impaired AZ dropped to ~0 (the fault really happened)
  2. the other AZs absorbed the load (their share rose accordingly)
  3. the user-facing SLI stayed within SLO during the fault window
A test that passed only because the fault never took effect is worse than no
test: it gives false confidence.

Input: per-minute request counts by AZ and error counts. In AWS, pull these from
the ALB `RequestCount` metric with the `AvailabilityZone` dimension.
"""
from __future__ import annotations

from typing import Dict, List


def verify_az_loss(
    requests_by_az: Dict[str, List[int]],
    errors: List[int],
    fault_az: str,
    fault_start: int,
    fault_end: int,
    slo: float = 0.999,
    absorbed_tolerance: float = 0.9,
) -> Dict[str, object]:
    minutes = len(errors)
    before = range(0, fault_start)
    during = range(fault_start, fault_end)

    def total(az: str, window) -> int:
        return sum(requests_by_az[az][i] for i in window)

    def all_total(window) -> int:
        return sum(total(az, window) for az in requests_by_az)

    fault_share_during = total(fault_az, during) / max(1, all_total(during))
    others = [az for az in requests_by_az if az != fault_az]
    others_rate_before = sum(total(az, before) for az in others) / max(1, len(before))
    others_rate_during = sum(total(az, during) for az in others) / max(1, len(during))
    expected_total_rate = all_total(before) / max(1, len(before))
    absorbed = others_rate_during >= absorbed_tolerance * expected_total_rate
    err_during = sum(errors[i] for i in during)
    availability = 1 - err_during / max(1, all_total(during))
    return {
        "fault_took_effect": fault_share_during < 0.01,
        "load_absorbed": absorbed,
        "others_rate_before": round(others_rate_before, 1),
        "others_rate_during": round(others_rate_during, 1),
        "availability_during": round(availability, 5),
        "within_slo": availability >= slo,
        "verdict": "PROVEN" if fault_share_during < 0.01 and absorbed and availability >= slo else "NOT PROVEN",
        "minutes": minutes,
    }
