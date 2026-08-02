"""Pytest fixtures for Veritas EvalEngine."""

import pytest
from veritas_evalengine.core.schemas import AgentRun, Claim, ClaimVerdict, EvalSuite, EvalTask, EvidenceSpan


@pytest.fixture
def sample_task() -> EvalTask:
    return EvalTask(
        task_id="task-101",
        task_type="rag",
        prompt="What is the capital of France?",
        context_documents=[
            {"id": "doc1", "text": "Paris is the capital of France."}
        ],
        reference_answer="Paris",
    )


@pytest.fixture
def sample_run(sample_task: EvalTask) -> AgentRun:
    span = EvidenceSpan(source_id="doc1", text="Paris is the capital of France.")
    claim = Claim(text="Paris is the capital of France.", verdict=ClaimVerdict.SUPPORTED, evidence_spans=[span])
    return AgentRun(
        run_id="run-101",
        task_id=sample_task.task_id,
        final_answer="Paris is the capital of France.",
        claims=[claim],
        evidence_spans=[span],
    )


@pytest.fixture
def sample_suite(sample_task: EvalTask) -> EvalSuite:
    return EvalSuite(
        name="test_suite",
        tasks=[sample_task],
    )
