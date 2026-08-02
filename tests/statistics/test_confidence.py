"""Tests for confidence math."""

from veritas_evalengine.statistics.confidence import bootstrap_ci, pass_at_k, wilson_ci


def test_wilson_ci():
    lcb, ucb = wilson_ci(10, 10)
    assert lcb > 0.6
    assert ucb <= 1.0


def test_bootstrap_ci():
    data = [1.0, 1.0, 0.9, 0.95, 1.0]
    low, high = bootstrap_ci(data)
    assert low <= high


def test_pass_at_k():
    res = pass_at_k(10, 8, 1)
    assert res == 0.8
