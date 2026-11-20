"""Bad-minute SLOs (ch. 8 "Client-Side SLOs" and ch. 9 CUJ aggregation).

Two uses from the book:
1. High noise floor (client-side telemetry): if ~5% of client requests always
   fail (bad networks, old phones), a request-ratio SLO can never be tighter than
   ~95%, and fast-burn alerts can't fire. Instead, call a minute "bad" when its
   error rate exceeds a threshold just above the noise floor (e.g. 6%), and set
   the SLO on the fraction of GOOD MINUTES (e.g. 99.9% => ~43 bad minutes / 30d).
2. CUJ aggregation: a journey minute is bad if ANY constituent interaction (CUI)
   SLI was bad in that minute.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence, Tuple


@dataclass
class BadMinuteSLO:
    bad_minute_error_threshold: float  # e.g. 0.06
    slo: float  # fraction of good minutes, e.g. 0.999

    def classify(self, per_minute: Iterable[Tuple[int, int]]) -> List[bool]:
        """per_minute: (failures, total) for each minute. Returns True for BAD minutes."""
        out = []
        for failures, total in per_minute:
            out.append(total > 0 and failures / total > self.bad_minute_error_threshold)
        return out

    def compliance(self, per_minute: Sequence[Tuple[int, int]]) -> float:
        flags = self.classify(per_minute)
        return 1 - sum(flags) / len(flags) if flags else 1.0

    def allowed_bad_minutes(self, window_minutes: int) -> float:
        return (1 - self.slo) * window_minutes


def cuj_bad_minutes(cui_bad_flags: Dict[str, Sequence[bool]]) -> List[bool]:
    """A CUJ minute is bad if any of its CUIs (search, pan/zoom, route, start nav...) is bad."""
    series = list(cui_bad_flags.values())
    if not series:
        return []
    length = len(series[0])
    if any(len(s) != length for s in series):
        raise ValueError("all CUI series must be aligned to the same minutes")
    return [any(s[i] for s in series) for i in range(length)]
