from abc import abstractmethod
from typing import Protocol


class Resource[T](Protocol):
    @abstractmethod
    async def initialize(self) -> None: ...

    @abstractmethod
    async def get(self) -> T: ...

    @abstractmethod
    async def cleanup(self) -> None: ...
