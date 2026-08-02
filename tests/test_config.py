"""Tests for configuration loading."""

from pathlib import Path
from veritas_evalengine.core.config import load_eval_suite


def test_load_eval_suite(tmp_path: Path):
    suite_file = tmp_path / "test_suite.yaml"
    suite_file.write_text("""
name: temp_suite
description: Temporary test suite
version: "1.0"
tasks:
  - task_id: task-01
    task_type: rag
    prompt: Sample prompt
""")

    suite = load_eval_suite(suite_file)
    assert suite.name == "temp_suite"
    assert len(suite.tasks) == 1
    assert suite.tasks[0].task_id == "task-01"
