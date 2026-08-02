"""Statistical confidence utilities (Capability 5 & statistics module)."""

from __future__ import annotations

import math
from typing import Callable, List, Tuple
import numpy as np

from veritas_evalengine.scorers.evidence import wilson_score_interval


def wilson_ci(successes: int, trials: int, alpha: float = 0.05) -> Tuple[float, float]:
    """Compute Wilson score interval bounds."""
    return wilson_score_interval(successes, trials, confidence=1.0 - alpha)


def bootstrap_ci(
    data: List[float],
    statistic: Callable[[np.ndarray], float] = np.mean,
    n_bootstrap: int = 1000,
    alpha: float = 0.05,
) -> Tuple[float, float]:
    """Compute bootstrap confidence interval for any custom statistic."""
    if not data:
        return (0.0, 0.0)
    arr = np.array(data, dtype=np.float64)
    n = len(arr)
    boot_stats = []

    for _ in range(n_bootstrap):
        resample = np.random.choice(arr, size=n, replace=True)
        boot_stats.append(float(statistic(resample)))

    low = float(np.percentile(boot_stats, 100 * (alpha / 2)))
    high = float(np.percentile(boot_stats, 100 * (1 - alpha / 2)))
    return (low, high)


def pass_at_k(n: int, c: int, k: int) -> float:
    """Unbiased pass@k estimator (HumanEval / Codex style).

    pass@k = 1 - comb(n - c, k) / comb(n, k)
    n: total samples per task
    c: correct samples passing tests
    k: k evaluations evaluated
    """
    if n - c < k:
        return 1.0
    return float(1.0 - math.comb(n - c, k) / math.comb(n, k))
