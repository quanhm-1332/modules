from abc import abstractmethod
from typing import Protocol


class CacheRead(Protocol):
    @abstractmethod
    async def get(self, key: str) -> bytes: ...
