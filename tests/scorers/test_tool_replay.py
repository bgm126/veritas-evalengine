"""Tests for tool replay scorer."""

from veritas_evalengine.adapters.reference import ReferenceToolAdapter
from veritas_evalengine.core.schemas import EvalTask, ToolCall
from veritas_evalengine.scorers.tool_replay import ToolReplayScorer


def test_tool_replay_success():
    task = EvalTask(
        task_id="tool-01",
        task_type="tool",
        prompt="Cancel order",
        expected_tool_calls=[
            ToolCall(tool_name="fetch_order", arguments={"order_id": "123"}),
            ToolCall(tool_name="cancel_order", arguments={"order_id": "123"}),
        ],
        expected_terminal_state="COMPLETED",
    )
    adapter = ReferenceToolAdapter(simulate_failure=False)
    run = adapter.run(task)

    scorer = ToolReplayScorer()
    res = scorer.score(task, run)
    assert res.passed is True
    assert res.metrics["accuracy"] == 1.0


def test_tool_replay_failure():
    task = EvalTask(
        task_id="tool-02",
        task_type="tool",
        prompt="Cancel order",
        expected_tool_calls=[
            ToolCall(tool_name="fetch_order", arguments={"order_id": "123"}),
            ToolCall(tool_name="cancel_order", arguments={"order_id": "123"}),
        ],
        expected_terminal_state="COMPLETED",
    )
    adapter = ReferenceToolAdapter(simulate_failure=True)
    run = adapter.run(task)

    scorer = ToolReplayScorer()
    res = scorer.score(task, run)
    assert res.passed is False
