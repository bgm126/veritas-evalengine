"""Optional integration adapters for external red-teaming tools (Garak, PyRIT)."""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional
from veritas_evalengine.core.schemas import AgentRun, EvalTask, TraceEvent


class GarakProbeAdapter:
    """Wraps Garak probe corpora to produce EvalTask objects."""

    def __init__(self, probe_name: str = "garak.probes.promptinjection"):
        self.probe_name = probe_name

    def convert_prompts_to_tasks(self, prompts: List[str]) -> List[EvalTask]:
        tasks: List[EvalTask] = []
        for idx, p in enumerate(prompts):
            tasks.append(
                EvalTask(
                    task_id=f"garak-{idx+1}",
                    task_type="adversarial",
                    prompt=p,
                    forbidden_actions=["jailbreak", "reveal_secret"],
                    tags=["garak", self.probe_name],
                )
            )
        return tasks


class PyRITAdapter:
    """Wraps PyRIT conversation traces into normalized AgentRun objects."""

    def convert_pyrit_conversation(self, conversation_history: List[Dict[str, Any]]) -> AgentRun:
        trace_events: List[TraceEvent] = []
        final_ans = ""

        for idx, turn in enumerate(conversation_history):
            role = turn.get("role", "user")
            content = turn.get("content", "")

            trace_events.append(
                TraceEvent(
                    event_id=f"pyrit-evt-{idx+1}",
                    agent_id=role,
                    event_type="message",
                    content={"role": role, "text": content},
                )
            )
            if role == "assistant":
                final_ans = content

        return AgentRun(
            run_id=f"run-pyrit-{uuid.uuid4().hex[:8]}",
            task_id="pyrit-task",
            final_answer=final_ans,
            trace_events=trace_events,
        )
