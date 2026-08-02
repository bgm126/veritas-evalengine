"""Drift and Instruction-Adherence Monitor (Capability 5)."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from veritas_evalengine.core.protocols import Scorer
from veritas_evalengine.core.schemas import AgentRun, EvalTask, ScorerResult


class RunHistory:
    """JSONL-backed local run history."""

    def __init__(self, history_file: str | Path = "run_history.jsonl"):
        self.history_file = Path(history_file)

    def append(self, metric_name: str, value: float, run_id: str) -> None:
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        entry = {"metric_name": metric_name, "value": value, "run_id": run_id}
        with open(self.history_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    def get_series(self, metric_name: str) -> List[float]:
        if not self.history_file.exists():
            return []
        values = []
        with open(self.history_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    if data.get("metric_name") == metric_name:
                        values.append(float(data.get("value", 0.0)))
        return values


class PSIDetector:
    """Population Stability Index calculation."""

    @staticmethod
    def calculate(reference: List[float], current: List[float], num_bins: int = 5) -> float:
        if not reference or not current:
            return 0.0
        ref_arr = np.array(reference)
        curr_arr = np.array(current)

        bins = np.linspace(min(ref_arr.min(), curr_arr.min()), max(ref_arr.max(), curr_arr.max()), num_bins + 1)
        ref_counts, _ = np.histogram(ref_arr, bins=bins)
        curr_counts, _ = np.histogram(curr_arr, bins=bins)

        ref_pct = (ref_counts + 1e-5) / (len(ref_arr) + 1e-5 * num_bins)
        curr_pct = (curr_counts + 1e-5) / (len(curr_arr) + 1e-5 * num_bins)

        psi_val = np.sum((curr_pct - ref_pct) * np.log(curr_pct / ref_pct))
        return float(psi_val)


class EWMADetector:
    """Exponentially Weighted Moving Average detector."""

    @staticmethod
    def calculate(series: List[float], alpha: float = 0.3) -> float:
        if not series:
            return 0.0
        ewma = series[0]
        for val in series[1:]:
            ewma = alpha * val + (1 - alpha) * ewma
        return float(ewma)


class CUSUMDetector:
    """Cumulative Sum change-point detector."""

    @staticmethod
    def detect(series: List[float], target: float = 1.0, threshold: float = 1.5, drift: float = 0.1) -> Tuple[bool, float]:
        if not series:
            return False, 0.0
        s_hi = 0.0
        s_lo = 0.0
        max_s = 0.0

        for x in series:
            s_hi = max(0.0, s_hi + (target - x - drift))
            s_lo = max(0.0, s_lo + (x - target - drift))
            max_s = max(max_s, s_hi, s_lo)
            if s_hi >= threshold or s_lo >= threshold:
                return True, max_s

        return False, max_s


class EmbeddingDistanceDetector:
    """Calculates cosine distance between text outputs."""

    @staticmethod
    def distance(text_a: str, text_b: str) -> float:
        words_a = set(text_a.lower().split())
        words_b = set(text_b.lower().split())
        all_words = words_a.union(words_b)
        if not all_words:
            return 0.0
        vec_a = np.array([1 if w in words_a else 0 for w in all_words])
        vec_b = np.array([1 if w in words_b else 0 for w in all_words])

        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)
        if norm_a == 0 or norm_b == 0:
            return 1.0
        cos_sim = np.dot(vec_a, vec_b) / (norm_a * norm_b)
        return float(1.0 - cos_sim)


class BootstrapDriftCI:
    """Bootstrap confidence intervals for drift metrics."""

    @staticmethod
    def compute_ci(data: List[float], num_bootstraps: int = 500, alpha: float = 0.05) -> Tuple[float, float]:
        if not data:
            return (0.0, 0.0)
        arr = np.array(data)
        means = []
        n = len(arr)
        for _ in range(num_bootstraps):
            sample = np.random.choice(arr, size=n, replace=True)
            means.append(float(np.mean(sample)))

        low = float(np.percentile(means, 100 * (alpha / 2)))
        high = float(np.percentile(means, 100 * (1 - alpha / 2)))
        return (low, high)


class InstructionViolationStream:
    """Held-out synthetic stream for validating detector performance."""

    def __init__(self, reference_length: int = 20, violation_rate: float = 0.2):
        self.reference_length = reference_length
        self.violation_rate = violation_rate

    def generate_stream(self) -> List[float]:
        series = [1.0] * self.reference_length
        for _ in range(10):
            val = 0.0 if np.random.rand() < self.violation_rate else 1.0
            series.append(val)
        return series


class DriftScorer:
    """Scorer for drift and instruction adherence monitoring."""

    name = "drift"

    def __init__(self, history: Optional[RunHistory] = None):
        self.history = history or RunHistory()

    def score(self, task: EvalTask, run: AgentRun) -> ScorerResult:
        ref_text = task.reference_answer or ""
        dist = EmbeddingDistanceDetector.distance(run.final_answer, ref_text) if ref_text else 0.0
        adherence_score = max(0.0, 1.0 - dist)

        self.history.append("adherence", adherence_score, run.run_id)
        series = self.history.get_series("adherence")

        psi_val = PSIDetector.calculate(series[:10], series[-10:]) if len(series) >= 20 else 0.0
        ewma_val = EWMADetector.calculate(series) if series else adherence_score
        cusum_alarm, cusum_score = CUSUMDetector.detect(series) if series else (False, 0.0)

        passed = not cusum_alarm and psi_val < 0.25

        metrics = {
            "adherence_score": adherence_score,
            "psi": psi_val,
            "ewma": ewma_val,
            "cusum_score": cusum_score,
            "cusum_alarm": 1.0 if cusum_alarm else 0.0,
        }

        return ScorerResult(
            scorer_name=self.name,
            passed=passed,
            score=adherence_score,
            details={"cusum_alarm": cusum_alarm, "series_length": len(series)},
            metrics=metrics,
        )
