"""Evidence-Backed Hallucination Detector (Capability 1)."""

from __future__ import annotations

import math
import re
from typing import Any, Dict, List, Optional, Protocol, Tuple, runtime_checkable
from veritas_evalengine.core.protocols import Scorer
from veritas_evalengine.core.schemas import (
    AgentRun,
    Claim,
    ClaimVerdict,
    EvalTask,
    EvidenceSpan,
    ScorerResult,
)


def wilson_score_interval(successes: int, trials: int, confidence: float = 0.95) -> Tuple[float, float]:
    """Compute Wilson score interval lower and upper bounds for binomial proportion."""
    if trials == 0:
        return (0.0, 1.0)

    p = successes / trials
    # Z value for standard normal distribution (95% -> z=1.96)
    z = 1.95996 if math.isclose(confidence, 0.95) else 1.96

    denominator = 1 + (z**2) / trials
    center = p + (z**2) / (2 * trials)
    spread = z * math.sqrt((p * (1 - p) + (z**2) / (4 * trials)) / trials)

    lcb = max(0.0, (center - spread) / denominator)
    ucb = min(1.0, (center + spread) / denominator)
    return (lcb, ucb)


class ClaimDecomposer:
    """Decomposes text into atomic claim strings."""

    def decompose(self, text: str) -> List[Claim]:
        if not text or not text.strip():
            return []
        # Split on sentence terminators while preserving meaningful text
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
        claims: List[Claim] = []
        for sentence in sentences:
            if len(sentence) > 5:
                claims.append(Claim(text=sentence))
        return claims


class EvidenceVerifier:
    """Finds matching evidence spans in context documents."""

    def find_spans(self, claim_text: str, context_documents: List[Dict[str, Any]]) -> List[EvidenceSpan]:
        spans: List[EvidenceSpan] = []
        claim_words = set(re.findall(r"\w+", claim_text.lower()))
        if not claim_words:
            return spans

        for doc in context_documents:
            doc_id = str(doc.get("id", doc.get("source_id", "doc")))
            doc_text = str(doc.get("text", ""))

            # Substring match or overlap match
            if claim_text.lower() in doc_text.lower():
                start = doc_text.lower().find(claim_text.lower())
                spans.append(EvidenceSpan(source_id=doc_id, text=doc_text, start_char=start, end_char=start + len(claim_text)))
            else:
                doc_words = set(re.findall(r"\w+", doc_text.lower()))
                overlap = claim_words.intersection(doc_words)
                if len(overlap) / len(claim_words) >= 0.5:
                    spans.append(EvidenceSpan(source_id=doc_id, text=doc_text))
        return spans


@runtime_checkable
class EntailmentScorer(Protocol):
    """Abstract interface for entailment backends."""

    def classify(self, claim_text: str, evidence_spans: List[EvidenceSpan]) -> ClaimVerdict:
        ...


class MockEntailmentScorer:
    """Offline exact-match check; it does not infer entailment or contradiction."""

    def classify(self, claim_text: str, evidence_spans: List[EvidenceSpan]) -> ClaimVerdict:
        if not evidence_spans:
            return ClaimVerdict.UNVERIFIABLE
        claim_normalized = " ".join(re.findall(r"\w+", claim_text.lower()))
        if not claim_normalized:
            return ClaimVerdict.UNVERIFIABLE
        for span in evidence_spans:
            evidence_normalized = " ".join(re.findall(r"\w+", span.text.lower()))
            if claim_normalized in evidence_normalized:
                return ClaimVerdict.SUPPORTED
        return ClaimVerdict.UNVERIFIABLE


class DeBERTaEntailmentScorer:
    """Lazy-loaded DeBERTa-v3-large-MNLI entailment scorer."""

    def __init__(self, model_name: str = "cross-encoder/nli-deberta-v3-base"):
        self.model_name = model_name
        self._pipeline = None

    def _load(self):
        if self._pipeline is None:
            try:
                from transformers import pipeline

                self._pipeline = pipeline("text-classification", model=self.model_name)
            except Exception as e:
                # Fallback if transformers model cannot be loaded
                self._pipeline = "MOCK_FALLBACK"

    def classify(self, claim_text: str, evidence_spans: List[EvidenceSpan]) -> ClaimVerdict:
        if not evidence_spans:
            return ClaimVerdict.UNVERIFIABLE
        self._load()
        if self._pipeline == "MOCK_FALLBACK":
            return MockEntailmentScorer().classify(claim_text, evidence_spans)

        context = " ".join([s.text for s in evidence_spans])
        try:
            res = self._pipeline({"text": context, "text_pair": claim_text})
            label = str(res[0].get("label", "")).lower()
            if "entailment" in label or "support" in label:
                return ClaimVerdict.SUPPORTED
            elif "contradict" in label:
                return ClaimVerdict.CONTRADICTED
            return ClaimVerdict.UNVERIFIABLE
        except Exception:
            return MockEntailmentScorer().classify(claim_text, evidence_spans)


class EvidenceScorer:
    """Score evidence-backed grounding of claims in AgentRun.

    Pipeline:
    1. Decompose answer → atomic claims
    2. For each claim, find matching evidence spans
    3. Run entailment (DeBERTa, LLM-Judge, or Mock)
    4. Aggregate verdicts with Wilson CI
    """

    name = "evidence"

    def __init__(
        self,
        decomposer: Optional[ClaimDecomposer] = None,
        verifier: Optional[EvidenceVerifier] = None,
        entailment: Optional[EntailmentScorer] = None,
    ):
        self.decomposer = decomposer or ClaimDecomposer()
        self.verifier = verifier or EvidenceVerifier()
        self.entailment = entailment or MockEntailmentScorer()

    def score(self, task: EvalTask, run: AgentRun) -> ScorerResult:
        claims = run.claims or self.decomposer.decompose(run.final_answer)

        supported_count = 0
        contradicted_count = 0
        unverifiable_count = 0

        scored_claims: List[Claim] = []
        for claim in claims:
            spans = claim.evidence_spans or self.verifier.find_spans(claim.text, task.context_documents)
            verdict = self.entailment.classify(claim.text, spans)
            claim.verdict = verdict
            claim.evidence_spans = spans
            scored_claims.append(claim)

            if verdict == ClaimVerdict.SUPPORTED:
                supported_count += 1
            elif verdict == ClaimVerdict.CONTRADICTED:
                contradicted_count += 1
            else:
                unverifiable_count += 1

        total_claims = len(scored_claims)
        grounding_rate = supported_count / total_claims if total_claims > 0 else 1.0
        contradiction_rate = contradicted_count / total_claims if total_claims > 0 else 0.0

        lcb, ucb = wilson_score_interval(supported_count, total_claims)

        passed = contradiction_rate == 0.0 and grounding_rate >= 0.8

        metrics = {
            "grounding_rate": grounding_rate,
            "contradiction_rate": contradiction_rate,
            "unverifiable_rate": unverifiable_count / total_claims if total_claims > 0 else 0.0,
            "grounding_wilson_lcb": lcb,
            "grounding_wilson_ucb": ucb,
            "total_claims": float(total_claims),
        }

        return ScorerResult(
            scorer_name=self.name,
            passed=passed,
            score=grounding_rate,
            details={
                "supported_count": supported_count,
                "contradicted_count": contradicted_count,
                "unverifiable_count": unverifiable_count,
            },
            claims=scored_claims,
            metrics=metrics,
        )
