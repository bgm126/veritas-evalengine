"""Tests for HaluEval benchmark adapter."""

import pytest
from veritas_evalengine.benchmarks.halueval import HaluEvalBenchmark


@pytest.mark.benchmark
def test_halueval_adapter():
    adapter = HaluEvalBenchmark()
    suite = adapter.load_suite(limit=1)
    assert suite.name == "halueval"
    assert len(suite.tasks) == 1
