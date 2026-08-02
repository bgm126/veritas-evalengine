"""Tests for judge reliability lab."""

from veritas_evalengine.scorers.judge import BradleyTerryRanker, JudgeReliabilityAnalyzer, PairwiseJudge


def test_pairwise_judge_swap():
    judge = PairwiseJudge()
    res = judge.compare("What is 2+2?", "4", "The answer is 4.")
    assert "is_flipped" in res


def test_judge_reliability_analyzer():
    res = JudgeReliabilityAnalyzer.spearman_correlation([1.0, 2.0, 3.0], [1.0, 2.0, 3.0])
    assert res == 1.0


def test_bradley_terry_ranker():
    # 3 items, comparisons: (0, 1), (0, 2), (1, 2)
    comparisons = [(0, 1), (0, 2), (1, 2)]
    weights = BradleyTerryRanker.fit(3, comparisons)
    assert len(weights) == 3
    assert weights[0] > weights[2]
