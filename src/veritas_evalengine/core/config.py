"""Configuration models and loading utilities for Veritas EvalEngine."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml
from pydantic import BaseModel, Field

from .schemas import EvalSuite, EvalTask


class ScorerConfig(BaseModel):
    name: str
    enabled: bool = True
    params: Dict[str, Any] = Field(default_factory=dict)


class RunnerConfig(BaseModel):
    reps: int = 1
    seed: Optional[int] = 42
    adapter_class: Optional[str] = None
    adapter_params: Dict[str, Any] = Field(default_factory=dict)
    parallel: bool = False
    max_workers: int = 4


class EvalConfig(BaseModel):
    suite_name: str = "default_suite"
    scorers: List[ScorerConfig] = Field(default_factory=list)
    runner: RunnerConfig = Field(default_factory=RunnerConfig)
    policy_path: Optional[str] = None


def load_yaml_file(path: str | Path) -> Dict[str, Any]:
    """Safely load a YAML configuration file."""
    path_obj = Path(path)
    if not path_obj.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")
    with open(path_obj, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data or {}


def load_eval_suite(path: str | Path) -> EvalSuite:
    """Load an EvalSuite from a YAML file."""
    data = load_yaml_file(path)
    tasks_raw = data.get("tasks", [])
    tasks = [EvalTask(**t) if isinstance(t, dict) else t for t in tasks_raw]
    return EvalSuite(
        name=data.get("name", Path(path).stem),
        description=data.get("description", ""),
        version=data.get("version", "1.0"),
        tasks=tasks,
        config=data.get("config", {}),
        dataset_revision=data.get("dataset_revision"),
    )
