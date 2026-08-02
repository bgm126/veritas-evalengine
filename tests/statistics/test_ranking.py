"""Tests for Bradley-Terry ranking."""

from veritas_evalengine.statistics.ranking import bt_rank


def test_bt_rank():
    comparisons = [(0, 1), (0, 1), (1, 2)]
    scores = bt_rank(3, comparisons)
    assert len(scores) == 3
    assert scores[0] >= scores[1]
