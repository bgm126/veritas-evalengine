"""Generic agent adapter wrapping any simple callable into the AgentAdapter protocol."""

from __future__ import annotations

import time
import uuid
from typing import Callable
from veritas_evalengine.core.schemas import AgentRun, CostInfo, EvalTask


class GenericAgentAdapter:
    """Wraps a string-to-string function `(prompt: str) -> str` into an AgentAdapter."""

    def __init__(self, func: Callable[[str], str], model_name: str = "generic-callable"):
        self.func = func
        self.model_name = model_name

    def run(self, task: EvalTask) -> AgentRun:
        start = time.perf_counter()
        final_answer = self.func(task.prompt)
        duration_ms = (time.perf_counter() - start) * 1000.0

        return AgentRun(
            run_id=f"run-{uuid.uuid4().hex[:8]}",
            task_id=task.task_id,
            final_answer=final_answer,
            cost=CostInfo(latency_ms=duration_ms),
            metadata={"model_name": self.model_name},
        )
