from abc import abstractmethod
from collections.abc import AsyncIterator
from typing import Protocol, runtime_checkable

from . import output as _o


@runtime_checkable
class TextGeneration(Protocol):
    @abstractmethod
    async def generate_text(
        self, user_prompt: str, *, system_prompt: str | None = None
    ) -> _o.RunOutput[str]: ...


@runtime_checkable
class TextStreaming(Protocol):
    @abstractmethod
    def stream_text(
        self, user_prompt: str, *, system_prompt: str | None = None
    ) -> AsyncIterator[_o.StreamOutput]: ...


@runtime_checkable
class StructuredOutputGeneration[OutputDataT](Protocol):
    @abstractmethod
    async def generate_output(
        self,
        user_prompt: str,
        output_type: type[OutputDataT],
        *,
        system_prompt: str | None = None,
    ) -> _o.RunOutput[OutputDataT]: ...
