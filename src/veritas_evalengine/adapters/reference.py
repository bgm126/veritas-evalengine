"""Reference agent adapters for system demonstration and testing.

Provides mock adapters for RAG, tool-use, coding, and multi-agent systems.
"""

from __future__ import annotations

import random
import uuid
from typing import Any
from veritas_evalengine.core.schemas import (
    AgentRun,
    Claim,
    ClaimVerdict,
    CostInfo,
    EvalTask,
    EvidenceSpan,
    StateTransition,
    ToolCall,
    TraceEvent,
)


class ReferenceRAGAdapter:
    """Mock RAG agent adapter.

    If generate_hallucination=True, appends ungrounded claims to answers.
    """

    def __init__(self, generate_hallucination: bool = False):
        self.generate_hallucination = generate_hallucination

    def run(self, task: EvalTask) -> AgentRun:
        docs = task.context_documents
        doc_texts = [d.get("text", "") for d in docs]
        source_id = docs[0].get("id", "doc1") if docs else "doc1"

        if doc_texts:
            base_answer = f"Based on {source_id}: {doc_texts[0]}"
            spans = [EvidenceSpan(source_id=source_id, text=doc_texts[0])]
            claims = [Claim(text=doc_texts[0], evidence_spans=spans)]
        else:
            base_answer = "I don't know based on the provided documents."
            spans = []
            claims = []

        if self.generate_hallucination:
            hallucinated_text = " The system was originally invented in 1750 by Lord Sterling."
            base_answer += hallucinated_text
            claims.append(Claim(text="The system was originally invented in 1750 by Lord Sterling.", evidence_spans=[]))

        return AgentRun(
            run_id=f"rag-run-{uuid.uuid4().hex[:8]}",
            task_id=task.task_id,
            final_answer=base_answer,
            claims=claims,
            evidence_spans=spans,
            cost=CostInfo(input_tokens=150, output_tokens=50, latency_ms=120.0),
        )


class ReferenceToolAdapter:
    """Mock tool-using agent adapter (e.g. order management)."""

    def __init__(self, simulate_failure: bool = False):
        self.simulate_failure = simulate_failure

    def run(self, task: EvalTask) -> AgentRun:
        tool_calls = []
        state_transitions = [
            StateTransition(from_state="INIT", to_state="AUTH", trigger="authenticate"),
            StateTransition(from_state="AUTH", to_state="PROCESSING", trigger="fetch_order"),
        ]

        # Execute expected tool call sequence if present, or default
        for expected in task.expected_tool_calls:
            result = expected.result or {"status": "success"}
            if self.simulate_failure and expected.tool_name == "cancel_order":
                result = {"status": "error", "reason": "unauthorized"}

            tool_calls.append(
                ToolCall(
                    tool_name=expected.tool_name,
                    arguments=expected.arguments,
                    result=result,
                    duration_ms=45.0,
                )
            )

        terminal_state = "FAILED" if self.simulate_failure else (task.expected_terminal_state or "COMPLETED")
        state_transitions.append(
            StateTransition(from_state="PROCESSING", to_state=terminal_state, trigger="complete")
        )

        final_ans = (
            f"Action performed with status: {terminal_state}."
            if not self.simulate_failure
            else "Failed to complete request due to error."
        )

        return AgentRun(
            run_id=f"tool-run-{uuid.uuid4().hex[:8]}",
            task_id=task.task_id,
            final_answer=final_ans,
            tool_calls=tool_calls,
            state_transitions=state_transitions,
            cost=CostInfo(input_tokens=200, output_tokens=40, latency_ms=180.0),
        )


class ReferenceCodingAdapter:
    """Mock coding agent adapter."""

    def __init__(self, generate_bug: bool = False):
        self.generate_bug = generate_bug

    def run(self, task: EvalTask) -> AgentRun:
        if self.generate_bug:
            code = "def solution(x):\n    return x - 1  # Bug: wrong math"
        else:
            code = "def solution(x):\n    return x + 1"

        return AgentRun(
            run_id=f"code-run-{uuid.uuid4().hex[:8]}",
            task_id=task.task_id,
            final_answer=f"```python\n{code}\n```",
            cost=CostInfo(input_tokens=100, output_tokens=30, latency_ms=90.0),
            metadata={"code": code},
        )


class ReferenceMultiAgentAdapter:
    """Mock multi-agent research system with upstream/downstream agents."""

    def __init__(self, inject_upstream_error: bool = False):
        self.inject_upstream_error = inject_upstream_error

    def run(self, task: EvalTask) -> AgentRun:
        root_id = "agent-researcher"
        worker_id = "agent-analyst"

        events = [
            TraceEvent(
                event_id="evt-1",
                agent_id=root_id,
                event_type="delegation",
                content={"to": worker_id, "query": task.prompt},
            )
        ]

        if self.inject_upstream_error:
            events.append(
                TraceEvent(
                    event_id="evt-2",
                    agent_id=worker_id,
                    event_type="claim",
                    parent_event_id="evt-1",
                    content={"claim_text": "Company revenue grew by 900% in Q3.", "valid": False},
                )
            )
            final_ans = "According to our analysis, company revenue grew by 900% in Q3."
        else:
            events.append(
                TraceEvent(
                    event_id="evt-2",
                    agent_id=worker_id,
                    event_type="claim",
                    parent_event_id="evt-1",
                    content={"claim_text": "Company revenue grew by 12% in Q3.", "valid": True},
                )
            )
            final_ans = "According to our analysis, company revenue grew by 12% in Q3."

        events.append(
            TraceEvent(
                event_id="evt-3",
                agent_id=root_id,
                event_type="message",
                parent_event_id="evt-2",
                content={"final_synthesis": final_ans},
            )
        )

        return AgentRun(
            run_id=f"multi-run-{uuid.uuid4().hex[:8]}",
            task_id=task.task_id,
            final_answer=final_ans,
            trace_events=events,
            cost=CostInfo(input_tokens=500, output_tokens=150, latency_ms=350.0),
        )
