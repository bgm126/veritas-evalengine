"""Tests for entailment clustering and semantic entropy."""

from veritas_evalengine.entropy.clustering import EntailmentClusterer, SemanticEntropyCalculator
from veritas_evalengine.entropy.sampling import SampleResult


def test_entailment_clustering_and_entropy():
    samples = [
        SampleResult(text="Paris is the capital of France."),
        SampleResult(text="The capital of France is Paris."),
        SampleResult(text="France's capital city is Paris."),
    ]

    clusterer = EntailmentClusterer()
    clusters = clusterer.cluster(samples)
    assert len(clusters) >= 1

    entropy_res = SemanticEntropyCalculator.calculate(clusters, len(samples))
    assert "semantic_entropy" in entropy_res
    assert entropy_res["semantic_entropy"] >= 0.0
