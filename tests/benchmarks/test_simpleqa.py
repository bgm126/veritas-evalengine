"""Tests for SimpleQA benchmark adapter."""

import pytest
from veritas_evalengine.benchmarks.simpleqa import SimpleQABenchmark


@pytest.mark.benchmark
def test_simpleqa_adapter():
    adapter = SimpleQABenchmark()
    suite = adapter.load_suite(limit=1)
    assert suite.name == "simple_qa"
    assert len(suite.tasks) == 1
