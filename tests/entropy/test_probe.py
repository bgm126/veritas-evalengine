"""Tests for hidden state semantic entropy probe."""

import numpy as np
from veritas_evalengine.entropy.probe import HiddenStateProbe, ProbeEvaluator, ProbeTrainer


def test_probe_training_and_eval():
    np.random.seed(42)
    dim = 16
    X = [np.random.randn(dim) for _ in range(20)]
    y = [0.1 if np.mean(x) < 0 else 0.9 for x in X]

    trainer = ProbeTrainer(input_dim=dim)
    probe = trainer.train(X, y)

    preds = [probe.predict(x) for x in X]
    eval_res = ProbeEvaluator.evaluate(preds, y)

    assert eval_res["rmse"] >= 0.0
    assert eval_res["auroc"] >= 0.5
