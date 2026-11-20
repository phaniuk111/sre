"""Overload & dependency resilience patterns from SRE 2nd ed. ch. 17.

Server side : LoadShedder (criticality-aware), graceful degradation hook
Client side : backoff_with_jitter, RetryBudget, AdaptiveThrottler, CircuitBreaker, hedged_call
"""
from .backoff import backoff_with_jitter, retry
from .budgets import RetryBudget
from .throttling import AdaptiveThrottler
from .circuit_breaker import CircuitBreaker, CircuitOpenError
from .shedding import Criticality, LoadShedder, OverloadedError
from .hedging import hedged_call

__all__ = [
    "backoff_with_jitter", "retry", "RetryBudget", "AdaptiveThrottler",
    "CircuitBreaker", "CircuitOpenError", "Criticality", "LoadShedder",
    "OverloadedError", "hedged_call",
]
