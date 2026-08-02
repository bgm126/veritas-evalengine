"""Tests for TruthfulQA benchmark adapter."""

import pytest
from veritas_evalengine.benchmarks.truthfulqa import TruthfulQABenchmark


@pytest.mark.benchmark
def test_truthfulqa_adapter():
    adapter = TruthfulQABenchmark()
    suite = adapter.load_suite(limit=2)
    assert suite.name == "truthful_qa"
    assert len(suite.tasks) == 2
