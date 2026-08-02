"""Stress Test Suite Runner (Phase 4)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from veritas_evalengine.core.protocols import AgentAdapter
from veritas_evalengine.core.schemas import EvalSuite, EvalTask
from veritas_evalengine.engine.report_types import EvalReport
from veritas_evalengine.engine.runner import EvalRunner
from veritas_evalengine.scorers.evidence import wilson_score_interval
from veritas_evalengine.scorers.fidelity import PolicyAdherenceScorer
from veritas_evalengine.stress.generators import (
    ContradictorySourceGenerator,
    ForbiddenActionGenerator,
    InstructionConflictGenerator,
    MissingInfoGenerator,
    MultiTurnJailbreakGenerator,
    PoisonedDocGenerator,
    PoisonedToolGenerator,
    PromptInjectionGenerator,
)


class StressRunner:
    """Executes stress test suites against an agent adapter and summarizes attack success rates."""

    def __init__(self, adapter: AgentAdapter):
        self.adapter = adapter
        self.generators = {
            "missing_info": MissingInfoGenerator(),
            "contradictory_sources": ContradictorySourceGenerator(),
            "poisoned_doc": PoisonedDocGenerator(),
            "poisoned_tool": PoisonedToolGenerator(),
            "instruction_conflict": InstructionConflictGenerator(),
            "prompt_injection": PromptInjectionGenerator(),
            "jailbreak": MultiTurnJailbreakGenerator(),
            "forbidden_action": ForbiddenActionGenerator(),
        }

    def run_all_families(self, n_per_family: int = 2) -> Dict[str, Any]:
        family_results: Dict[str, Dict[str, Any]] = {}

        for family_name, gen in self.generators.items():
            tasks: List[EvalTask] = [gen.generate(seed=100 + i) for i in range(n_per_family)]
            suite = EvalSuite(name=f"stress_{family_name}", tasks=tasks)

            runner = EvalRunner(adapter=self.adapter, scorers=[PolicyAdherenceScorer()])
            report = runner.run_suite(suite)

            attacks_succeeded = report.failed_tasks
            total_tasks = report.total_tasks

            lcb, ucb = wilson_score_interval(attacks_succeeded, total_tasks)

            family_results[family_name] = {
                "total_attacks": total_tasks,
                "attacks_succeeded": attacks_succeeded,
                "attack_success_rate": attacks_succeeded / total_tasks if total_tasks > 0 else 0.0,
                "wilson_lcb": lcb,
                "wilson_ucb": ucb,
            }

        return family_results
