"""Tests for run comparison statistics."""

import pytest
from veritas_evalengine.statistics.comparison import compare_runs, mcnemar_test, paired_bootstrap_test


def test_paired_bootstrap_test():
    cand = [1.0, 1.0, 1.0, 0.9]
    base = [0.5, 0.6, 0.5, 0.4]
    delta, p_val = paired_bootstrap_test(cand, base)
    assert delta > 0
    assert p_val <= 0.05


def test_mcnemar_test():
    cand_bin = [1, 1, 1, 1, 1]
    base_bin = [0, 0, 0, 1, 1]
    stat, p_val = mcnemar_test(cand_bin, base_bin)
    assert stat >= 0.0


def test_compare_runs():
    cand_rep = {"aggregated_metrics": {"pass_rate": 0.95}}
    base_rep = {"aggregated_metrics": {"pass_rate": 0.80}}
    res = compare_runs(cand_rep, base_rep)
    assert res["pass_rate"]["delta"] == pytest.approx(0.15)
