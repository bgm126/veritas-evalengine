"""Tests for drift statistics functions."""

from veritas_evalengine.statistics.drift_stats import cusum, cusum_bilateral, ewma, psi


def test_drift_stats_functions():
    ref = [1.0] * 10
    curr = [1.0] * 10
    assert psi(ref, curr) < 0.1
    assert ewma([1.0, 0.8, 0.6]) > 0.0

    alarm, s_hi, s_lo = cusum_bilateral([1.0, 0.0, 0.0, 0.0])
    assert s_hi >= 0.0
