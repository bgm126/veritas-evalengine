"""Tests for scorer and adapter registry."""

from veritas_evalengine.adapters.reference import ReferenceRAGAdapter
from veritas_evalengine.engine.registry import AdapterRegistry, ScorerRegistry


def test_adapter_registry():
    AdapterRegistry.register("mock_rag", ReferenceRAGAdapter)
    adapter = AdapterRegistry.get("mock_rag")
    assert isinstance(adapter, ReferenceRAGAdapter)
