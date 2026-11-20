"""Error budgets and burn rates.

Key ideas (ch. 8):
  * SLI = good events / valid events (a ratio, 0..1)
  * SLO = target for the SLI over a window (e.g. 99.9% over 30 days)
  * Error budget = 1 - SLO  (the *allowed* unreliability)
  * Burn rate = observed error rate / budgeted error rate.
      burn rate 1   -> budget lasts exactly the SLO window
      burn rate 14.4 on a 30d window -> 2% of budget gone in 1 hour
"""
from __future__ import annotations

from dataclasses import dataclass

MINUTES_PER_DAY = 24 * 60


@dataclass(frozen=True)
class ErrorBudget:
    slo: float  # e.g. 0.999
    window_days: float = 30.0

    def __post_init__(self) -> None:
        if not 0.0 < self.slo < 1.0:
            raise ValueError("SLO must be strictly between 0 and 1 (100% is never the right target)")
        if self.window_days <= 0:
            raise ValueError("window must be positive")

    @property
    def budget_fraction(self) -> float:
        """Allowed error ratio, e.g. 0.001 for 99.9%."""
        return 1.0 - self.slo

    @property
    def allowed_downtime_minutes(self) -> float:
        """Time-based view: 99.9% over 30d -> 43.2 minutes."""
        return self.budget_fraction * self.window_days * MINUTES_PER_DAY

    def allowed_bad_events(self, total_events: int) -> float:
        """Event-based view: with 10M requests and 99.9%, 10,000 may fail."""
        return self.budget_fraction * total_events

    def remaining_fraction(self, good: int, total: int) -> float:
        """Fraction of budget left (can be negative when overspent)."""
        if total <= 0:
            return 1.0
        bad = total - good
        allowed = self.allowed_bad_events(total)
        return 1.0 - bad / allowed if allowed else float("-inf")


def burn_rate(error_ratio: float, slo: float) -> float:
    """How many times faster than 'sustainable' the budget is being spent."""
    budget = 1.0 - slo
    if budget <= 0:
        raise ValueError("SLO must be < 1")
    return error_ratio / budget


def budget_consumed_fraction(rate: float, alert_window_hours: float, slo_window_days: float = 30) -> float:
    """Fraction of the whole budget consumed if `rate` persists for the alert window.

    consumed = burn_rate * alert_window / slo_window
    e.g. 14.4 * 1h / 720h = 0.02 (2%)
    """
    return rate * alert_window_hours / (slo_window_days * 24)


def burn_rate_for_consumption(consumed_fraction: float, alert_window_hours: float, slo_window_days: float = 30) -> float:
    """Inverse of budget_consumed_fraction: what burn rate eats X% in Y hours?"""
    return consumed_fraction * slo_window_days * 24 / alert_window_hours


def time_to_exhaustion_hours(rate: float, remaining_fraction: float = 1.0, slo_window_days: float = 30) -> float:
    """At the current burn rate, how long until the remaining budget is gone?"""
    if rate <= 0:
        return float("inf")
    return remaining_fraction * slo_window_days * 24 / rate
