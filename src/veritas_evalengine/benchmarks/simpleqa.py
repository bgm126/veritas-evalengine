"""SimpleQA benchmark adapter."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from veritas_evalengine.core.schemas import EvalSuite, EvalTask


class SimpleQABenchmark:
    """SimpleQA factuality benchmark adapter."""

    name = "simple_qa"

    def load_suite(self, limit: Optional[int] = None) -> EvalSuite:
        sample_data = [
            {
                "question": "What is the chemical symbol for Gold?",
                "answer": "Au",
            }
        ]

        if limit:
            sample_data = sample_data[:limit]

        tasks: List[EvalTask] = []
        for idx, item in enumerate(sample_data):
            tasks.append(
                EvalTask(
                    task_id=f"simpleqa-{idx+1}",
                    task_type="rag",
                    prompt=item["question"],
                    reference_answer=item["answer"],
                    tags=["benchmark", "simple_qa"],
                )
            )

        return EvalSuite(
            name=self.name,
            description="SimpleQA factuality benchmark",
            tasks=tasks,
            dataset_revision="v1.0",
        )
