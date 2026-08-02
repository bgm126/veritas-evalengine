"""Agent adapters module."""

from .generic import GenericAgentAdapter
from .otel import OTelAdapter
from .reference import (
    ReferenceCodingAdapter,
    ReferenceMultiAgentAdapter,
    ReferenceRAGAdapter,
    ReferenceToolAdapter,
)

__all__ = [
    "GenericAgentAdapter",
    "OTelAdapter",
    "ReferenceCodingAdapter",
    "ReferenceMultiAgentAdapter",
    "ReferenceRAGAdapter",
    "ReferenceToolAdapter",
]
