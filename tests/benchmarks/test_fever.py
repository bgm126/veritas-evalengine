"""Tests for FEVER benchmark adapter."""

import pytest
from veritas_evalengine.benchmarks.fever import FEVERBenchmark


@pytest.mark.benchmark
def test_fever_adapter():
    adapter = FEVERBenchmark()
    suite = adapter.load_suite(limit=2)
    assert suite.name == "fever"
    assert len(suite.tasks) == 2
