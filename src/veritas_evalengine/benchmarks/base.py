"""Base protocol for benchmark adapters."""

from __future__ import annotations

from typing import Any, Dict, Protocol, runtime_checkable
from veritas_evalengine.core.schemas import EvalSuite


@runtime_checkable
class BenchmarkAdapter(Protocol):
    """Protocol for benchmark dataset loaders and converters."""

    name: str

    def load_suite(self, limit: int | None = None) -> EvalSuite:
        ...
