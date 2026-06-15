"""sunbot.core.llm — interface: role-segregated typing.Protocol contracts,
data models, and config. Depends only on std; no external SDK.
See docs/final-proposal.md (Phần B).
"""

from ._interface import (
    StructuredOutputGeneration,
    TextGeneration,
    TextStreaming,
)
from .output import RunOutput, StreamOutput

__all__ = [
    "RunOutput",
    "StreamOutput",
    "StructuredOutputGeneration",
    "TextGeneration",
    "TextStreaming",
]
