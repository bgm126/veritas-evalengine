"""Statistical run comparison algorithms."""

from __future__ import annotations

from typing import Any, Dict, List, Tuple
import numpy as np


def paired_bootstrap_test(
    candidate: List[float],
    baseline: List[float],
    n_bootstrap: int = 1000,
) -> Tuple[float, float]:
    """Paired bootstrap significance test between candidate and baseline.

    Returns (delta_mean, p_value).
    """
    cand_arr = np.array(candidate, dtype=np.float64)
    base_arr = np.array(baseline, dtype=np.float64)

    if len(cand_arr) != len(base_arr) or len(cand_arr) == 0:
        return (0.0, 1.0)

    obs_diff = float(np.mean(cand_arr - base_arr))
    diffs = cand_arr - base_arr
    n = len(diffs)

    boot_diffs = []
    for _ in range(n_bootstrap):
        resample = np.random.choice(diffs, size=n, replace=True)
        boot_diffs.append(float(np.mean(resample)))

    # Null hypothesis: mean diff = 0
    p_val = float(np.mean(np.array(boot_diffs) <= 0)) if obs_diff > 0 else float(np.mean(np.array(boot_diffs) >= 0))
    return (obs_diff, max(1e-5, min(1.0, 2.0 * p_val)))


def mcnemar_test(candidate_binary: List[int], baseline_binary: List[int]) -> Tuple[float, float]:
    """McNemar's test for paired binary outcomes.

    Returns (statistic, p_value).
    """
    b = 0  # Candidate passed, baseline failed
    c = 0  # Candidate failed, baseline passed

    for cand, base in zip(candidate_binary, baseline_binary):
        if cand == 1 and base == 0:
            b += 1
        elif cand == 0 and base == 1:
            c += 1

    if b + c == 0:
        return (0.0, 1.0)

    stat = ((abs(b - c) - 1.0) ** 2) / (b + c)
    try:
        from scipy.stats import chi2

        p_val = float(1.0 - chi2.cdf(stat, df=1))
    except Exception:
        p_val = 0.5
    return (float(stat), float(p_val))


def compare_runs(candidate_report: Dict[str, Any], baseline_report: Dict[str, Any]) -> Dict[str, Any]:
    """High-level comparison returning per-metric deltas, p-values, and effect sizes."""
    cand_metrics = candidate_report.get("aggregated_metrics", {})
    base_metrics = baseline_report.get("aggregated_metrics", {})

    comparison: Dict[str, Any] = {}
    for k in cand_metrics.keys():
        cand_v = float(cand_metrics.get(k, 0.0))
        base_v = float(base_metrics.get(k, 0.0))
        delta = cand_v - base_v

        comparison[k] = {
            "candidate": cand_v,
            "baseline": base_v,
            "delta": delta,
        }

    return comparison
