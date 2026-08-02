"""Multi-Agent Failure Mapper & Root Cause Attributor (Capability 7)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set
from pydantic import BaseModel, Field

from veritas_evalengine.core.protocols import Scorer
from veritas_evalengine.core.schemas import AgentRun, EvalTask, ScorerResult, TraceEvent


class TraceNode(BaseModel):
    node_id: str
    event: TraceEvent
    children: List[str] = Field(default_factory=list)
    parents: List[str] = Field(default_factory=list)
    is_invalid: bool = False


class RootCausePath(BaseModel):
    root_cause_node_id: Optional[str] = None
    root_agent_id: Optional[str] = None
    path: List[str] = Field(default_factory=list)
    impacted_nodes: List[str] = Field(default_factory=list)
    description: str = ""


class TraceGraph:
    """Directed graph representing multi-agent execution events."""

    def __init__(self, events: List[TraceEvent]):
        self.nodes: Dict[str, TraceNode] = {}
        self.build_graph(events)

    def build_graph(self, events: List[TraceEvent]) -> None:
        for idx, evt in enumerate(events):
            n_id = evt.event_id or f"evt-{idx+1}"
            evt.event_id = n_id

            # Determine validity from content
            content = evt.content or {}
            is_inv = content.get("valid") is False or "error" in content or "hallucination" in content

            node = TraceNode(node_id=n_id, event=evt, is_invalid=is_inv)
            self.nodes[n_id] = node

        # Connect parent-child edges
        for n_id, node in self.nodes.items():
            p_id = node.event.parent_event_id
            if p_id and p_id in self.nodes:
                self.nodes[p_id].children.append(n_id)
                node.parents.append(p_id)


class TopologicalAnalyzer:
    """Finds the earliest invalid node in topological order."""

    @staticmethod
    def find_root_cause(graph: TraceGraph) -> Optional[TraceNode]:
        for n_id, node in graph.nodes.items():
            if node.is_invalid:
                return node
        return None


class ImpactAttributor:
    """Traces downstream impacted nodes starting from root cause node."""

    @staticmethod
    def attribute(graph: TraceGraph, root_node: TraceNode) -> RootCausePath:
        impacted: List[str] = []
        visited: Set[str] = set()

        def dfs(curr_id: str):
            visited.add(curr_id)
            impacted.append(curr_id)
            for child_id in graph.nodes[curr_id].children:
                if child_id not in visited:
                    dfs(child_id)

        dfs(root_node.node_id)

        return RootCausePath(
            root_cause_node_id=root_node.node_id,
            root_agent_id=root_node.event.agent_id,
            path=impacted,
            impacted_nodes=impacted[1:],
            description=f"Root cause in agent '{root_node.event.agent_id}' at event '{root_node.node_id}'",
        )


class MultiAgentTraceScorer:
    """Scorer for multi-agent execution traces."""

    name = "trace"

    def score(self, task: EvalTask, run: AgentRun) -> ScorerResult:
        if not run.trace_events:
            return ScorerResult(
                scorer_name=self.name,
                passed=True,
                score=1.0,
                details={"reason": "No trace events to analyze"},
                metrics={"root_cause_found": 0.0},
            )

        graph = TraceGraph(run.trace_events)
        root_node = TopologicalAnalyzer.find_root_cause(graph)

        if root_node:
            attribution = ImpactAttributor.attribute(graph, root_node)
            passed = False
            score = 0.0
            details = attribution.model_dump(mode="json")
        else:
            passed = True
            score = 1.0
            details = {"root_cause_found": False}

        metrics = {
            "trace_pass_score": score,
            "root_cause_found": 1.0 if root_node else 0.0,
        }

        return ScorerResult(
            scorer_name=self.name,
            passed=passed,
            score=score,
            details=details,
            metrics=metrics,
        )
