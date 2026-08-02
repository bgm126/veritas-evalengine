"""Core evaluation schemas.

All downstream modules consume only these types, never raw dicts.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ClaimVerdict(str, Enum):
    SUPPORTED = "supported"
    CONTRADICTED = "contradicted"
    UNVERIFIABLE = "unverifiable"
    NON_VERIFIABLE = "non_verifiable"


class EvidenceSpan(BaseModel):
    source_id: str
    text: str
    start_char: Optional[int] = None
    end_char: Optional[int] = None


class Claim(BaseModel):
    text: str
    verdict: Optional[ClaimVerdict] = None
    evidence_spans: List[EvidenceSpan] = Field(default_factory=list)
    confidence: Optional[float] = None


class ToolCall(BaseModel):
    tool_name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    result: Any = None
    timestamp: Optional[datetime] = None
    duration_ms: Optional[float] = None


class StateTransition(BaseModel):
    from_state: str
    to_state: str
    trigger: Optional[str] = None
    timestamp: Optional[datetime] = None


class TraceEvent(BaseModel):
    """Multi-agent trace event."""

    event_id: Optional[str] = None
    agent_id: str
    event_type: str  # "message", "tool_call", "claim", "delegation", "policy_check"
    parent_event_id: Optional[str] = None
    content: Dict[str, Any] = Field(default_factory=dict)
    timestamp: Optional[datetime] = None


class ModelMetadata(BaseModel):
    model_name: str
    provider: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    prompt_hash: Optional[str] = None
    config_hash: Optional[str] = None


class CostInfo(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0
    total_cost_usd: float = 0.0
    latency_ms: float = 0.0


class AgentRun(BaseModel):
    """Normalized output from any agent adapter.

    This is THE contract boundary — every scorer, statistical test,
    and reporter works exclusively from AgentRun instances.
    """

    run_id: str
    task_id: str
    final_answer: str
    claims: List[Claim] = Field(default_factory=list)
    evidence_spans: List[EvidenceSpan] = Field(default_factory=list)
    tool_calls: List[ToolCall] = Field(default_factory=list)
    state_transitions: List[StateTransition] = Field(default_factory=list)
    trace_events: List[TraceEvent] = Field(default_factory=list)
    model_metadata: Optional[ModelMetadata] = None
    cost: Optional[CostInfo] = None
    seed: Optional[int] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def content_hash(self) -> str:
        payload = self.model_dump_json(exclude={"run_id", "timestamp"})
        return hashlib.sha256(payload.encode()).hexdigest()[:16]


class EvalTask(BaseModel):
    """A single evaluation task."""

    task_id: str
    task_type: str  # "rag", "tool", "coding", "multi_agent", "adversarial"
    prompt: str
    reference_answer: Optional[str] = None
    reference_claims: List[Claim] = Field(default_factory=list)
    context_documents: List[Dict[str, Any]] = Field(default_factory=list)
    expected_tool_calls: List[ToolCall] = Field(default_factory=list)
    expected_terminal_state: Optional[str] = None
    forbidden_actions: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EvalSuite(BaseModel):
    """A collection of evaluation tasks loaded from YAML or created dynamically."""

    name: str
    description: str = ""
    version: str = "1.0"
    tasks: List[EvalTask] = Field(default_factory=list)
    config: Dict[str, Any] = Field(default_factory=dict)
    dataset_revision: Optional[str] = None


class ScorerResult(BaseModel):
    """Output result from scoring an AgentRun against an EvalTask."""

    scorer_name: str
    passed: Optional[bool] = None
    score: Optional[float] = None
    details: Dict[str, Any] = Field(default_factory=dict)
    claims: List[Claim] = Field(default_factory=list)
    metrics: Dict[str, float] = Field(default_factory=dict)
