"""Statistical drift metrics math functions."""

from __future__ import annotations

from typing import List, Tuple
from veritas_evalengine.scorers.drift import CUSUMDetector, EWMADetector, PSIDetector


def psi(reference: List[float], current: List[float], num_bins: int = 5) -> float:
    """Population Stability Index."""
    return PSIDetector.calculate(reference, current, num_bins=num_bins)


def ewma(series: List[float], span: float = 0.3) -> float:
    """Exponentially Weighted Moving Average."""
    return EWMADetector.calculate(series, alpha=span)


def cusum(series: List[float], target: float = 1.0, threshold: float = 1.5, drift: float = 0.1) -> Tuple[bool, float]:
    """One-sided CUSUM change-point detector."""
    return CUSUMDetector.detect(series, target=target, threshold=threshold, drift=drift)


def cusum_bilateral(
    series: List[float], target: float = 1.0, threshold: float = 1.5, drift: float = 0.1
) -> Tuple[bool, float, float]:
    """Bilateral CUSUM detector for upper and lower shifts."""
    if not series:
        return False, 0.0, 0.0
    s_hi = 0.0
    s_lo = 0.0
    alarm = False

    for x in series:
        s_hi = max(0.0, s_hi + (target - x - drift))
        s_lo = max(0.0, s_lo + (x - target - drift))
        if s_hi >= threshold or s_lo >= threshold:
            alarm = True

    return alarm, s_hi, s_lo
