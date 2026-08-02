"""Tests for stress lab generators."""

from veritas_evalengine.stress.generators import (
    ContradictorySourceGenerator,
    ForbiddenActionGenerator,
    MissingInfoGenerator,
    PromptInjectionGenerator,
)


def test_stress_generators():
    gen1 = MissingInfoGenerator()
    task1 = gen1.generate(seed=42)
    assert "missing_info" in task1.tags

    gen2 = ContradictorySourceGenerator()
    task2 = gen2.generate(seed=42)
    assert len(task2.context_documents) == 2

    gen3 = PromptInjectionGenerator()
    task3 = gen3.generate(seed=42)
    assert len(task3.forbidden_actions) > 0
