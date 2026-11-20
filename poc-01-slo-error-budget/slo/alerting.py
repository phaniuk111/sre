"""Multi-window, multi-burn-rate alerting.

The book (ch. 8, "Automatic Alert Configurations on SLOs") describes Google's
central alert generator:
  * FAST burn: >= 2% of the 30-day budget in 1 hour  -> PAGE
  * SLOW burn: >= 10% of the 30-day budget in 3 days -> TICKET
Each long window is paired with a short window (1/12 of the long one) so the
alert *resets quickly* once the service recovers.

The Site Reliability Workbook (ch. 5) recommends a four-rule variant; both are
provided so you can compare them in an interview.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List

from .budget import burn_rate_for_consumption

# A function returning the observed error ratio for a window length in hours.
ErrorRatioFn = Callable[[float], float]


@dataclass(frozen=True)
class BurnRateWindow:
    name: str
    long_window_h: float
    short_window_h: float
    burn_rate_threshold: float
    severity: str  # "page" | "ticket"

    def fires(self, slo: float, error_ratio: ErrorRatioFn) -> bool:
        budget = 1.0 - slo
        threshold_ratio = self.burn_rate_threshold * budget
        # BOTH windows must exceed the threshold: long window gives significance,
        # short window proves the problem is still happening right now.
        return error_ratio(self.long_window_h) > threshold_ratio and error_ratio(self.short_window_h) > threshold_ratio


@dataclass
class MultiWindowPolicy:
    slo: float
    windows: List[BurnRateWindow] = field(default_factory=list)

    def evaluate(self, error_ratio: ErrorRatioFn) -> Dict[str, List[str]]:
        result: Dict[str, List[str]] = {"page": [], "ticket": []}
        for w in self.windows:
            if w.fires(self.slo, error_ratio):
                result[w.severity].append(w.name)
        return result


def google_default_policy(slo: float, slo_window_days: float = 30) -> MultiWindowPolicy:
    """The two-rule policy described in SRE 2nd ed. ch. 8."""
    fast = burn_rate_for_consumption(0.02, 1, slo_window_days)   # 14.4 for 30d
    slow = burn_rate_for_consumption(0.10, 72, slo_window_days)  # 1.0 for 30d
    return MultiWindowPolicy(
        slo=slo,
        windows=[
            BurnRateWindow("fast-burn-2pct-1h", 1, 1 / 12, fast, "page"),
            BurnRateWindow("slow-burn-10pct-3d", 72, 6, slow, "ticket"),
        ],
    )


def workbook_policy(slo: float, slo_window_days: float = 30) -> MultiWindowPolicy:
    """The four-rule policy from The Site Reliability Workbook ch. 5."""
    return MultiWindowPolicy(
        slo=slo,
        windows=[
            BurnRateWindow("2pct-in-1h", 1, 5 / 60, burn_rate_for_consumption(0.02, 1, slo_window_days), "page"),
            BurnRateWindow("5pct-in-6h", 6, 0.5, burn_rate_for_consumption(0.05, 6, slo_window_days), "page"),
            BurnRateWindow("10pct-in-1d", 24, 2, burn_rate_for_consumption(0.10, 24, slo_window_days), "ticket"),
            BurnRateWindow("10pct-in-3d", 72, 6, burn_rate_for_consumption(0.10, 72, slo_window_days), "ticket"),
        ],
    )
