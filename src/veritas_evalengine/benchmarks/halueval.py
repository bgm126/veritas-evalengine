"""HaluEval benchmark adapter."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from veritas_evalengine.core.schemas import EvalSuite, EvalTask


class HaluEvalBenchmark:
    """HaluEval dataset benchmark adapter."""

    name = "halueval"

    def load_suite(self, limit: Optional[int] = None) -> EvalSuite:
        sample_data = [
            {
                "question": "Where was Albert Einstein born?",
                "right_answer": "Albert Einstein was born in Ulm, Germany.",
                "hallucinated_answer": "Albert Einstein was born in Zurich, Switzerland.",
            }
        ]

        if limit:
            sample_data = sample_data[:limit]

        tasks: List[EvalTask] = []
        for idx, item in enumerate(sample_data):
            tasks.append(
                EvalTask(
                    task_id=f"halueval-{idx+1}",
                    task_type="rag",
                    prompt=item["question"],
                    reference_answer=item["right_answer"],
                    metadata={"hallucinated_answer": item["hallucinated_answer"]},
                    tags=["benchmark", "halueval"],
                )
            )

        return EvalSuite(
            name=self.name,
            description="HaluEval benchmark tasks",
            tasks=tasks,
            dataset_revision="v1.0",
        )
