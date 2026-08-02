"""Tests for drift detector scorer."""

import json
from pathlib import Path
from veritas_evalengine.core.schemas import AgentRun, EvalTask
from veritas_evalengine.scorers.drift import CUSUMDetector, DriftScorer, EWMADetector, PSIDetector


def test_psi_detector():
    ref = [1.0, 1.0, 1.0, 1.0, 1.0]
    curr = [1.0, 1.0, 1.0, 1.0, 1.0]
    psi = PSIDetector.calculate(ref, curr)
    assert psi < 0.05


def test_cusum_detector(tmp_path: Path):
    golden_file = Path("tests/scorers/golden/drift_cusum_alert.json")
    if golden_file.exists():
        data = json.loads(golden_file.read_text())
        alarm, _ = CUSUMDetector.detect(data["series"])
        assert alarm == data["expected_alarm"]


def test_drift_scorer(sample_task: EvalTask, sample_run: AgentRun):
    scorer = DriftScorer()
    res = scorer.score(sample_task, sample_run)
    assert res.scorer_name == "drift"
    assert "ewma" in res.metrics
