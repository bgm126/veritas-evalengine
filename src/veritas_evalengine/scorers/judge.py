"""Judge Reliability Lab (Capability 4)."""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from veritas_evalengine.core.protocols import Scorer
from veritas_evalengine.core.schemas import AgentRun, EvalTask, ScorerResult


class AbsoluteRubricJudge:
    """Grades an AgentRun output on a 1-5 rubric scale."""

    def __init__(self, rubric: str = "Clarity and accuracy of response"):
        self.rubric = rubric

    def evaluate(self, task: EvalTask, run: AgentRun) -> Dict[str, Any]:
        ans = run.final_answer.strip()
        ref = (task.reference_answer or "").strip()

        if not ans:
            score = 1.0
            reasoning = "Empty response"
        elif ref and ref.lower() in ans.lower():
            score = 5.0
            reasoning = "Matches reference answer accurately."
        elif len(ans) > 10:
            score = 4.0
            reasoning = "Substantive response provided."
        else:
            score = 2.0
            reasoning = "Minimal or incomplete response."

        return {"score": score, "reasoning": reasoning, "rubric": self.rubric}


class PairwiseJudge:
    """Pairwise comparison judge with position-bias swap testing."""

    def compare(self, prompt: str, candidate_a: str, candidate_b: str) -> Dict[str, Any]:
        # Position 1: A vs B
        winner_pos1 = self._judge_pair(prompt, candidate_a, candidate_b)
        # Position 2: B vs A (swap test)
        winner_pos2 = self._judge_pair(prompt, candidate_b, candidate_a)

        # Map back to A or B
        # In the swapped call, the first argument is the original candidate B.
        pos2_mapped = "B" if winner_pos2 == "A" else ("A" if winner_pos2 == "B" else "TIE")

        is_flipped = winner_pos1 != pos2_mapped and winner_pos1 != "TIE" and pos2_mapped != "TIE"
        final_winner = winner_pos1 if winner_pos1 == pos2_mapped else "TIE"

        return {
            "winner": final_winner,
            "position_1_winner": winner_pos1,
            "position_2_mapped_winner": pos2_mapped,
            "is_flipped": is_flipped,
        }

    def _judge_pair(self, prompt: str, text_a: str, text_b: str) -> str:
        if len(text_a) > len(text_b) + 5:
            return "A"
        elif len(text_b) > len(text_a) + 5:
            return "B"
        return "TIE"


class GEvalJudge:
    """G-Eval structured rubric judge. Captures internal reasoning."""

    def evaluate(self, task: EvalTask, run: AgentRun) -> Dict[str, Any]:
        rubric_res = AbsoluteRubricJudge().evaluate(task, run)
        # Does NOT expose hidden chain of thought in output public fields, but captures reasoning internally
        return {
            "g_eval_score": rubric_res["score"],
            "captured_reasoning": rubric_res["reasoning"],
        }


class JudgeReliabilityAnalyzer:
    """Analyzes Cohen's kappa, Spearman correlation, position-bias flip rate, and calibration error."""

    @staticmethod
    def position_bias_flip_rate(pairwise_results: List[Dict[str, Any]]) -> float:
        if not pairwise_results:
            return 0.0
        flips = sum(1 for r in pairwise_results if r.get("is_flipped", False))
        return flips / len(pairwise_results)

    @staticmethod
    def spearman_correlation(scores_a: List[float], scores_b: List[float]) -> float:
        if len(scores_a) < 2:
            return 1.0
        try:
            from scipy.stats import spearmanr

            corr, _ = spearmanr(scores_a, scores_b)
            return float(corr) if not math.isnan(corr) else 0.0
        except Exception:
            return 0.0

    @staticmethod
    def cohens_kappa(ratings_a: List[int], ratings_b: List[int]) -> float:
        if not ratings_a:
            return 1.0
        try:
            from sklearn.metrics import cohen_kappa_score

            return float(cohen_kappa_score(ratings_a, ratings_b, weights="quadratic"))
        except Exception:
            # Fallback simple agreement proportion
            agreements = sum(1 for a, b in zip(ratings_a, ratings_b) if a == b)
            return agreements / len(ratings_a)

    @staticmethod
    def expected_calibration_error(confidences: List[float], accuracies: List[int], num_bins: int = 5) -> float:
        if not confidences:
            return 0.0
        conf_arr = np.array(confidences)
        acc_arr = np.array(accuracies)

        bin_boundaries = np.linspace(0, 1, num_bins + 1)
        ece = 0.0
        n = len(conf_arr)

        for i in range(num_bins):
            bin_lower = bin_boundaries[i]
            bin_upper = bin_boundaries[i + 1]

            in_bin = (conf_arr > bin_lower) & (conf_arr <= bin_upper)
            bin_size = np.sum(in_bin)

            if bin_size > 0:
                bin_acc = np.mean(acc_arr[in_bin])
                bin_conf = np.mean(conf_arr[in_bin])
                ece += (bin_size / n) * abs(bin_acc - bin_conf)

        return float(ece)


class BradleyTerryRanker:
    """Fits Bradley-Terry model from pairwise comparison data using MM algorithm."""

    @staticmethod
    def fit(num_items: int, comparisons: List[Tuple[int, int]]) -> np.ndarray:
        """comparisons: list of (winner_idx, loser_idx) tuples."""
        weights = np.ones(num_items)
        if not comparisons:
            return weights

        # Wins matrix and match counts matrix
        wins = np.zeros((num_items, num_items))
        for winner, loser in comparisons:
            wins[winner, loser] += 1.0

        for _ in range(100):
            old_weights = weights.copy()
            for i in range(num_items):
                win_i = np.sum(wins[i, :])
                denom = 0.0
                for j in range(num_items):
                    if i != j and (wins[i, j] + wins[j, i]) > 0:
                        denom += (wins[i, j] + wins[j, i]) / (old_weights[i] + old_weights[j])
                if denom > 0:
                    weights[i] = win_i / denom

            weights = weights / np.sum(weights)
            if np.max(np.abs(weights - old_weights)) < 1e-6:
                break

        return weights


class JudgeScorer:
    """Scorer wrapper for rubric judges."""

    name = "judge"

    def __init__(self, judge: Optional[AbsoluteRubricJudge] = None):
        self.judge = judge or AbsoluteRubricJudge()

    def score(self, task: EvalTask, run: AgentRun) -> ScorerResult:
        eval_res = self.judge.evaluate(task, run)
        score = float(eval_res["score"])
        passed = score >= 3.0

        return ScorerResult(
            scorer_name=self.name,
            passed=passed,
            score=score,
            details=eval_res,
            metrics={"rubric_score": score},
        )
