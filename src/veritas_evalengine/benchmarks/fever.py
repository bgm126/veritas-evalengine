"""FEVER benchmark adapter."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from veritas_evalengine.core.schemas import Claim, ClaimVerdict, EvalSuite, EvalTask


class FEVERBenchmark:
    """FEVER fact-verification benchmark adapter."""

    name = "fever"

    def load_suite(self, limit: Optional[int] = None) -> EvalSuite:
        sample_data = [
            {
                "claim": "Roman Atwood is a YouTuber.",
                "label": "SUPPORTS",
            },
            {
                "claim": "History of Art was created in 1900.",
                "label": "REFUTES",
            },
        ]

        if limit:
            sample_data = sample_data[:limit]

        tasks: List[EvalTask] = []
        for idx, item in enumerate(sample_data):
            verdict = ClaimVerdict.SUPPORTED if item["label"] == "SUPPORTS" else ClaimVerdict.CONTRADICTED
            ref_claim = Claim(text=item["claim"], verdict=verdict)

            tasks.append(
                EvalTask(
                    task_id=f"fever-{idx+1}",
                    task_type="rag",
                    prompt=f"Verify claim: {item['claim']}",
                    reference_claims=[ref_claim],
                    tags=["benchmark", "fever"],
                )
            )

        return EvalSuite(
            name=self.name,
            description="FEVER fact verification benchmark",
            tasks=tasks,
            dataset_revision="v1.0",
        )
