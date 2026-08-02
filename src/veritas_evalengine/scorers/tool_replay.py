"""Tool Replay Bench Scorer (Capability 3)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from veritas_evalengine.core.protocols import Scorer
from veritas_evalengine.core.schemas import AgentRun, EvalTask, ScorerResult, ToolCall


class ToolSpec(BaseModel):
    name: str
    description: str = ""
    input_schema: Dict[str, Any] = Field(default_factory=dict)
    output_schema: Dict[str, Any] = Field(default_factory=dict)
    side_effects: List[str] = Field(default_factory=list)
    idempotent: bool = True


class TraceReplayer:
    """Replays and validates tool-call traces."""

    def __init__(self, tool_specs: Optional[List[ToolSpec]] = None):
        self.tool_specs = {t.name: t for t in (tool_specs or [])}

    def replay_trace(self, expected_calls: List[ToolCall], actual_calls: List[ToolCall], forbidden_actions: List[str]) -> Dict[str, Any]:
        call_errors: List[str] = []
        forbidden_violations: List[str] = []

        # Check forbidden actions
        for call in actual_calls:
            if call.tool_name in forbidden_actions:
                forbidden_violations.append(f"Forbidden tool called: {call.tool_name}")

        # Check call order and matching tool names
        order_matched = True
        if len(actual_calls) < len(expected_calls):
            call_errors.append(f"Missing expected tool calls: expected {len(expected_calls)}, got {len(actual_calls)}")
            order_matched = False
        else:
            for idx, expected in enumerate(expected_calls):
                actual = actual_calls[idx]
                if actual.tool_name != expected.tool_name:
                    call_errors.append(f"Step {idx}: expected tool '{expected.tool_name}', got '{actual.tool_name}'")
                    order_matched = False
                elif expected.arguments:
                    for arg_k, arg_v in expected.arguments.items():
                        if actual.arguments.get(arg_k) != arg_v:
                            call_errors.append(
                                f"Step {idx} ({expected.tool_name}): argument mismatch for '{arg_k}' (expected {arg_v}, got {actual.arguments.get(arg_k)})"
                            )

        accuracy = 1.0 if (order_matched and not call_errors and not forbidden_violations) else 0.0
        return {
            "accuracy": accuracy,
            "order_matched": order_matched,
            "call_errors": call_errors,
            "forbidden_violations": forbidden_violations,
            "actual_call_count": len(actual_calls),
            "expected_call_count": len(expected_calls),
        }


class ToolReplayScorer:
    """Scorer for deterministic tool replay validation."""

    name = "tool_replay"

    def __init__(self, tool_specs: Optional[List[ToolSpec]] = None):
        self.replayer = TraceReplayer(tool_specs)

    def score(self, task: EvalTask, run: AgentRun) -> ScorerResult:
        replay_result = self.replayer.replay_trace(
            expected_calls=task.expected_tool_calls,
            actual_calls=run.tool_calls,
            forbidden_actions=task.forbidden_actions,
        )

        passed = replay_result["accuracy"] == 1.0 and len(replay_result["forbidden_violations"]) == 0
        if task.expected_terminal_state and run.state_transitions:
            last_state = run.state_transitions[-1].to_state
            if last_state != task.expected_terminal_state:
                passed = False
                replay_result["call_errors"].append(
                    f"Terminal state mismatch: expected {task.expected_terminal_state}, got {last_state}"
                )

        metrics = {
            "accuracy": float(replay_result["accuracy"]),
            "forbidden_violation_count": float(len(replay_result["forbidden_violations"])),
            "call_error_count": float(len(replay_result["call_errors"])),
        }

        return ScorerResult(
            scorer_name=self.name,
            passed=passed,
            score=replay_result["accuracy"],
            details=replay_result,
            metrics=metrics,
        )
