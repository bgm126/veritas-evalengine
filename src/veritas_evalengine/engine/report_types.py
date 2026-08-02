"""Report and evaluation result data types."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from veritas_evalengine.core.policy import PolicyVerdict
from veritas_evalengine.core.schemas import AgentRun, EvalTask, ScorerResult


class EvalTaskResult(BaseModel):
    task_id: str
    task_type: str
    runs: List[AgentRun] = Field(default_factory=list)
    scorer_results: List[ScorerResult] = Field(default_factory=list)
    passed: bool = True
    metrics: Dict[str, float] = Field(default_factory=dict)


class EvalReport(BaseModel):
    suite_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    total_tasks: int = 0
    passed_tasks: int = 0
    failed_tasks: int = 0
    policy_verdict: Optional[PolicyVerdict] = None
    task_results: List[EvalTaskResult] = Field(default_factory=list)
    aggregated_metrics: Dict[str, float] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(mode="json")
