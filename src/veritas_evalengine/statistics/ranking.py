"""Bradley-Terry model fitting and ranking algorithms."""

from __future__ import annotations

from typing import List, Tuple
import numpy as np
from veritas_evalengine.scorers.judge import BradleyTerryRanker


class BradleyTerryModel:
    """Model wrapper for Bradley-Terry ranking."""

    def __init__(self, num_items: int):
        self.num_items = num_items
        self.scores = np.ones(num_items)

    def fit(self, comparisons: List[Tuple[int, int]]) -> np.ndarray:
        self.scores = BradleyTerryRanker.fit(self.num_items, comparisons)
        return self.scores


def bt_rank(num_items: int, comparisons: List[Tuple[int, int]]) -> List[float]:
    """Returns fitted Bradley-Terry latent strength parameters."""
    model = BradleyTerryModel(num_items)
    scores = model.fit(comparisons)
    return [float(s) for s in scores]
