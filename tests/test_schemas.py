"""Tests for core evaluation schemas."""

from veritas_evalengine.core.schemas import AgentRun, Claim, ClaimVerdict, EvalSuite, EvalTask, ToolCall


def test_agent_run_content_hash(sample_task: EvalTask):
    run1 = AgentRun(run_id="run-1", task_id=sample_task.task_id, final_answer="Answer A")
    run2 = AgentRun(run_id="run-2", task_id=sample_task.task_id, final_answer="Answer A")
    run3 = AgentRun(run_id="run-3", task_id=sample_task.task_id, final_answer="Answer B")

    assert run1.content_hash() == run2.content_hash()
    assert run1.content_hash() != run3.content_hash()


def test_eval_suite_tasks(sample_task: EvalTask):
    suite = EvalSuite(name="suite1", tasks=[sample_task])
    assert len(suite.tasks) == 1
    assert suite.tasks[0].task_id == "task-101"
