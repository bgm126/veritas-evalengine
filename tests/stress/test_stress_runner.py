"""Tests for stress runner."""

from veritas_evalengine.adapters.reference import ReferenceRAGAdapter
from veritas_evalengine.stress.runner import StressRunner


def test_stress_runner():
    adapter = ReferenceRAGAdapter(generate_hallucination=False)
    runner = StressRunner(adapter)

    results = runner.run_all_families(n_per_family=1)
    assert "prompt_injection" in results
    assert "attacks_succeeded" in results["prompt_injection"]
