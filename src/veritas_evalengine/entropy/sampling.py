"""Stochastic Sampling for Semantic Entropy (Capability 2)."""

from __future__ import annotations

import random
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SampleResult(BaseModel):
    text: str
    log_probs: List[float] = Field(default_factory=list)
    temperature: float = 0.7


class StochasticSampler:
    """Generates N completions at temperature T for a prompt."""

    def __init__(self, num_samples: int = 5, temperature: float = 0.7, provider: str = "mock"):
        self.num_samples = num_samples
        self.temperature = temperature
        self.provider = provider

    def sample(self, prompt: str, candidates: Optional[List[str]] = None) -> List[SampleResult]:
        if candidates and len(candidates) >= self.num_samples:
            return [SampleResult(text=c, temperature=self.temperature) for c in candidates[: self.num_samples]]

        # Mock generator for offline execution
        results = []
        base_responses = [
            f"The capital of France is Paris.",
            f"Paris is the capital of France.",
            f"France's capital city is Paris.",
            f"The capital city of France is Paris.",
            f"Paris serves as the capital of France.",
        ]
        for i in range(self.num_samples):
            text = base_responses[i % len(base_responses)]
            results.append(SampleResult(text=text, log_probs=[-0.1 * (i + 1)], temperature=self.temperature))
        return results
