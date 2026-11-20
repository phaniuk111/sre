"""SLO maths toolkit (Book ch. 8, ch. 9 "Variation-Based Monitoring", appendix E).

Everything here is dependency-free so you can reason about it in an interview
whiteboard setting, and it is the same maths the CloudWatch alarms in
../terraform implement.
"""
from .budget import (
    ErrorBudget,
    burn_rate,
    budget_consumed_fraction,
    time_to_exhaustion_hours,
)
from .alerting import (
    BurnRateWindow,
    MultiWindowPolicy,
    google_default_policy,
    workbook_policy,
)
from .stats import wilson_interval, binomial_should_alert, min_failures_to_alert
from .composition import serial_availability, parallel_availability, k_of_n_availability
from .bad_minutes import BadMinuteSLO

__all__ = [
    "ErrorBudget",
    "burn_rate",
    "budget_consumed_fraction",
    "time_to_exhaustion_hours",
    "BurnRateWindow",
    "MultiWindowPolicy",
    "google_default_policy",
    "workbook_policy",
    "wilson_interval",
    "binomial_should_alert",
    "min_failures_to_alert",
    "serial_availability",
    "parallel_availability",
    "k_of_n_availability",
    "BadMinuteSLO",
]
