"""Tests for evidence scorer."""

from veritas_evalengine.core.schemas import AgentRun, Claim, ClaimVerdict, EvalTask, EvidenceSpan
from veritas_evalengine.scorers.evidence import ClaimDecomposer, EvidenceScorer, EvidenceVerifier, MockEntailmentScorer


def test_claim_decomposer():
    decomposer = ClaimDecomposer()
    claims = decomposer.decompose("Paris is the capital of France. It has a population of 2 million.")
    assert len(claims) == 2


def test_evidence_verifier():
    verifier = EvidenceVerifier()
    docs = [{"id": "doc1", "text": "Paris is the capital of France."}]
    spans = verifier.find_spans("Paris is the capital of France", docs)
    assert len(spans) == 1
    assert spans[0].source_id == "doc1"


def test_evidence_scorer(sample_task: EvalTask, sample_run: AgentRun):
    scorer = EvidenceScorer(entailment=MockEntailmentScorer())
    res = scorer.score(sample_task, sample_run)
    assert res.passed is True
    assert res.metrics["grounding_rate"] == 1.0
    assert "grounding_wilson_lcb" in res.metrics
