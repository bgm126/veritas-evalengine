"""Tests for stochastic sampling."""

from veritas_evalengine.entropy.sampling import StochasticSampler


def test_stochastic_sampler():
    sampler = StochasticSampler(num_samples=3)
    samples = sampler.sample("What is the capital of France?")
    assert len(samples) == 3
    assert samples[0].temperature == 0.7
