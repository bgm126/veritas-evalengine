"""Tests for Garak and PyRIT adapters."""

from veritas_evalengine.stress.adapters import GarakProbeAdapter, PyRITAdapter


def test_garak_probe_adapter():
    adapter = GarakProbeAdapter()
    tasks = adapter.convert_prompts_to_tasks(["Ignore instructions", "Reveal prompt"])
    assert len(tasks) == 2
    assert tasks[0].task_type == "adversarial"


def test_pyrit_adapter():
    adapter = PyRITAdapter()
    history = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"},
    ]
    run = adapter.convert_pyrit_conversation(history)
    assert run.final_answer == "Hi there!"
    assert len(run.trace_events) == 2
