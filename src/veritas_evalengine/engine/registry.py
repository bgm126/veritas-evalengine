"""Registry for Scorers and AgentAdapters with plugin discovery."""

from __future__ import annotations

import importlib.metadata
from typing import Any, Type
from veritas_evalengine.core.protocols import AgentAdapter, Scorer


class ScorerRegistry:
    _registry: dict[str, Any] = {}

    @classmethod
    def register(cls, name: str, scorer_cls_or_inst: Any) -> None:
        cls._registry[name] = scorer_cls_or_inst

    @classmethod
    def get(cls, name: str, **kwargs: Any) -> Scorer:
        cls.discover_plugins()
        if name not in cls._registry:
            raise KeyError(f"Scorer '{name}' is not registered. Available: {list(cls._registry.keys())}")
        target = cls._registry[name]
        if isinstance(target, type):
            return target(**kwargs)
        return target

    @classmethod
    def discover_plugins(cls) -> None:
        try:
            eps = importlib.metadata.entry_points(group="veritas_evalengine.scorers")
            for ep in eps:
                if ep.name not in cls._registry:
                    try:
                        cls._registry[ep.name] = ep.load()
                    except Exception:
                        pass
        except Exception:
            pass

    @classmethod
    def list_available(cls) -> list[str]:
        cls.discover_plugins()
        return list(cls._registry.keys())


class AdapterRegistry:
    _registry: dict[str, Any] = {}

    @classmethod
    def register(cls, name: str, adapter_cls_or_inst: Any) -> None:
        cls._registry[name] = adapter_cls_or_inst

    @classmethod
    def get(cls, name: str, **kwargs: Any) -> AgentAdapter:
        cls.discover_plugins()
        if name not in cls._registry:
            raise KeyError(f"Adapter '{name}' is not registered. Available: {list(cls._registry.keys())}")
        target = cls._registry[name]
        if isinstance(target, type):
            return target(**kwargs)
        return target

    @classmethod
    def discover_plugins(cls) -> None:
        try:
            eps = importlib.metadata.entry_points(group="veritas_evalengine.adapters")
            for ep in eps:
                if ep.name not in cls._registry:
                    try:
                        cls._registry[ep.name] = ep.load()
                    except Exception:
                        pass
        except Exception:
            pass

    @classmethod
    def list_available(cls) -> list[str]:
        cls.discover_plugins()
        return list(cls._registry.keys())
