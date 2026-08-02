"""Protocol definitions for adapter and scorer extension points."""
from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from .schemas import AgentRun, EvalTask, ScorerResult


@runtime_checkable
class AgentAdapter(Protocol):
    """The agent-agnostic boundary. Implement this for your agent."""

    def run(self, task: EvalTask) -> AgentRun:
        ...


@runtime_checkable
class Scorer(Protocol):
    """Score an AgentRun against its task."""

    name: str

    def score(self, task: EvalTask, run: AgentRun) -> ScorerResult:
        ...
