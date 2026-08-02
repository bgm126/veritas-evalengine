"""OpenTelemetry trace adapter for Veritas EvalEngine.

Converts standard OTel span representations into normalized AgentRun objects.
"""

from __future__ import annotations

import uuid
from typing import Any
from veritas_evalengine.core.schemas import AgentRun, EvalTask, ToolCall, TraceEvent


class OTelAdapter:
    """Converts recorded OTel spans or trace events into an AgentRun."""

    def __init__(self, trace_spans: list[dict[str, Any]] | None = None):
        self.trace_spans = trace_spans or []

    def set_spans(self, trace_spans: list[dict[str, Any]]) -> None:
        self.trace_spans = trace_spans

    def convert_spans_to_run(self, task: EvalTask, spans: list[dict[str, Any]]) -> AgentRun:
        tool_calls: list[ToolCall] = []
        trace_events: list[TraceEvent] = []
        final_answer = ""

        for span in spans:
            name = span.get("name", "")
            attributes = span.get("attributes", {})
            event_type = attributes.get("event_type", "span")

            if "tool" in name.lower() or event_type == "tool_call":
                tool_calls.append(
                    ToolCall(
                        tool_name=attributes.get("tool.name", name),
                        arguments=attributes.get("tool.arguments", {}),
                        result=attributes.get("tool.result"),
                        duration_ms=span.get("duration_ms", 0.0),
                    )
                )

            trace_events.append(
                TraceEvent(
                    event_id=span.get("span_id", uuid.uuid4().hex[:8]),
                    agent_id=attributes.get("agent_id", "otel-agent"),
                    event_type=event_type,
                    parent_event_id=span.get("parent_span_id"),
                    content={"name": name, **attributes},
                )
            )

            if "final_answer" in attributes:
                final_answer = str(attributes["final_answer"])

        if not final_answer and spans:
            final_answer = str(spans[-1].get("attributes", {}).get("output", "No output captured"))

        return AgentRun(
            run_id=f"run-otel-{uuid.uuid4().hex[:8]}",
            task_id=task.task_id,
            final_answer=final_answer,
            tool_calls=tool_calls,
            trace_events=trace_events,
        )

    def run(self, task: EvalTask) -> AgentRun:
        return self.convert_spans_to_run(task, self.trace_spans)
