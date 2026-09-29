"""Simple baseline utilities for checking entropy predictions.

These helpers deliberately avoid pretending that an unvalidated hidden-state
probe can predict uncertainty. Train and validate a model-specific predictor
outside this package before using predictions in a release decision.
"""

from __future__ import annotations

from typing import Dict, List


class HiddenStateProbe:
    """Baseline predictor that returns the mean target seen during training."""

    def __init__(self, input_dim: int = 128):
        self.input_dim = input_dim
        self.mean_target = 0.0
        self.is_trained = False

    def predict(self, hidden_state) -> float:
        if not self.is_trained:
            raise RuntimeError("Probe has not been trained on labeled examples")
        return self.mean_target


class ProbeTrainer:
    """Fit a transparent constant baseline to labeled entropy observations."""

    def __init__(self, input_dim: int = 128, lr: float = 0.01):
        self.input_dim = input_dim

    def train(self, hidden_states, target_entropies, epochs: int = 50) -> HiddenStateProbe:
        if len(hidden_states) != len(target_entropies) or not target_entropies:
            raise ValueError("Provide one target entropy for each hidden state")
        probe = HiddenStateProbe(input_dim=self.input_dim)
        probe.mean_target = sum(float(value) for value in target_entropies) / len(target_entropies)
        probe.is_trained = True
        return probe


class ProbeEvaluator:
    """Report simple prediction error against labeled examples."""

    @staticmethod
    def evaluate(predicted_entropies: List[float], actual_entropies: List[float]) -> Dict[str, float]:
        if not predicted_entropies or not actual_entropies:
            return {"rmse": 0.0, "mae": 0.0}
        if len(predicted_entropies) != len(actual_entropies):
            raise ValueError("Predicted and actual entropy lists must have the same length")
        errors = [float(pred) - float(actual) for pred, actual in zip(predicted_entropies, actual_entropies)]
        mae = sum(abs(error) for error in errors) / len(errors)
        rmse = (sum(error * error for error in errors) / len(errors)) ** 0.5
        return {"rmse": rmse, "mae": mae}
