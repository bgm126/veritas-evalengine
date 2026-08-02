"""Entailment Clustering and Semantic Entropy Calculation (Capability 2)."""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional
from veritas_evalengine.core.schemas import ClaimVerdict, EvidenceSpan
from veritas_evalengine.entropy.sampling import SampleResult
from veritas_evalengine.scorers.evidence import EntailmentScorer, MockEntailmentScorer


class SemanticCluster:
    def __init__(self, cluster_id: int, representative: str):
        self.cluster_id = cluster_id
        self.representative = representative
        self.members: List[str] = [representative]

    def add_member(self, sample: str) -> None:
        self.members.append(sample)


class EntailmentClusterer:
    """Clusters N samples into semantic equivalence classes."""

    def __init__(self, entailment: Optional[EntailmentScorer] = None):
        self.entailment = entailment or MockEntailmentScorer()

    def cluster(self, samples: List[SampleResult]) -> List[SemanticCluster]:
        clusters: List[SemanticCluster] = []
        cluster_counter = 0

        for sample in samples:
            text = sample.text
            assigned = False
            for cluster in clusters:
                # Check bidirectional or unidirectional entailment match
                span = EvidenceSpan(source_id="sample", text=cluster.representative)
                verdict = self.entailment.classify(text, [span])
                if verdict == ClaimVerdict.SUPPORTED:
                    cluster.add_member(text)
                    assigned = True
                    break

            if not assigned:
                cluster_counter += 1
                clusters.append(SemanticCluster(cluster_id=cluster_counter, representative=text))

        return clusters


class SemanticEntropyCalculator:
    """Calculates Shannon semantic entropy across semantic clusters.

    H(X) = - Σ p(c) * log(p(c))
    """

    @staticmethod
    def calculate(clusters: List[SemanticCluster], total_samples: int) -> Dict[str, float]:
        if total_samples <= 0 or not clusters:
            return {"semantic_entropy": 0.0, "cluster_count": 0.0}

        entropy = 0.0
        probabilities: List[float] = []

        for cluster in clusters:
            p_c = len(cluster.members) / total_samples
            probabilities.append(p_c)
            if p_c > 0:
                entropy -= p_c * math.log(p_c)

        return {
            "semantic_entropy": entropy,
            "cluster_count": float(len(clusters)),
            "max_possible_entropy": math.log(total_samples) if total_samples > 1 else 0.0,
        }
