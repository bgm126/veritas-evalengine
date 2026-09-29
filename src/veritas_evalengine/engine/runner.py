"""Main evaluation runner for Veritas EvalEngine."""

from __future__ import annotations

import random
from typing import Any, Sequence
from veritas_evalengine.core.config import EvalConfig
from veritas_evalengine.core.policy import PolicyEngine, ReleasePolicy
from veritas_evalengine.core.protocols import AgentAdapter, Scorer
from veritas_evalengine.core.schemas import AgentRun, EvalSuite, EvalTask, ScorerResult
from veritas_evalengine.engine.report_types import EvalReport, EvalTaskResult
from veritas_evalengine.engine.registry import AdapterRegistry, ScorerRegistry


class EvalRunner:
    """Executes evaluation tasks, invokes scorers, and evaluates release policy."""

    def __init__(
        self,
        adapter: AgentAdapter | None = None,
        scorers: Sequence[Scorer] | None = None,
        policy: ReleasePolicy | None = None,
        config: EvalConfig | None = None,
    ):
        self.adapter = adapter
        self.scorers = list(scorers) if scorers else []
        self.policy = policy
        self.config = config or EvalConfig()

    def run_suite(self, suite: EvalSuite, reps: int = 1, seed: int | None = 42) -> EvalReport:
        if reps < 1:
            raise ValueError("reps must be at least 1")
        if seed is not None:
            random.seed(seed)

        adapter = self.adapter
        if adapter is None and self.config.runner.adapter_class:
            adapter = AdapterRegistry.get(self.config.runner.adapter_class, **self.config.runner.adapter_params)

        if adapter is None:
            raise ValueError("No agent adapter provided to EvalRunner")

        task_results: list[EvalTaskResult] = []
        aggregated_metrics: dict[str, float] = {}

        total_tasks = len(suite.tasks)
        passed_tasks = 0
        failed_tasks = 0

        for task in suite.tasks:
            runs: list[AgentRun] = []
            scorer_results: list[ScorerResult] = []
            task_passed = True
            task_metric_samples: dict[str, list[float]] = {}

            for rep in range(reps):
                if seed is not None:
                    task_seed = seed + rep
                else:
                    task_seed = None

                run = adapter.run(task)
                run.seed = task_seed
                runs.append(run)

                for scorer in self.scorers:
                    try:
                        res = scorer.score(task, run)
                        scorer_results.append(res)
                        if res.passed is False:
                            task_passed = False

                        for m_key, m_val in res.metrics.items():
                            full_key = f"{scorer.name}.{m_key}"
                            task_metric_samples.setdefault(full_key, []).append(float(m_val))
                    except Exception as e:
                        err_res = ScorerResult(
                            scorer_name=scorer.name,
                            passed=False,
                            score=0.0,
                            details={"error": str(e)},
                        )
                        scorer_results.append(err_res)
                        task_passed = False

            if task_passed:
                passed_tasks += 1
            else:
                failed_tasks += 1

            task_metrics = {
                key: sum(values) / len(values)
                for key, values in task_metric_samples.items()
                if values
            }

            task_results.append(
                EvalTaskResult(
                    task_id=task.task_id,
                    task_type=task.task_type,
                    runs=runs,
                    scorer_results=scorer_results,
                    passed=task_passed,
                    metrics=task_metrics,
                )
            )

        # Compute aggregated summary metrics
        aggregated_metrics["pass_rate"] = passed_tasks / total_tasks if total_tasks > 0 else 0.0
        aggregated_metrics["total_tasks"] = float(total_tasks)
        aggregated_metrics["passed_tasks"] = float(passed_tasks)
        aggregated_metrics["failed_tasks"] = float(failed_tasks)
        aggregated_metrics["deterministic_failure_count"] = float(failed_tasks)

        # Collect metrics from individual scorers into aggregated metrics
        all_metrics: dict[str, list[float]] = {}
        for tr in task_results:
            for k, v in tr.metrics.items():
                all_metrics.setdefault(k, []).append(v)

        for k, values in all_metrics.items():
            if values:
                aggregated_metrics[k] = sum(values) / len(values)

        # Evaluate policy if available
        policy_verdict = None
        if self.policy:
            engine = PolicyEngine(self.policy)
            policy_verdict = engine.evaluate(aggregated_metrics)

        return EvalReport(
            suite_name=suite.name,
            total_tasks=total_tasks,
            passed_tasks=passed_tasks,
            failed_tasks=failed_tasks,
            policy_verdict=policy_verdict,
            task_results=task_results,
            aggregated_metrics=aggregated_metrics,
        )
