"""Tests for evaluation runner."""

from veritas_evalengine.adapters.reference import ReferenceRAGAdapter
from veritas_evalengine.core.policy import ReleasePolicy
from veritas_evalengine.core.schemas import EvalSuite, EvalTask
from veritas_evalengine.engine.runner import EvalRunner


def test_eval_runner_execution(sample_suite: EvalSuite):
    adapter = ReferenceRAGAdapter(generate_hallucination=False)
    policy = ReleasePolicy(fail_if=["deterministic_failure_count > 0"])
    runner = EvalRunner(adapter=adapter, policy=policy)

    report = runner.run_suite(sample_suite)
    assert report.total_tasks == 1
    assert report.passed_tasks == 1
    assert report.policy_verdict is not None
    assert report.policy_verdict.passed is True
