"""Tests for multi-agent failure mapper."""

from veritas_evalengine.adapters.reference import ReferenceMultiAgentAdapter
from veritas_evalengine.core.schemas import EvalTask
from veritas_evalengine.scorers.trace import MultiAgentTraceScorer


def test_multi_agent_trace_clean():
    task = EvalTask(task_id="m1", task_type="multi_agent", prompt="Analyze Q3 revenue")
    adapter = ReferenceMultiAgentAdapter(inject_upstream_error=False)
    run = adapter.run(task)

    scorer = MultiAgentTraceScorer()
    res = scorer.score(task, run)
    assert res.passed is True


def test_multi_agent_trace_failure_attribution():
    task = EvalTask(task_id="m2", task_type="multi_agent", prompt="Analyze Q3 revenue")
    adapter = ReferenceMultiAgentAdapter(inject_upstream_error=True)
    run = adapter.run(task)

    scorer = MultiAgentTraceScorer()
    res = scorer.score(task, run)
    assert res.passed is False
    assert res.details.get("root_agent_id") == "agent-analyst"
